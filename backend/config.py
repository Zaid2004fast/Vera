import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")

GROQ_MODEL      = "llama-3.3-70b-versatile"   # full VERA pipeline (chat)
AUDITOR_MODEL   = "llama-3.1-8b-instant"       # auditor only — 500k tokens/day

EMBED_MODEL     = "all-MiniLM-L6-v2"
CONFIDENCE_THRESHOLD = 0.60
CHROMA_COLLECTION    = "vera_knowledge"
DB_PATH         = "backend/db/vera.db"
BENCHMARK_PATH  = "data/benchmarks/qa_pairs.json"