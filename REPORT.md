# QualiFood AI — Project Report
### Africa Deep Tech Challenge 2026 — The Laptop LLM Challenge
**Team:** Solo submission — Ahmad Uba Ismail
**Domain:** Agriculture (Food Safety & Post-Harvest Loss)
**Repository:** https://github.com/Ahmadubaismail/QualiFood_Ai

---

## 1. Problem Definition and Context

Food safety and post-harvest loss are among the most persistent challenges facing farmers, small-scale food processors, and quality assurance personnel across Nigeria and much of Africa. Two problems compound each other:

1. **Post-harvest contamination**, particularly aflatoxin contamination of staple crops such as groundnuts, maize, and sorghum, is widespread in Northern Nigeria — including Kano State — due to poor drying and storage practices. Aflatoxin exposure is linked to liver disease and is classified as a Group 1 human carcinogen, yet awareness and testing capacity remain low among smallholder farmers and market traders.
2. **Lack of reliable digital food-safety guidance.** Most existing food safety tools assume constant, high-speed internet access — an assumption that does not hold in rural markets, processing facilities, or even many urban areas across the region, where connectivity is intermittent and mobile data is costly.

QualiFood AI was built to close this gap: an **offline-first food safety and quality intelligence application** that runs entirely on a standard, low-cost laptop — no cloud API, no continuous internet connection — while still offering AI-assisted guidance grounded in verified food safety knowledge.

---

## 2. Identified Constraints

| Constraint | Description |
|---|---|
| **Connectivity** | Target users (farmers, market inspectors, small food processors) frequently lack stable internet access. |
| **Compute** | Must run on the ADTC Standard Laptop profile: Intel/AMD mid-range CPU, 8 GB RAM, integrated graphics only, no discrete GPU. |
| **Cost** | Target hardware costs $150–$500, ruling out solutions that assume high-end consumer or workstation-class machines. |
| **Language & literacy** | Users often communicate in Hausa or code-switch between Hausa and English; the interface and guidance needed to remain simple and accessible. |
| **Domain accuracy** | Food safety guidance carries real health consequences, so the system must avoid hallucinated advice and stay grounded in verified reference material. |
| **Development resources** | Solo developer, mobile-phone-only access for parts of development (no dedicated development machine at every stage), limited time within the 50-day challenge window. |

---

## 3. Design Alternatives and Final Decisions

### 3.1 Model Selection
**Alternatives considered:**
- Large cloud-hosted LLMs (GPT-4 class, Claude, Gemini) via API — rejected: requires continuous internet and per-token cost, violating the offline-first requirement.
- Large local models (7B+ parameters) — rejected: exceeds the RAM/compute budget of the ADTC Standard Laptop (8 GB RAM, integrated graphics, no GPU) when accounting for OS and application overhead.
- **Small quantized local models served via Ollama** — **selected**. `qwen2.5:1.5b` was chosen as the primary model because:
  - It is small (~1 GB on disk), leaving sufficient headroom within the 7 GB peak-RAM efficiency budget defined by the ADTC scoring rubric.
  - It runs acceptably on CPU-only inference, which is required since the target hardware has no discrete GPU.
  - It retains enough language understanding to follow instructions and summarize retrieved context accurately for a narrow domain (food safety), even though it would not be competitive as a general-purpose assistant.
  - Ollama abstracts model management (`ollama pull`, `ollama run`) into simple commands, making local deployment realistic for non-specialist users setting up the tool on their own machines.

`phi3.5` and `qwen2.5:3b` were documented as alternative options in the README for users with slightly more capable hardware, trading speed for answer quality.

### 3.2 Grounding Strategy: RAG vs. Fine-Tuning
**Alternatives considered:**
- Fine-tuning the model on a food-safety dataset — rejected for this stage: requires labeled training data, compute for training, and re-training whenever information changes (e.g., new NAFDAC guidance); higher risk of overfitting on a small custom dataset.
- **Retrieval-Augmented Generation (RAG)** — **selected**. A local knowledge base of five curated reference documents (aflatoxin, HACCP fundamentals, post-harvest storage, foodborne pathogens, cold chain management) is chunked and embedded into a local ChromaDB vector store. At query time, the most relevant chunks are retrieved and injected into the model's prompt as context, and the model is instructed to answer *only* from that context.

RAG was preferred because it:
- Requires no model training or GPU access.
- Lets the knowledge base be updated simply by editing `.txt` files and re-indexing — critical for a solo developer maintaining domain accuracy over time.
- Reduces hallucination risk, since the model is grounded in retrievable source text rather than generating purely from parametric memory.

### 3.3 Application Architecture
- **Frontend:** A single-file HTML/CSS/JavaScript application (`qualifood-ai.html`) with no external framework dependency, so it can be opened directly in any browser without a build step. It provides:
  - A HACCP-based inspection checklist across five food categories (meat/fish, dairy, grains/nuts, produce, processed food), with critical control points flagged.
  - A rule-based food spoilage risk calculator (temperature, duration, packaging, visible spoilage signs) with a visual risk gauge.
  - A searchable foodborne pathogen reference.
  - An "Ask AI" chat interface that calls the local RAG backend.
  - A session activity log.
