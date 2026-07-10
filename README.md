# QualiFood AI — Local RAG Backend (For Africa Deep Tech Challenge 2026)

This file explains how to run a real on-device LLM + RAG on your computer, so QualiFood AI can answer food safety/agriculture questions **completely offline**.

## What's Included

```
qualifood-rag/
├── knowledge_base/          # Food safety/agriculture reference data (.txt files)
│   ├── aflatoxin.txt
│   ├── haccp_basics.txt
│   ├── postharvest_storage.txt
│   ├── foodborne_pathogens.txt
│   └── cold_chain.txt
├── rag_engine.py             # ChromaDB retrieval logic
├── app.py                    # FastAPI server (RAG + Ollama)
├── requirements.txt
├── qualifood-ai.html         # Frontend (now includes the "Ask AI" tab)
└── README.md
```

## Step-by-Step Setup

### 1. Install Ollama
Ollama is the simplest way to run an LLM locally without a GPU.

- Download from: https://ollama.com/download
- Choose the version for your OS (Windows/Mac/Linux)
- After installing, open a terminal/command prompt and run:
  ```
  ollama --version
  ```
  If it shows a version number, it's working.

### 2. Pull a Small Model

In the terminal:
```
ollama pull qwen2.5:1.5b
```
This model is around ~1GB and is designed to run comfortably on 8GB RAM machines without a GPU — matching the ADTC Standard Laptop spec.

**Other model options** (if you want to experiment):
- `phi3.5` — from Microsoft, strong at reasoning
- `qwen2.5:3b` — larger, better quality answers, but slower

Change the model name in `app.py` (the line `MODEL_NAME = "qwen2.5:1.5b"`) if you pick a different one.

### 3. Install Python Dependencies

Make sure you have Python 3.10+ installed. Then:
```
cd qualifood-rag
pip install -r requirements.txt
```

### 4. Run the Backend

```
uvicorn app:app --reload --port 8000
```

On the first run, it will take a moment to:
1. Read every `.txt` file in `knowledge_base/`
2. Split them into chunks and store them in ChromaDB (a local vector database)

If you see this in the terminal, everything's working:
```
[RAG] Done. Total chunks indexed: XX
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 5. Open the Frontend

Open `qualifood-ai.html` in a browser (double-click it, or drag it into Chrome/Firefox).
Go to the **🤖 AI** tab, then try a question like:
- "Why do my groundnuts get moldy?"
- "How should I store maize after harvest?"
- "What is HACCP?"

## Testing RAG On Its Own (Without Ollama)

If you want to test retrieval before connecting the LLM:
```
python rag_engine.py "why do groundnuts get moldy?"
```
This will show the retrieved chunks most relevant to the query.

## For Benchmarking (ADTC Requirement)

The challenge requires you to measure:
- **Throughput** (tokens/sec) — run `ollama run qwen2.5:1.5b --verbose`, which shows tokens/sec after each response.
- **RAM usage** — use `htop` (Linux/Mac) or Task Manager (Windows) while the model is running.
- **Latency** — measure the time from sending a question to receiving a response at the `/chat` endpoint.

Clone the "model profiler" provided in the challenge rules to generate the full benchmark results required for submission.

## Adding New Knowledge Base Content

1. Add a new `.txt` file inside `knowledge_base/`
2. Call the endpoint to refresh the database:
   ```
   curl -X POST http://localhost:8000/reindex
   ```
   Or simply re-run `uvicorn` after deleting the `chroma_store/` folder.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Ollama command not found" | Reinstall Ollama, make sure it's added to your PATH |
| Frontend shows "not connected" | Make sure `uvicorn` is running and the terminal window is still open |
| Responses are very slow | Try a smaller model (`qwen2.5:1.5b` instead of `qwen2.5:3b`) |
| CORS error in browser console | Confirm `app.py` includes CORSMiddleware (it's already included) |

## For Submission (ADTC 2026)

Remember to include in your report:
- Why you chose `qwen2.5:1.5b` (or another model) — size, speed, accuracy trade-offs
- Why you chose RAG over direct fine-tuning (RAG is simpler, easier to update with local data, and reduces hallucination)
- How the app fits the "African Use Case" bonus — food safety/aflatoxin is a real problem for farmers in Kano and across Nigeria
