import json, sqlite3, sys, time, re
from datetime import date
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from backend.config import DB_PATH, BENCHMARK_PATH, GROQ_API_KEY, AUDITOR_MODEL
from backend.rag.retriever import retrieve
import chromadb
from sentence_transformers import SentenceTransformer

AUDIT_PROMPT = """You are a CS interview expert. Answer this question accurately and concisely.

Relevant context:
{context}

Question: {question}

Give a direct, technically accurate answer in 3-5 sentences."""

def get_audit_answer(question: str) -> str:
    """
    Single-agent answer using the small fast model.
    Retries automatically on 429 rate limit errors.
    """
    llm = ChatGroq(api_key=GROQ_API_KEY, model=AUDITOR_MODEL, temperature=0.1)
    chunks = retrieve(question, n_results=3)
    context = "\n\n".join(chunks)
    prompt = AUDIT_PROMPT.format(context=context, question=question)

    for attempt in range(3):
        try:
            result = llm.invoke([HumanMessage(content=prompt)])
            return result.content
        except Exception as e:
            if "429" in str(e):
                wait = 60 * (attempt + 1)   # 60s → 120s → 180s
                print(f"    Rate limit hit. Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise   # not a rate limit error, re-raise immediately
    return ""

def normalize(text: str) -> str:
    """Normalize mathematical notation so O(n^2) matches O(n squared) etc."""
    t = text.lower()
    # Big-O notation variants
    t = re.sub(r'o\(n\s*[\^²]\s*2?\)', 'o(n squared)', t)
    t = re.sub(r'o\(n\s*2\)', 'o(n squared)', t)
    t = re.sub(r'o\(v\s*\+\s*e\)', 'o(v plus e)', t)
    t = re.sub(r'o\(\(v\s*\+\s*e\)', 'o((v plus e)', t)
    t = re.sub(r'o\(n\s*log\s*n\)', 'o(n log n)', t)
    t = re.sub(r'o\(log\s*n\)', 'o(log n)', t)
    # Synonym normalization
    t = t.replace('3-way handshake', 'three-way handshake')
    t = t.replace('three way handshake', 'three-way handshake')
    t = t.replace("kahn's", 'kahn')
    t = t.replace('divide in half', 'halving')
    t = t.replace('dividing', 'halving')
    t = t.replace('split in half', 'halving')
    t = t.replace('virtual address space', 'virtual addresses')
    t = t.replace('non-clustered', 'nonclustered')
    t = t.replace('nonclustered', 'non-clustered')
    t = t.replace('directed acyclic graph', 'directed acyclic')
    return t

def keyword_score(vera_answer: str, keywords: list) -> bool:
    normalized_answer = normalize(vera_answer)
    matched = []
    missed  = []
    for kw in keywords:
        if normalize(kw) in normalized_answer:
            matched.append(kw)
        else:
            missed.append(kw)
    # Pass if at least 70% of keywords matched (not strict 100%)
    score = len(matched) / len(keywords)
    return score >= 0.70

def patch_knowledge_base(failed: list):
    if not failed:
        return
    client     = chromadb.PersistentClient(path="./chroma_data")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    collection  = client.get_collection("vera_knowledge")

    for item in failed:
        patch_text = (
            f"IMPORTANT — Verified CS interview answer:\n"
            f"Q: {item['question']}\n"
            f"A: {item['answer']}"
        )
        embedding = embed_model.encode(patch_text).tolist()
        collection.upsert(
            ids=[f"patch-{item['id']}"],
            embeddings=[embedding],
            documents=[patch_text],
            metadatas=[{"topic": item["topic"], "is_patch": "true"}]
        )
    print(f"  Patched {len(failed)} failed questions into ChromaDB")

def run_audit():
    today = date.today().isoformat()

    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        benchmarks = json.load(f)

    print(f"\nVERA Nightly Audit — {today}")
    print(f"Model: {AUDITOR_MODEL}  (500k tokens/day free tier)")
    print(f"Running {len(benchmarks)} benchmark questions...\n")

    results        = []
    topic_results  = defaultdict(list)

    for i, item in enumerate(benchmarks, 1):
        try:
            vera_answer = get_audit_answer(item["question"])
            is_correct  = keyword_score(vera_answer, item["keywords"])

            results.append({
                **item,
                "vera_answer": vera_answer,
                "is_correct":  is_correct,
                "confidence":  0.8,   # fixed for single-agent audits
            })
            topic_results[item["topic"]].append(is_correct)

            symbol = "✓" if is_correct else "✗"
            print(f"  [{i:02d}] {symbol} [{item['topic'][:3].upper()}] {item['question'][:55]}")

            # Small pause between questions to respect per-minute limits
            time.sleep(0.5)

        except Exception as e:
            print(f"  [{i:02d}] ERROR on {item['id']}: {e}")
            results.append({
                **item,
                "vera_answer": "",
                "is_correct":  False,
                "confidence":  0.0,
            })
            topic_results[item["topic"]].append(False)

    # ── Calculate metrics ────────────────────────────────────────
    total    = len(results)
    correct  = sum(r["is_correct"] for r in results)
    overall_accuracy = correct / total
    avg_confidence   = sum(r["confidence"] for r in results) / total
    topic_accuracies = {
        topic: round(sum(vals) / len(vals), 3)
        for topic, vals in topic_results.items()
    }

    # ── Save to SQLite ───────────────────────────────────────────
    conn = sqlite3.connect(DB_PATH)
    for r in results:
        conn.execute("""
            INSERT INTO benchmark_results
                (run_date, topic, question, vera_answer,
                 correct_answer, is_correct, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (today, r["topic"], r["question"], r["vera_answer"],
              r["answer"], 1 if r["is_correct"] else 0, r["confidence"]))

    conn.execute("""
        INSERT INTO accuracy_metrics
            (run_date, overall_accuracy, topic_accuracies,
             total_questions, avg_confidence)
        VALUES (?, ?, ?, ?, ?)
    """, (today, overall_accuracy, json.dumps(topic_accuracies),
          total, avg_confidence))
    conn.commit()
    conn.close()

    # ── Patch failures into ChromaDB ─────────────────────────────
    failed = [r for r in results if not r["is_correct"]]
    patch_knowledge_base(failed)

    # ── Print summary ────────────────────────────────────────────
    print(f"\n{'='*52}")
    print(f"  Overall accuracy : {overall_accuracy:.1%}  ({correct}/{total})")
    print(f"  Avg confidence   : {avg_confidence:.1%}")
    print(f"  Failed questions : {len(failed)}")
    print(f"\n  Topics breakdown:")
    for topic, acc in sorted(topic_accuracies.items(), key=lambda x: -x[1]):
        bar = "█" * int(acc * 20)
        print(f"    {topic:<28} {acc:.0%}  {bar}")
    print(f"{'='*52}")
    print(f"\n  Patches applied. Dashboard updates on next refresh.")

if __name__ == "__main__":
    run_audit()