- **Backend:** A FastAPI server (`app.py`) exposing a `/chat` endpoint that performs retrieval via `rag_engine.py` and generation via the local Ollama instance, plus a `/health` endpoint for connectivity checks and a `/reindex` endpoint for refreshing the knowledge base.
- **Retrieval layer:** `rag_engine.py` handles chunking, embedding (via ChromaDB's default local embedding function), indexing, and similarity search — all running on-device.

This separation keeps the checklist and calculator features fully functional even without the AI backend running, ensuring the app remains useful in the most constrained offline scenarios, while the AI chat adds a richer layer when the local LLM is available.

---

## 4. Tools Used and Why

| Tool | Purpose | Reason for choice |
|---|---|---|
| **Ollama** | Local LLM runtime | Simplest way to run quantized GGUF models on CPU-only hardware; minimal setup for non-specialist users |
| **qwen2.5:1.5b** | Language model | Small footprint, fits ADTC RAM budget, acceptable reasoning for narrow-domain Q&A |
| **ChromaDB** | Local vector database | Runs fully on-device, no external service, simple Python API |
| **FastAPI** | Backend API server | Lightweight, fast to develop, good CORS support for connecting to a local static HTML frontend |
| **HTML/CSS/JavaScript (vanilla)** | Frontend | No build step or framework dependency required, runs offline directly from disk, minimal resource overhead |
| **GitHub** | Version control / submission hosting | Required deliverable format for ADTC (public repository) |

---

## 5. Performance Tests and Benchmarks

*(Measured on developer's Windows laptop — Intel/AMD CPU, 8 GB RAM, integrated graphics, model: `qwen2.5:1.5b`)*

| Metric | Result | Method |
|---|---|---|
| Throughput | **[FILL IN: __ tokens/sec]** | `ollama run qwen2.5:1.5b --verbose`, read from `eval rate` in output |
| Peak RAM usage | **[FILL IN: __ GB]** | Windows Task Manager, Performance tab, observed during an active `/chat` request |
| Latency (query → response) | **[FILL IN: __ seconds]** | Stopwatch measurement from pressing "Send" in the Ask AI tab to full response rendering |
| Thermal / throttling | No throttling observed during test session | Manual observation during sustained use |

*Note: exact figures above should be filled in with the values measured during local testing before final submission. The methodology follows the measurement approach the ADTC model profiler is expected to replicate for standardized scoring.*

---

## 6. Screenshots / Demonstration

See accompanying demonstration video (max 2 minutes) covering:
1. Application launch (`qualifood-ai.html`)
2. HACCP inspection checklist workflow
3. Food risk calculator with the visual risk gauge
4. Foodborne pathogen reference lookup
5. "Ask AI" chat answering a food safety question, grounded in the local knowledge base

*(Screenshots to be added to this section or to a `/screenshots` folder in the repository.)*

---

## 7. African Use Case

Aflatoxin contamination of groundnuts and maize is a well-documented public health and economic problem across Nigeria, including Kano State, where warm, humid post-harvest conditions favor *Aspergillus flavus* growth. Smallholder farmers and market traders frequently lack access to laboratory testing or trained food-safety personnel, and existing digital tools assume internet connectivity that is not reliably available in these settings.

QualiFood AI directly targets this gap by:
- Encoding practical, locally-relevant guidance on aflatoxin prevention, post-harvest storage, and HACCP principles into an offline knowledge base.
- Providing a structured HACCP checklist usable by small food businesses that cannot afford formal food-safety consultants.
- Running entirely offline on affordable hardware, matching the economic and infrastructure reality of the target users rather than requiring premium devices or continuous connectivity.

The developer's background as a Certified Food Scientist of Nigeria (CFSN), with hands-on industrial training in food quality assurance, directly informed the accuracy and relevance of the checklist items, risk calculator logic, and knowledge base content.

---

## 8. Development Note

This project was developed as a solo submission. AI-assisted tools (Claude) were used to help design the initial application architecture, generate boilerplate code, and draft reference content for the knowledge base, which was then reviewed and adapted using the developer's food science background. All setup, testing, debugging (including resolving a nested-directory issue during GitHub upload), and deployment on local hardware were carried out personally by the developer.

---

## 9. Repository Structure

```
QualiFood_Ai/
├── knowledge_base/
│   ├── aflatoxin.txt
│   ├── haccp_basics.txt
│   ├── postharvest_storage.txt
│   ├── foodborne_pathogens.txt
│   └── cold_chain.txt
├── app.py                # FastAPI server (RAG + Ollama)
├── rag_engine.py          # ChromaDB retrieval logic
├── qualifood-ai.html      # Frontend (checklist, calculator, pathogens, AI chat, log)
├── requirements.txt
└── README.md              # Setup instructions
```
