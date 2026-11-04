import sqlite3

conn = sqlite3.connect("gearshare.db")
conn.execute("PRAGMA foreign_keys = ON")

print("Foreign key violations:")
violations = conn.execute("PRAGMA foreign_key_check").fetchall()
print(violations if violations else "None")

print("\nItems and their categories:")
rows = conn.execute("""
    SELECT items.name, categories.category_name
    FROM items
    JOIN categories ON items.category_id = categories.category_id
    ORDER BY items.name
""").fetchall()

for row in rows:
    print(row)

print("\nRental records without return dates:")
print(conn.execute("""
    SELECT COUNT(*)
    FROM rentals
    WHERE return_date IS NULL
""").fetchone()[0])

conn.close()
