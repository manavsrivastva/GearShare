import sqlite3
import sys

sql = sys.stdin.read()
conn = sqlite3.connect("gearshare.db")

statements = [
    statement.strip()
    for statement in sql.split(";")
    if statement.strip()
]

for index, statement in enumerate(statements, start=1):
    if statement.startswith("--"):
        lines = statement.splitlines()
        statement = "\n".join(
            line for line in lines
            if not line.strip().startswith("--")
        ).strip()

    if not statement:
        continue

    print(f"\n{'=' * 15} Q{index} {'=' * 15}")

    cursor = conn.execute(statement)

    if cursor.description:
        print([column[0] for column in cursor.description])
        for row in cursor.fetchall():
            print(row)

conn.close()
