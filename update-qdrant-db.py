import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# =========================
# 🧠 Config
# =========================
COLLECTION_NAME = "my_vectors"
VECTOR_DIM = 384  # using MiniLM with 384 dimensions
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# =========================
# 🚀 Load Sentence Transformer (local embedding model)
# =========================
print("🧠 Loading local sentence transformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# 🔌 Connect to Qdrant
# =========================
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# =========================
# 📦 Create Collection if it doesn't exist
# =========================
if client.collection_exists(collection_name=COLLECTION_NAME):
    print(f"🧨 Deleting existing collection '{COLLECTION_NAME}'...")
    client.delete_collection(collection_name=COLLECTION_NAME)

print(f"📦 Creating new collection '{COLLECTION_NAME}' with {VECTOR_DIM} dimensions...")
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
)

# =========================
# 📝 Sample Documents
# =========================
documents = [
    {"text": "The quick brown fox jumps over the lazy dog.", "title": "Fox"},
    {"text": "A vector database is great for similarity search.", "title": "Vectors"},
    {"text": "Local embedding models work without internet or API keys.", "title": "Offline"},
]

# =========================
# 🔁 Embed + Prepare Points
# =========================
def get_embedding(text: str):
    return model.encode(text).tolist()

points = []
for doc in documents:
    try:
        vector = get_embedding(doc["text"])
        unique_id = str(uuid.uuid4())
        points.append(
            PointStruct(
                id=unique_id,
                vector=vector,
                payload={
                    "title": doc["title"],
                    "text": doc["text"]
                }
            )
        )
        print(f"🔗 Embedded & prepped doc: {doc['title']} (ID: {unique_id})")
    except Exception as e:
        print(f"❌ Failed to embed doc '{doc['title']}': {e}")

# =========================
# 🚀 Upsert to Qdrant
# =========================
try:
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Inserted {len(points)} vectors into Qdrant collection '{COLLECTION_NAME}'")
except Exception as e:
    print(f"❌ Failed to upsert points to Qdrant: {e}")

