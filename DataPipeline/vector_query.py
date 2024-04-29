import pandas as pd
import numpy as np
import os
import json
import re
import time
# import matplotlib.pyplot as plt
import faiss
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
import networkx as nx
# import matplotlib
# matplotlib.use('Agg')
PATH_TO_EMBEDS = "../server/db/compressed_array.npz"
PATH_TO_DF = "../server/db/quick_lookup.csv"
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
        return index_vals_list, scores[0]
    
    def match_idx_to_id(self, index_vals_list, scores):
        pred_list = []
        updated_scores = []
        
        for score, idx in zip(scores, index_vals_list):
            if idx < self.df_data.shape[0]:
                id = self.df_data.iloc[idx]['id']
                author = self.df_data.iloc[idx]['authors']
                if len(id.split(".")[0]) == 3:
                    id = "0" + id
                pred_list.append({"id": id, "authors": author})
                updated_scores.append(score)
        return pred_list, np.array(updated_scores)
    
    def run_arxiv_search(self, query_text, num_results_to_print, top_k=300):
        pred_index_list, scores = self.run_faiss_search(query_text, top_k)
        # This returns a list of dicts with length equal to top_k
        pred_list, scores = self.match_idx_to_id(pred_index_list, scores)
        return pred_list[:num_results_to_print], scores
    
    def run_query(self, query_text, num_results_to_print):
        timer = time.time()
        preds, scores = self.run_arxiv_search(query_text, num_results_to_print)
        # print("Results:")
        # for pred in preds:
        #     # print arxiv link based on id
        #     print(f"https://arxiv.org/abs/{pred['id']}")
        # print("Time taken:", time.time() - timer)
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
    # plt.savefig("coauthor_graph.png")
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


if __name__ == "__main__":
    # this step load takes a while, but only needs to be done once
    searcher = ArxivSearch()
    # quick 0.2s query on my machine
    ids, scores = searcher.run_query("machine learning", 500)
    # searcher.run_query("natural language processing", 20)
    # searcher.run_query("deep learning", 30)
    # # long text query
    # searcher.run_query("This paper presents a new approach to solve the problem of machine learning, while it's old", 500)
    # this computes the coauthor graph within the subset of retrieved papers
    coauthor_graph = compute_coauthor_graph(ids)
    # This is for a basic hits reraanking
    reranked_ids = hits_reranking(coauthor_graph, ids)
    print("HITS Reranked:")
    for pred in reranked_ids:
        print(f"https://arxiv.org/abs/{pred['id']}")