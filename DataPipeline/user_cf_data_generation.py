import os
import json
from vector_query import ArxivSearch

GEN_DOCS_PER_USER = True #not os.path.exists("docs_per_user.json")
if GEN_DOCS_PER_USER:
    if not os.path.exists("user_sessions.json"):
        import sqlite3
        from sqlite3 import Error
        import traceback

        DB_PATH = r"../server/db/database.db"

        def query(fn):
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
                return fn(conn)
            except Error as e:
                print(traceback.format_exc())
            finally:
                if conn:
                    conn.close()


        def get_n_random_rows(conn, n=100):
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM papers WHERE id IN (SELECT id FROM papers ORDER BY RANDOM() LIMIT {n})")
            return [(row[1], row[3]) for row in cur.fetchall()]

        N_ROWS = 1000

        papers_set = query(lambda x: get_n_random_rows(x, N_ROWS))

        from transformers import AutoModelForCausalLM
        from transformers import AutoTokenizer
        import re

        model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-2-7b-hf", device_map="auto", load_in_4bit=True
        )

        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf", padding_side="left")
        tokenizer.pad_token = tokenizer.eos_token  # Most LLMs don't have a pad token by default
        from transformers import TextStreamer
        streamer = TextStreamer(tokenizer)

        user_sessions = []
        for paper in papers_set:
            title, abstract = paper
            prompt = f"TITLE: {title}\nABSTRACT: {abstract}\nQUESTIONS:\n- "
            generated_ids = model.generate(**tokenizer([prompt], return_tensors="pt").to("cuda"),  streamer=streamer, do_sample=True, max_new_tokens=1000)
            output = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            # Generate questions based on paper
            user_sessions.append([q.strip() for q in re.findall(r"\n-\s*([^\n-]*)", output) if len(q.strip()) > 0])

        with open('user_sessions.json', 'w') as f:
            json.dump(user_sessions, f)

    print("Generate docs_per_user")
    from random import randrange
    user_sessions = json.load(open("user_sessions.json"))
    searcher = ArxivSearch()
    docs_per_user = []
    if os.path.exists("docs_per_user.json"):
        docs_per_user = json.load(open('docs_per_user.json'))
    for i, user_session in enumerate(user_sessions):
        if i <= len(docs_per_user)-1:
            continue
        print(i, len(user_sessions), (i / len(user_sessions)) * 100)
        docs = []
        for query in user_session:
            doc_count = randrange(10, 80)
            print(doc_count, query)
            ids, _ = searcher.run_query(query, doc_count)
            docs.extend([id["id"] for id in ids])
        docs_per_user.append(list(set(docs)))
        with open('docs_per_user.json', 'w') as f:
            json.dump(docs_per_user, f)

print("Generate NN model")
import numpy as np
import pickle
from sklearn.neighbors import NearestNeighbors
docs_per_user = json.load(open('docs_per_user.json'))
all_papers = []
for docs in docs_per_user:
    all_papers.extend(docs)
all_papers = list(set(all_papers))
matrix = np.zeros((len(docs_per_user), len(all_papers)))
for i, docs in enumerate(docs_per_user):
    for doc in docs:
        doc_idx = all_papers.index(doc)
        matrix[i][doc_idx] = 1
model = NearestNeighbors(metric="cosine", n_neighbors=21, algorithm='brute')
model.fit(matrix)

def normalize(lst):
    lst = np.array(lst)
    total = np.sum(lst)
    if not total:
        total = 1
    return (lst / total).tolist()

normalized_user_ratings = [normalize([user.count(paper) for paper in all_papers]) for user in docs_per_user]

print("Save NN model")
# save similarity model
with open('nn_model.pkl','wb') as f:
    pickle.dump(model,f)
with open('all_papers_order.json', 'w') as f:
    json.dump(all_papers, f)
with open('normalized_user_ratings.json', 'w') as f:
    json.dump(normalized_user_ratings, f)

    