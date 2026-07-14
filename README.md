# VERA — Verified and Reliable AI

A self-auditing multi-agent AI tutor for CS interview preparation.

**Live demo:** https://vera-zaid.vercel.app

## What makes it different

Most chatbots call an API and return whatever they get. VERA runs four
specialized agents on every question:

1. **Guard** — blocks non-CS questions immediately
2. **Response Agent** — answers using RAG over a curated CS knowledge base
3. **Critic Agent** — adversarially challenges the answer for errors and gaps
4. **Synthesis Agent** — merges both outputs and assigns a confidence score

Every night, a fifth agent — the **Auditor** — fires 58 benchmark questions
at VERA via GitHub Actions, logs failures, and patches ChromaDB automatically.
The dashboard shows accuracy improving over time with zero human input.

## Architecture

Guard → Response Agent → Critic Agent → Synthesis Agent → Output

Nightly: Synthesis → Auditor → ChromaDB patch → Dashboard

## Results

- Benchmark accuracy: 87.9% on first clean run across 13 CS topics
- Automated nightly self-testing via GitHub Actions
- Human-in-the-loop review queue for responses below 60% confidence

## Tech stack

| Component | Tool |
|-----------|------|
| Agent orchestration | LangGraph |
| LLM inference | Groq API (Llama 3.3 70B) |
| Vector database | ChromaDB |
| Backend | FastAPI |
| Frontend | React + Recharts |
| Deployment | Render.com + Vercel |
| Automation | GitHub Actions (nightly cron) |

## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/vera
cd vera
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# add your GROQ_API_KEY and GEMINI_API_KEY to .env
python load_kb.py
uvicorn backend.api.main:app --reload
# in another terminal
cd frontend && npm install && npm run dev
```

Open http://localhost:5173