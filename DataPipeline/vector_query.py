import pandas as pd
import numpy as np
import os
import json
import re
import time
import faiss
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder

PATH_TO_EMBEDS = "compressed_array.npz"
PATH_TO_DF = "quick_lookup.csv"

class ArxivSearch:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = np.load(PATH_TO_EMBEDS)
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
            id = self.df_data.iloc[idx].id
            if len(id.split(".")[0]) == 3:
                id = "0" + id
            pred_list.append(id)
        return pred_list
    
    def run_arxiv_search(self, query_text, num_results_to_print, top_k=300):
        pred_index_list, scores = self.run_faiss_search(query_text, top_k)
        # This returns a list of dicts with length equal to top_k
        pred_list = self.match_idx_to_id(pred_index_list)
        return pred_list[:num_results_to_print], scores
    
    def run_query(self, query_text, num_results_to_print):
        timer = time.time()
        num_results_to_print = 20
        ids, scores = self.run_arxiv_search(query_text, num_results_to_print)
        print("Results:")
        for id in ids:
            # print arxiv link to the paper
            print(f"    https://arxiv.org/abs/{id}")
        print("Time elapsed:", time.time() - timer)
        
        # you can return anything you like
        # return ids, scores



if __name__ == "__main__":
    # this step load takes a while, but only needs to be done once
    searcher = ArxivSearch()
    # quick 0.2s query on my machine
    searcher.run_query("machine learning", 20)
    searcher.run_query("natural language processing", 20)
    searcher.run_query("deep learning", 30)
    # long text query
    searcher.run_query("This paper presents a new approach to solve the problem of machine learning, while it's old", 20)