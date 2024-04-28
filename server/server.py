from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated, List
import json
from urllib.parse import unquote
from db.utils import preprocess
from db.db_queries import create_session, create_session_history, get_history_for_session, get_paper_by_id, query, get_all_paper_titles, get_all_matching_paper_titles, get_preprocessed_papers_by_title, get_all_sessions
from utils import ArxivSearch, compute_coauthor_graph, hits_reranking, load_data, weighted_bm25_query

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
def get_papers(paper_query=None):
    if paper_query:
        # Decode URL-encoded string
        paper_query = unquote(paper_query)
        results = [row[0] for row in query(lambda x: get_all_matching_paper_titles(x, paper_query))]
    else:
        results = [row[0] for row in query(get_all_paper_titles)]
    return results

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

@app.get("/query")
def make_query(session_id: Annotated[int | None, Query()] = None, keywords: Annotated[str, Query()] = "", selected_papers: Annotated[list[str], Query()] = []):
    print(session_id, keywords, selected_papers)
    if len(selected_papers) == 0 and len(keywords) == 0:
        return []
    if session_id is None:
        session_id = query(lambda x: create_session(x))
    else:
        session_id = int(session_id)
    full_query = []

    # Parse query
    query_keywords = preprocess(keywords)

    # Parse added documents (if any)
    full_query.extend(query_keywords)
    for row in query(lambda x: get_preprocessed_papers_by_title(x, selected_papers)):
        title = row[0]
        authors = row[1]
        abstract = row[2]
        full_query.extend(preprocess(title).split())
        full_query.extend(preprocess(abstract).split())
        full_query.extend(preprocess(authors).split())
    
    top_k = 500
    ids, scores = searcher.run_query(" ".join(full_query), top_k)
    coauthor_graph = compute_coauthor_graph(ids)
    reranked_ids = hits_reranking(coauthor_graph, ids, top_k)
    
    relevant_docs = []
    for doc_struct in reranked_ids:
        doc = query(lambda x: get_paper_by_id(x, doc_struct["id"]))
        if len(doc) == 1:
            doc = doc[0]
            title = doc[1]
            authors = doc[2]
            abstract = doc[3]
            relevant_docs.append({
                "score": doc_struct["score"],
                "link":f"https://arxiv.org/abs/{doc_struct['id']}",
                "title": title,
                "authors": authors,
                "abstract": abstract,
            })
    query(lambda x: create_session_history(x, session_id, keywords, selected_papers))
    return { "docs": relevant_docs, "session_id": str(session_id) }


if __name__ == "__main__":
    import uvicorn
    # Run `uvicorn main:app - reload` to start backend
    uvicorn.run(app, host="0.0.0.0", port=8000)