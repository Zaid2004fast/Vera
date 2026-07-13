import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS responses (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            query             TEXT NOT NULL,
            initial_response  TEXT,
            critic_feedback   TEXT,
            final_response    TEXT,
            confidence_score  REAL,
            in_review_queue   INTEGER DEFAULT 0,
            human_verified    INTEGER DEFAULT 0,
            human_correction  TEXT,
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS benchmark_results (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date         DATE NOT NULL,
            topic            TEXT,
            question         TEXT,
            vera_answer      TEXT,
            correct_answer   TEXT,
            is_correct       INTEGER,
            confidence_score REAL
        );

        CREATE TABLE IF NOT EXISTS accuracy_metrics (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date         DATE NOT NULL,
            overall_accuracy REAL,
            topic_accuracies TEXT,
            total_questions  INTEGER,
            avg_confidence   REAL
        );
    """)
    conn.commit()
    conn.close()
    print("✓ Database initialised")

if __name__ == "__main__":
    init_db()