from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from urllib.parse import unquote
from db.utils import preprocess
from db.db_queries import query, get_all_paper_titles, get_all_matching_paper_titles, get_preprocessed_papers_by_title

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Frontend URL
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/papers")
def get_papers(paper_query=None):
    if paper_query:
        # Decode URL-encoded string
        paper_query = unquote(paper_query)
        results = [row[0] for row in query(lambda x: get_all_matching_paper_titles(x, paper_query))]
    else:
        results = [row[0] for row in query(get_all_paper_titles)]
    return results

class QueryItems(BaseModel):
    keywords: str
    selected_papers: List[str]

@app.post("/query")
def make_query(query_items: QueryItems):
    # Parse query
    query_keywords = preprocess(query_items.keywords)
    # Parse added documents (if any)
    selected_papers = [{
        "title": row[0],
        "authors": row[1],
        "abstract": row[2],
    } for row in query(lambda x: get_preprocessed_papers_by_title(x, query_items.selected_papers))]
    # Apply preprocessing
    return {"keywords": query_keywords, "selected_papers": selected_papers}

    # return {"documents": [
    #     {
    #         "title": f"Title {i}",
    #         "authors": f"Author {i}",
    #         "abstract": f"Abstract {i}",
    #         "link": f"arxiv.com/{i}",
    #     }
    #     for i in range(3)
    # ]}

if __name__ == "__main__":
    import uvicorn
    # Run `uvicorn main:app - reload` to start backend
    uvicorn.run(app, host="0.0.0.0", port=8000)