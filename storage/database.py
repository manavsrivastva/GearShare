import sqlite3
from contextlib import contextmanager


class Database:
    """Manages SQLite connections and database transactions."""

    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def initialize(self, schema_sql):
        """Create database tables using the supplied schema."""
        self.connection.executescript(schema_sql)

    @contextmanager
    def transaction(self):
        """Commit successful operations and roll back failures."""
        try:
            with self.connection:
                yield self.connection
        except Exception:
            raise

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
