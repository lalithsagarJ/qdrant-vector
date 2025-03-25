## 📄 README.md

```
# ⚡ Local Semantic Search with Qdrant + SentenceTransformers + FastAPI

This project is a blazing-fast, fully offline-capable vector search engine using:

- 🧠 **Local Embeddings** via Hugging Face SentenceTransformers
- 🚀 **Qdrant** as the vector database
- 🌐 **FastAPI** as a search API layer
- 📂 `.txt` files from `./data/` as your searchable corpus

---

## 🔧 Setup

### 1. Clone this repo

```
git clone https://github.com/lalithsagarJ/qdrant-vector.git
cd qdrant-vector
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

Or manually:

```
pip install sentence-transformers qdrant-client fastapi uvicorn python-multipart
```

### 3. Add your `.txt` files

Put all your documents in the `data/` folder:

```
project/
├── data/
│   ├── doc1.txt
│   └── doc2.txt
```

---

## 🚀 Usage

### 🧠 Step 1: Load & Embed Documents

This will:
- Read all `.txt` files
- Generate 384-dim sentence embeddings using `all-MiniLM-L6-v2`
- Push them into Qdrant (will recreate the collection)

```
python qdrant_embed.py
```

---

### 🌐 Step 2: Run the Search API

```
uvicorn qdrant_api:app --reload --port 8080
```

---

## 🔍 Search from Python

```python
import requests

response = requests.post("http://localhost:8080/search", json={
    "query": "vector similarity search",
    "top_k": 3
})
print(response.json())
```

---

## 📦 Folder Structure

```
├── data/                     # Your documents (.txt)
├── qdrant_embed.py           # Ingest & embed script
├── qdrant_api.py             # FastAPI search server
├── README.md                 # This file
```

---

## 🛠 Tech Stack

| Component              | Role                               |
|------------------------|------------------------------------|
| `sentence-transformers`| Local text embedding               |
| `qdrant-client`        | Vector DB client                   |
| `Qdrant`               | Storage + ANN search engine        |
| `FastAPI`              | Search API server                  |
| `Uvicorn`              | ASGI server                        |

---

## 🧩 What's Next?

- Add PDF/CSV/Markdown ingestion
- Deploy on GKE, Docker, or Fly.io
- Build a chatbot (RAG-style) on top of this
- Add auth, TLS, logging, metrics, and health checks

---

## 🧠 Author

**Lalith Sagar**, a vector cowboy 🤠  
Built with help from my DevOps + AI ninja partner 🥷

---

## ☠️ License

MIT – use it, abuse it, build something epic.

```

---

