import sqlite3

# Load real catalogue data into an isolated in-memory database.
source = sqlite3.connect("gearshare.db")
demo = sqlite3.connect(":memory:")

items = source.execute(
    "SELECT sku, name, item_type FROM items"
).fetchall()

demo.execute("""
    CREATE TABLE items (
        sku TEXT,
        name TEXT,
        item_type TEXT
    )
""")

demo.executemany(
    "INSERT INTO items VALUES (?, ?, ?)",
    items
)

source.close()

print("Total catalogue items:", len(items))

# Demonstration 1: Unsafe SQL using string formatting.
attack_input = "' OR '1'='1"

unsafe_query = (
    f"SELECT sku, name FROM items WHERE name = '{attack_input}'"
)

unsafe_results = demo.execute(unsafe_query).fetchall()

print("\nUNSAFE QUERY")
print("Rows returned:", len(unsafe_results))

# Demonstration 2: Safe parameterized SQL.
safe_query = "SELECT sku, name FROM items WHERE name = ?"

safe_results = demo.execute(safe_query, (attack_input,)).fetchall()

print("\nSAFE PARAMETERIZED QUERY")
print("Rows returned:", len(safe_results))

# Demonstration 3: Valid search using parameterized SQL.
valid_results = demo.execute(
    safe_query, ("DJI Mini Drone",)
).fetchall()

print("\nVALID SAFE SEARCH")
print("Rows returned:", len(valid_results))
print("Result:", valid_results)

demo.close()
print("\nSQL injection demonstration completed.")
