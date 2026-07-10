"""
rag_engine.py
--------------
Handles Retrieval-Augmented Generation (RAG) for QualiFood AI.

What it does:
1. Reads every .txt file in knowledge_base/
2. Splits them into chunks
3. Stores them in ChromaDB (a local vector database — no internet, no cloud)
4. Provides a way to retrieve the most relevant information for a given query

Uses ChromaDB's default embedding function (all-MiniLM-L6-v2),
which runs entirely on your device — no API calls to external services.
"""

import os
import chromadb
from chromadb.config import Settings

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_store")

CHUNK_SIZE = 600     # approx characters per chunk
CHUNK_OVERLAP = 80   # characters shared between consecutive chunks, so context isn't lost at boundaries


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split a long text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


class RagEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_DIR)
        self.collection = self.client.get_or_create_collection(
            name="qualifood_kb",
            metadata={"hnsw:space": "cosine"},
        )
        self._ensure_indexed()

    def _ensure_indexed(self):
        """If the collection is empty, read and index every file in knowledge_base/."""
        if self.collection.count() > 0:
            print(f"[RAG] Already indexed {self.collection.count()} chunks in the database.")
            return

        print("[RAG] No documents indexed yet — reading knowledge_base/ ...")
        doc_id = 0
        for fname in sorted(os.listdir(KB_DIR)):
            if not fname.endswith(".txt"):
                continue
            path = os.path.join(KB_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            chunks = chunk_text(text)
            ids = [f"{fname}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": fname} for _ in chunks]
            self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)
            doc_id += len(chunks)
            print(f"[RAG]  -> {fname}: {len(chunks)} chunks")

        print(f"[RAG] Done. Total chunks indexed: {doc_id}")

    def retrieve(self, query, n_results=4):
        """Find the chunks most relevant to the user's query."""
        results = self.collection.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return list(zip(docs, metas))

    def reindex(self):
        """Clear everything and re-index (use this after editing files in knowledge_base/)."""
        self.client.delete_collection("qualifood_kb")
        self.collection = self.client.get_or_create_collection(
            name="qualifood_kb", metadata={"hnsw:space": "cosine"}
        )
        self._ensure_indexed()


if __name__ == "__main__":
    # Quick test from the command line: python rag_engine.py "your question"
    import sys
    engine = RagEngine()
    q = sys.argv[1] if len(sys.argv) > 1 else "why do groundnuts get moldy?"
    print(f"\nQuery: {q}\n")
    for doc, meta in engine.retrieve(q):
        print(f"--- from {meta['source']} ---")
        print(doc[:200], "...\n")
