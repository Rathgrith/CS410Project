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


def build_indexes(metadata_path, limit=100000, fields=['title', 'abstract', 'authors']):
    inverted_indexes = {field: defaultdict(dict) for field in fields}
    limit = min(N_PAPERS, limit)
    doc_lengths = {field: {} for field in fields}
    count = 0
    save_interval = 100000
    with open(metadata_path, 'r') as f:
        for line in tqdm(f, total=min(N_PAPERS, limit), desc="Building indexes", unit=" papers"):
            paper = json.loads(line)
            doc_id = paper['id']
            for field in fields:
                # Preprocess the content of each field
                text = preprocess(paper.get(field, ""))
                term_freq = Counter(text.split())
                # Update inverted index and document lengths
                for term, freq in term_freq.items():
                    if doc_id not in inverted_indexes[field][term]:
                        inverted_indexes[field][term][doc_id] = freq
                    else:
                        inverted_indexes[field][term][doc_id] += freq
                        
                doc_lengths[field][doc_id] = sum(term_freq.values())
            count += 1
            if count > limit:
                break
            if count % save_interval == 0 or count == limit:
                print(f"Processed {count} papers, saving indexes to disk...")
                # Save the indexes and lengths to disk
                for field in fields:
                    with open(f'{field}_inverted_index.pkl', 'wb') as f:
                        pickle.dump(dict(inverted_indexes[field]), f)
                    with open(f'{field}_doc_lengths.pkl', 'wb') as f:
                        pickle.dump(doc_lengths[field], f)
    print("Inverted indexes and document lengths have been saved.")

def preprocess(text):
    '''
    this function preprocesses the text
    '''
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    preprocessed_text = " ".join([stemmer.stem(word) for word in word_tokenize(text) if word and (word not in stop_words) and (word not in string.punctuation) and (not any(c.isdigit() for c in word))])
    return re.sub(r'[^\w\s]', '', string=preprocessed_text).lower()
