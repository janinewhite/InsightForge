from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


class AppLogger:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    dataset_name TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    retrieval_intent TEXT NOT NULL,
                    retrieval_payload TEXT NOT NULL,
                    answer_text TEXT NOT NULL,
                    used_llm INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    question TEXT NOT NULL,
                    expected TEXT NOT NULL,
                    actual TEXT NOT NULL,
                    score REAL NOT NULL,
                    notes TEXT
                )
                """
            )

    def log_interaction(
        self,
        dataset_name: str,
        user_query: str,
        retrieval_intent: str,
        retrieval_payload: str,
        answer_text: str,
        used_llm: bool,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO interactions (
                    timestamp, dataset_name, user_query, retrieval_intent, retrieval_payload, answer_text, used_llm
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    dataset_name,
                    user_query,
                    retrieval_intent,
                    retrieval_payload,
                    answer_text,
                    int(used_llm),
                ),
            )

    def log_evaluation(self, question: str, expected: str, actual: str, score: float, notes: str = "") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO evaluations (timestamp, question, expected, actual, score, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (datetime.utcnow().isoformat(), question, expected, actual, score, notes),
            )
