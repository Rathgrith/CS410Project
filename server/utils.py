import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
import re
import json
from collections import defaultdict, Counter
import math
import pickle
from tqdm import tqdm
import os
N_PAPERS = 2440876


# Inverse Document Frequency (IDF) calculation
def idf(N, df):
    return math.log((N - df + 0.5) / (df + 0.5) + 1)

# Calculate BM25 score for a single document and field
def bm25_score(doc_id, query_terms, field, N, inverted_index, doc_length, avg_doc_length, k1=1.5, b=0.75):
    score = 0.0
    for term in query_terms:
        if term in inverted_index[field]:
            df = len(inverted_index[field][term])
            term_freq = inverted_index[field][term].get(doc_id, 0)
            doc_len = doc_length.get(doc_id, 0)
            term_score = idf(N, df) * ((term_freq * (k1 + 1)) / (term_freq + k1 * (1 - b + b * (doc_len / avg_doc_length))))
            score += term_score
    return score

# Perform a query across multiple fields with weighted BM25
def weighted_bm25_query(query_terms, inverted_indexes, doc_lengths, field_weights):
    N = max(len(doc_lengths[field]) for field in field_weights)
    scores = {}
    avg_doc_lengths = {field: sum(doc_lengths[field].values()) / len(doc_lengths[field]) for field in field_weights}
    for field in field_weights:
        for doc_id in doc_lengths[field]:
            field_score = bm25_score(doc_id, query_terms, field, N, inverted_indexes, doc_lengths[field], avg_doc_lengths[field])
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += field_score * field_weights[field]
    
    # Sort documents by their score
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_scores

def load_existing_data(field):
    """Load existing inverted index and document lengths if they exist."""
    inverted_index = defaultdict(dict)
    doc_lengths = {}
    try:
        with open(f'{field}_inverted_index.pkl', 'rb') as f:
            inverted_index = pickle.load(f)
        with open(f'{field}_doc_lengths.pkl', 'rb') as f:
            doc_lengths = pickle.load(f)
        print(f"Loaded existing data for {field}.")
    except (EOFError, FileNotFoundError):
        print(f"No existing data found for {field}, starting from scratch.")
    return inverted_index, doc_lengths

def save_data(field, inverted_index, doc_lengths):
    """Save inverted index and document lengths to disk."""
    with open(f'{field}_inverted_index.pkl', 'wb') as f:
        pickle.dump(dict(inverted_index), f)
    with open(f'{field}_doc_lengths.pkl', 'wb') as f:
        pickle.dump(doc_lengths, f)
    print(f"Saved data for {field}.")

def build_indexes(metadata_path, fields=['title', 'abstract', 'authors'], limit=100000, save_interval=10000):
    processed_count = {field: 0 for field in fields}
    for field in fields:
        inverted_index, doc_lengths = load_existing_data(field)
        
        with open(metadata_path, 'r') as f:
            for line in tqdm(f, desc=f"Building indexes for {field}", unit=" papers"):
                paper = json.loads(line)
                doc_id = paper['id']
                
                if doc_id in doc_lengths:
                    continue  # Skip already processed documents
                
                text = preprocess(paper.get(field, ""))
                term_freq = Counter(text.split())
                
                for term, freq in term_freq.items():
                    inverted_index[term][doc_id] = freq
                
                doc_lengths[doc_id] = sum(term_freq.values())
                processed_count[field] += 1
                
                if processed_count[field] % save_interval == 0:
                    save_data(field, inverted_index, doc_lengths)
                
                if processed_count[field] >= limit:
                    break

        save_data(field, inverted_index, doc_lengths)

def load_data(pkl_direcory='DataPipeline/', fields = ['title', 'abstract']):
    inverted_indexes = {}
    doc_lengths = {}
    
    for field in fields:
        inverted_index_path = os.path.join(pkl_direcory, f'{field}_inverted_index.pkl')
        doc_lengths_path = os.path.join(pkl_direcory, f'{field}_doc_lengths.pkl')
        with open(inverted_index_path, 'rb') as f:
            inverted_indexes[field] = pickle.load(f)
        with open(doc_lengths_path, 'rb') as f:
            doc_lengths[field] = pickle.load(f)
    
    return inverted_indexes, doc_lengths


import pandas as pd
import numpy as np
import os
import json
import re
import time
import faiss
from sentence_transformers import SentenceTransformer
import networkx as nx

PATH_TO_EMBEDS = "./db/compressed_array.npz"
PATH_TO_DF = "./db/quick_lookup.csv"

class ArxivSearch:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = np.load(PATH_TO_EMBEDS)
        if PATH_TO_DF.endswith(".csv"):
            self.df_data = pd.read_csv(PATH_TO_DF, dtype={'id': str})
        self.embeddings = self.embeddings['array_data']
        self.embed_length = self.embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(self.embed_length)
        self.faiss_index.add(self.embeddings)

    def run_faiss_search(self, query_text, top_k):
        query = [query_text]
        query_embedding = self.model.encode(query)
        scores, index_vals = self.faiss_index.search(query_embedding, top_k)
        index_vals_list = index_vals[0]
        return index_vals_list, scores
    
    def match_idx_to_id(self, index_vals_list):
        pred_list = []
        
        for idx in index_vals_list:
            id = self.df_data.iloc[idx]['id']
            author = self.df_data.iloc[idx]['authors']
            if len(id.split(".")[0]) == 3:
                id = "0" + id
            pred_list.append({"id": id, "authors": author})
        return pred_list
    
    def run_arxiv_search(self, query_text, num_results_to_print, top_k=300):
        pred_index_list, scores = self.run_faiss_search(query_text, top_k)
        # This returns a list of dicts with length equal to top_k
        pred_list = self.match_idx_to_id(pred_index_list)
        return pred_list[:num_results_to_print], scores
    
    def run_query(self, query_text, num_results_to_print):
        timer = time.time()
        preds, scores = self.run_arxiv_search(query_text, num_results_to_print)
        print("Results:")
        for pred in preds:
            # print arxiv link based on id
            print(f"https://arxiv.org/abs/{pred['id']}")
        print("Time taken:", time.time() - timer)
        return preds, scores
        

def compute_coauthor_graph(pred_list):
    coauthor_graph = {}
    for pred in pred_list:
        authors = pred['authors'].split(", ")
        for author in authors:
            if author not in coauthor_graph:
                coauthor_graph[author] = set()
        for author in authors:
            for coauthor in authors:
                if author != coauthor:
                    coauthor_graph[author].add(coauthor)
    # # visualize the graph
    # G = nx.Graph()
    # for author, coauthors in coauthor_graph.items():
    #     for coauthor in coauthors:
    #         G.add_edge(author, coauthor)
    # # draw the graph
    # nx.draw(G, with_labels=True, font_size=1, node_size=20, font_color='black')
    return coauthor_graph


def hits_reranking(coauthor_graph, pred_list, top_k=10):
    # TODO: setup hyperparameters for hits reranking
    # rerank the papers based on hits
    hits = {}
    for author, coauthors in coauthor_graph.items():
        for coauthor in coauthors:
            if coauthor not in hits:
                hits[coauthor] = 0
            hits[coauthor] += 1
    # rerank the papers based on hits
    for pred in pred_list:
        authors = pred['authors'].split(", ")
        score = 0
        for author in authors:
            if author in hits:
                score += hits[author]
        pred['score'] = score
    pred_list = sorted(pred_list, key=lambda x: x['score'], reverse=True)
    return pred_list[:top_k]
