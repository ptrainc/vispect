from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_database(db_path: Path) -> None:
    with connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checked_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                filename TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                brightness REAL NOT NULL,
                sharpness REAL NOT NULL,
                model_mode TEXT NOT NULL,
                image_bytes BLOB
            )
            """
        )


def save_inspection(
    db_path: Path,
    filename: str,
    status: str,
    confidence: float | None,
    width: int,
    height: int,
    brightness: float,
    sharpness: float,
    model_mode: str,
    image_bytes: bytes,
) -> int:
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO inspections
            (filename, status, confidence, width, height, brightness, sharpness, model_mode, image_bytes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (filename, status, confidence, width, height, brightness, sharpness, model_mode, image_bytes),
        )
        return int(cursor.lastrowid)


def get_history(db_path: Path) -> list[dict]:
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, checked_at, filename, status, confidence,
                   width || ' × ' || height AS resolution, model_mode
            FROM inspections
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def delete_inspection(db_path: Path, record_id: int) -> None:
    with connect(db_path) as connection:
        connection.execute("DELETE FROM inspections WHERE id = ?", (record_id,))


def clear_history(db_path: Path) -> None:
    with connect(db_path) as connection:
        connection.execute("DELETE FROM inspections")

