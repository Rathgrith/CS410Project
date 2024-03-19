import pickle
import math
import os
from utils import preprocess, weighted_bm25_query
# Function to load the precomputed inverted indexes and document lengths
def load_data(pkl_direcory='DataPipeline/', fields = ['title', 'abstract', 'authors']):
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


# load the precomputed inverted indexes (term frequency for each fields) and document lengths indexes
# note that they are using full vocabulary, but easy to truncate to a subset of the vocabulary
# you are free to change the directory to where you saved the pkl files
# generating the inverted indexes and document lengths for the 3 given fields is time-consuming (70 minutes on my machine)
# may use the precomputed files I provided
inverted_indexes, doc_lengths = load_data('./100000_subset', fields=['title', 'abstract', 'authors'])
# config weights for each field, feel free to tweak
field_weights = {'title': 0.3, 'abstract': 0.4, 'authors': 0.3}
# preprocessed query terms
query_terms = preprocess("machine learning").split()
sorted_scores = weighted_bm25_query(query_terms, inverted_indexes, doc_lengths, field_weights)
print(sorted_scores[:10]) 
# example output:
# doc_id, score kv pairs
# [('0803.2976', 13.753191141017297), 
    # ('0802.1412', 12.076985365917412), 
    # ('0810.4752', 9.69622971763437), 
    # ('0805.2891', 9.10511868134971), 
    # ('0810.2434', 9.040174100661277), 
    # ('0712.4126', 8.671609264911448), 
    # ('0710.5896', 8.233968171906657), 
    # ('0708.1564', 8.114775559646187), 
    # ('0704.3905', 8.07680456701551), 
    # ('0709.2760', 7.903793683383984)]   
# the first paper has the highest score, and so on
# the score is the BM25F score of the document
# the doc_id is the identifier of the document
# you can use the doc_id to retrieve the full paper from the database  
