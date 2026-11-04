import sqlite3
import sys


def test_schema_creation():
    sql = sys.stdin.read()

    assert sql.strip(), "schema.sql was not provided."

    conn = sqlite3.connect(":memory:")

    try:
        conn.executescript(sql)

        tables = {
            row[0]
            for row in conn.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
            """).fetchall()
        }

        expected_tables = {
            "membership_tiers",
            "customers",
            "categories",
            "items",
            "tags",
            "item_tags",
            "rentals",
            "fines",
            "waiting_list",
            "audit_log",
        }

        assert expected_tables.issubset(tables)

        print("Schema executed successfully.")
        print("All 10 expected tables were created.")

    finally:
        conn.close()
