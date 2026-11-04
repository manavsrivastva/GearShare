import sqlite3

connection = sqlite3.connect("gearshare.db")

queries = {
    "Query 1 - Active rentals by SKU": (
        """
        SELECT * FROM rentals
        WHERE sku = ? AND return_date IS NULL
        """,
        ("1000000001",)
    ),
    "Query 2 - Customer rentals by issue date": (
        """
        SELECT * FROM rentals
        WHERE customer_id = ? AND issue_date >= ?
        """,
        ("C001", "2026-01-01")
    )
}

def show_plans(title):
    print(f"\n{title}")

    for name, (query, parameters) in queries.items():
        print(f"\n{name}")

        plan = connection.execute(
            "EXPLAIN QUERY PLAN " + query,
            parameters
        ).fetchall()

        for row in plan:
            print(row[3])

show_plans("BEFORE INDEXING")

connection.execute("""
    CREATE INDEX IF NOT EXISTS idx_rentals_sku_return
    ON rentals(sku, return_date)
""")

connection.execute("""
    CREATE INDEX IF NOT EXISTS idx_rentals_customer_issue
    ON rentals(customer_id, issue_date)
""")

connection.commit()

show_plans("AFTER INDEXING")

print("\nIndexes created successfully.")

connection.close()
