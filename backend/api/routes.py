import sqlite3
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.graph.workflow import run_vera
from backend.config import DB_PATH

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

# ── /chat ──────────────────────────────────────────────────────────
@router.post("/chat")
async def chat(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = run_vera(req.query)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO responses
            (query, initial_response, critic_feedback,
             final_response, confidence_score, in_review_queue)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        req.query,
        result["initial_response"],
        json.dumps(result["critic_feedback"]),
        result["final_response"],
        result["confidence_score"],
        1 if result["in_review_queue"] else 0
    ))
    conn.commit()
    conn.close()

    return {
        "answer":             result["final_response"],
        "confidence":         round(result["confidence_score"] * 100, 1),
        "in_review_queue":    result["in_review_queue"],
        "critic_found_issues": result["critic_feedback"].get("has_issues", False),
        "critic_severity":    result["critic_feedback"].get("severity", "none"),
        "improvements_made":  result["improvements_made"],
        "is_cs_question":     result["is_cs_question"],
    }

# ── /metrics/accuracy ──────────────────────────────────────────────
@router.get("/metrics/accuracy")
def get_accuracy():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT run_date, overall_accuracy, topic_accuracies,
               total_questions, avg_confidence
        FROM accuracy_metrics
        ORDER BY run_date ASC
    """).fetchall()
    conn.close()
    return [
        {
            "date":           r[0],
            "accuracy":       round(r[1] * 100, 1),
            "topics":         json.loads(r[2]) if r[2] else {},
            "total":          r[3],
            "avg_confidence": round(r[4] * 100, 1)
        }
        for r in rows
    ]

# ── /metrics/summary ───────────────────────────────────────────────
@router.get("/metrics/summary")
def get_summary():
    conn = sqlite3.connect(DB_PATH)

    total = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
    avg_conf = conn.execute("SELECT AVG(confidence_score) FROM responses").fetchone()[0]
    in_queue = conn.execute(
        "SELECT COUNT(*) FROM responses WHERE in_review_queue = 1 AND human_verified = 0"
    ).fetchone()[0]
    latest_accuracy = conn.execute("""
        SELECT overall_accuracy FROM accuracy_metrics
        ORDER BY run_date DESC LIMIT 1
    """).fetchone()

    conn.close()
    return {
        "total_queries":      total,
        "avg_confidence":     round((avg_conf or 0) * 100, 1),
        "review_queue_size":  in_queue,
        "latest_accuracy":    round((latest_accuracy[0] if latest_accuracy else 0) * 100, 1),
    }

# ── /review-queue ──────────────────────────────────────────────────
@router.get("/review-queue")
def get_review_queue():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT id, query, final_response, confidence_score, created_at
        FROM responses
        WHERE in_review_queue = 1 AND human_verified = 0
        ORDER BY created_at DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return [
        {
            "id":         r[0],
            "query":      r[1],
            "answer":     r[2],
            "confidence": round(r[3] * 100, 1),
            "timestamp":  r[4]
        }
        for r in rows
    ]

# ── /review-queue/{id}/verify ──────────────────────────────────────
@router.post("/review-queue/{id}/verify")
def verify_response(id: int, corrected_answer: str = ""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        UPDATE responses
        SET human_verified = 1, human_correction = ?
        WHERE id = ?
    """, (corrected_answer, id))
    conn.commit()
    conn.close()
    return {"status": "verified", "id": id}

# ── /history ───────────────────────────────────────────────────────
@router.get("/history")
def get_history(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT id, query, final_response, confidence_score,
               in_review_queue, created_at
        FROM responses
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [
        {
            "id":             r[0],
            "query":          r[1],
            "answer":         r[2],
            "confidence":     round(r[3] * 100, 1),
            "in_review_queue": bool(r[4]),
            "timestamp":      r[5]
        }
        for r in rows
    ]