# qdrant_api.py
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "my_vectors"

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class SearchResponse(BaseModel):
    title: str
    text: str
    score: float

@app.post("/search", response_model=List[SearchResponse])
def search_vectors(req: SearchRequest):
    vector = model.encode(req.query).tolist()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=req.top_k
    )
    return [
        SearchResponse(
            title=hit.payload["title"],
            text=hit.payload["text"],
            score=hit.score
        )
        for hit in results
    ]

@app.get("/")
def root():
    return {"message": "Qdrant Vector Search API is online 🧠"}

