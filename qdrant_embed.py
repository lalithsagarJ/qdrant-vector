# qdrant_embed.py
import os
import uuid
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

VECTOR_DIM = 384
COLLECTION_NAME = "my_vectors"
DATA_DIR = Path("data/")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
model = SentenceTransformer("all-MiniLM-L6-v2")

def create_or_reset_collection():
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
    )

def load_documents():
    docs = []
    for file in DATA_DIR.glob("*.txt"):
        content = file.read_text(encoding="utf-8")
        docs.append({"title": file.name, "text": content})
    return docs

def embed_and_push():
    documents = load_documents()
    points = []
    for doc in documents:
        vector = model.encode(doc["text"]).tolist()
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"title": doc["title"], "text": doc["text"]}
        ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Upserted {len(points)} documents into Qdrant.")

if __name__ == "__main__":
    create_or_reset_collection()
    embed_and_push()

