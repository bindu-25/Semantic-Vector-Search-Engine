# embedding_cache.py
# Lightweight SQLite-backed embedding cache
# Intended for reuse of text embeddings in semantic search systems

import os
import sqlite3
import pickle
import hashlib
from datetime import datetime, timezone
from typing import Optional

import numpy as np


DEFAULT_DB_PATH = "data/embedding_cache.sqlite"


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EmbeddingCache:
    """
    Simple persistent cache for text embeddings.
    Stores one embedding per text hash.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                text_hash TEXT PRIMARY KEY,
                embedding BLOB,
                updated_at TEXT
            )
            """
        )
        self.conn.commit()

    def get(self, text: str) -> Optional[np.ndarray]:
        h = text_hash(text)
        cur = self.conn.cursor()
        cur.execute(
            "SELECT embedding FROM embeddings WHERE text_hash = ?",
            (h,)
        )
        row = cur.fetchone()
        if not row:
            return None
        return pickle.loads(row[0])

    def set(self, text: str, embedding: np.ndarray):
        h = text_hash(text)
        emb_blob = pickle.dumps(
            np.asarray(embedding, dtype=np.float32),
            protocol=pickle.HIGHEST_PROTOCOL
        )
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO embeddings (text_hash, embedding, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(text_hash)
            DO UPDATE SET
                embedding = excluded.embedding,
                updated_at = excluded.updated_at
            """,
            (h, sqlite3.Binary(emb_blob),
             datetime.now(timezone.utc).isoformat())
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
