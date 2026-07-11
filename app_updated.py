"""
app.py
------
The core QualiFood AI backend — connects RAG (rag_engine.py) with Ollama
(a small LLM running locally on your device, no internet required) to
answer questions about food safety and agriculture.

HOW TO RUN:
1. Make sure Ollama is running: `ollama serve` (it usually auto-starts after install)
2. Make sure you've pulled a model: `ollama pull qwen2.5:1.5b`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the server: `uvicorn app:app --reload --port 8000`
5. Open qualifood-ai.html in a browser — the "Ask AI" tab will talk to this
   server at http://localhost:8000/chat
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama

from rag_engine import RagEngine

MODEL_NAME = "qwen2.5:1.5b"   # change this if you're using a different model (e.g. "phi3.5")

app = FastAPI(title="QualiFood AI - Local RAG Backend")

# CORS — allows the HTML file (file://) or a localhost port to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[APP] Loading RAG engine (will index knowledge_base/ on first run)...")
rag = RagEngine()
print("[APP] RAG engine ready.")


class ChatRequest(BaseModel):
    message: str
    n_results: int = 6


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


SYSTEM_PROMPT = (
    "You are QualiFood AI, a food safety assistant for farmers, food processors, "
    "and quality assurance (QA) officers in Nigeria and across Africa. "
    "Answer in simple, clear language and keep responses concise and accurate. "
    "Use ONLY the information given in the 'CONTEXT' section to answer the question. "
    "Do not add facts, numbers, or advice that are not present in the context, even if they "
    "seem reasonable — food safety mistakes can harm real people. "
    "If the given context only partially answers the question, answer the part you can support "
    "and clearly say what is missing, instead of guessing. "
    "If the context does not contain relevant information at all, say so directly rather than "
    "inventing an answer. "
    "When multiple context sources are relevant, you may briefly combine them, but do not "
    "contradict the source material."
)


def build_prompt(user_message: str, retrieved_chunks):
    context_block = "\n\n".join(
        f"[From: {meta['source']}]\n{doc}" for doc, meta in retrieved_chunks
    )
    return f"""CONTEXT:
{context_block}

USER QUESTION:
{user_message}

Answer the question based on the context above, in short, clear paragraphs."""


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    retrieved = rag.retrieve(req.message, n_results=req.n_results)
    prompt = build_prompt(req.message, retrieved)

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    answer = response["message"]["content"]
    sources = sorted(set(meta["source"] for _, meta in retrieved))
    return ChatResponse(answer=answer, sources=sources)


@app.post("/reindex")
def reindex():
    """Call this after adding/editing files in knowledge_base/ to refresh the database."""
    rag.reindex()
    return {"status": "reindexed", "chunks": rag.collection.count()}
