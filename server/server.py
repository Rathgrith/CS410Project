from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated, List
import json
from urllib.parse import unquote
from db.utils import preprocess
from db.db_queries import delete_session_all, delete_history_for_session, create_interaction, create_session, create_session_history, get_all_papers, get_history_for_session, get_interactions, get_paper_by_id, get_papers_by_id, get_papers_by_title, query, get_all_paper_titles, get_all_matching_paper_titles, get_preprocessed_papers_by_title, get_all_sessions
from utils import ArxivSearch, compute_coauthor_graph, hits_reranking, load_data, recommend, weighted_bm25_query


searcher = ArxivSearch()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Frontend URL
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

inverted_indexes, doc_lengths = load_data('./db/inverted_index', fields=['title', 'abstract'])

@app.get("/papers")
def get_papers(paper_query: Annotated[str, Query()] = ""):
    if paper_query:
        # Decode URL-encoded string
        paper_query = unquote(paper_query)
        results = [row[0] for row in query(lambda x: get_all_matching_paper_titles(x, paper_query))]
    else:
        results = [row[0] for row in query(get_all_paper_titles)]
    return results

@app.get("/papers/recommend")
def get_paper_recommendation(session_id: Annotated[int | None, Query()] = -1):
    session_id = int(session_id)
    if not session_id or session_id == -1:
        # Return recommendation based on all sessions
        history = query(lambda x: get_interactions(x))
    else:
        # Return recommendation based on session history
        history = query(lambda x: get_interactions(x, session_id))
    relevant_paper_ids = recommend(history)
    print("Recommended paper IDs", relevant_paper_ids)
    return [{
        "id":row[0],
        "link":f"https://arxiv.org/abs/{row[0]}",
        "title":row[1],
        "authors":row[2],
        "abstract":row[3]
    } for row in query(lambda x: get_papers_by_id(x, relevant_paper_ids))]

@app.get("/sessions")
def get_sessions():
    return [str(row[0]) for row in query(get_all_sessions)]

class QueryItems(BaseModel):
    keywords: str
    selected_papers: List[str]

@app.get("/session/{session_id}")
def get_session_history(session_id):
    return [{
        "id": row[0],
        "timestamp": row[2],
        "query": json.loads(row[3]),
    } for row in query(lambda x: get_history_for_session(x, session_id))]

@app.get("/delete_session/{session_id}")
def delete_session(session_id):
    query(lambda x: delete_session_all(x, session_id))

@app.get("/delete_session_history/{session_id}/{id}")
def delete_session_history(session_id, id):
    query(lambda x: delete_history_for_session(x, session_id, id))
    return get_session_history(session_id)

@app.get("/session/{session_id}/select/{paper_id}")
def make_interaction(session_id, paper_id):
    assert session_id
    assert paper_id
    session_id = int(session_id)
    assert session_id > -1
    query(lambda x: create_interaction(x, session_id, paper_id))


@app.get("/query")
def make_query(session_id: Annotated[int | None, Query()] = None, keywords: Annotated[str, Query()] = "", selected_papers: Annotated[list[str], Query()] = [], faiss_weight: Annotated[float, Query()] = 1.0, hits_weight: Annotated[float, Query()] = 1.0):
    raw_faiss_weight = faiss_weight
    raw_hits_weight = hits_weight
    # Normalize weights
    total_weight = faiss_weight + hits_weight
    faiss_weight /= total_weight 
    hits_weight /= total_weight 

    print(session_id, keywords, selected_papers, faiss_weight, hits_weight)

    if len(selected_papers) == 0 and len(keywords) == 0:
        return []
    if session_id is None:
        session_id = query(lambda x: create_session(x))
    else:
        session_id = int(session_id)

    # Parse query
    query_keywords = keywords
    
    full_query = [query_keywords]

    # Parse added documents (if any)
    for row in query(lambda x: get_papers_by_title(x, selected_papers)):
        title = row[0]
        authors = row[1]
        abstract = row[2]
        full_query.extend(title.split())
        full_query.extend(abstract.split())
        full_query.extend(authors.split())
    
    top_k = 500
    ids, scores = searcher.run_query(" ".join(full_query), top_k)
    coauthor_graph = compute_coauthor_graph(ids)
    # FAISS scores is lower=better so we swap it so bigger=better.
    scores = max(scores) - scores
    reranked_ids = hits_reranking(coauthor_graph, ids, scores, faiss_weight, hits_weight, top_k)
    
    relevant_docs = []
    for doc_struct in reranked_ids:
        doc = query(lambda x: get_paper_by_id(x, doc_struct["id"]))
        if len(doc) == 1:
            doc = doc[0]
            title = doc[1]
            authors = doc[2]
            abstract = doc[3]
            relevant_docs.append({
                "id": doc_struct['id'],
                "score": doc_struct["score"],
                "link": f"https://arxiv.org/abs/{doc_struct['id']}",
                "title": title,
                "authors": authors,
                "abstract": abstract,
            })
    query(lambda x: create_session_history(x, session_id, keywords, selected_papers, raw_faiss_weight, raw_hits_weight))
    return { "docs": relevant_docs, "session_id": str(session_id) }


if __name__ == "__main__":
    import uvicorn
    # Run `uvicorn main:app - reload` to start backend
    uvicorn.run(app, host="0.0.0.0", port=8000)