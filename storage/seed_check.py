import sys
from storage.database import Database
from storage.seed import DatabaseSeeder

schema_sql = sys.stdin.read()

db = Database(":memory:")
db.initialize(schema_sql)

seeder = DatabaseSeeder(db.connection)
seeder.seed_all()

tables = [
    "membership_tiers",
    "customers",
    "categories",
    "items",
    "tags",
    "item_tags",
    "rentals",
    "fines",
]

print("\nDATABASE SEED RESULTS")
for table in tables:
    count = db.connection.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]
    print(f"{table}: {count}")

active = db.connection.execute(
    "SELECT COUNT(*) FROM rentals WHERE return_date IS NULL"
).fetchone()[0]

print(f"open rentals: {active}")

violations = db.connection.execute(
    "PRAGMA foreign_key_check"
).fetchall()

print("Foreign key violations:", len(violations))

db.close()
