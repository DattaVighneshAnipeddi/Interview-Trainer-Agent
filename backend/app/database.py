from typing import Iterator
from pathlib import Path
from contextlib import contextmanager
import sqlite3

DATABASE_PATH = (
    Path(__file__).resolve().parent.parent / "interview_trainer.db"
)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Open a database connection and always close it."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """Create database tables and migrate existing sessions safely."""
    with get_connection() as connection:
        # 1. Create the users table first.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 2. Create the interview sessions table.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_sessions (
                session_id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                questions_json TEXT NOT NULL,
                current_question INTEGER NOT NULL DEFAULT 0,
                responses_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 3. Migrate existing databases to add user ownership.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(interview_sessions)"
            ).fetchall()
        }

        if "user_id" not in columns:
            connection.execute(
                """
                ALTER TABLE interview_sessions
                ADD COLUMN user_id INTEGER
                REFERENCES users(user_id)
                """
            )
