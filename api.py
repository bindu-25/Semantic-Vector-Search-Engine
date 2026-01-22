# api.py
"""
FastAPI wrapper around the semantic search engine.
"""

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from semantic_search_engine import SemanticSearchEngine

engine = SemanticSearchEngine()
API_KEY = "change_this"

app = FastAPI()


class Query(BaseModel):
    query: str
    top_k: int = 5


@app.post("/search")
def search(q: Query, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return engine.search(q.query, q.top_k)
