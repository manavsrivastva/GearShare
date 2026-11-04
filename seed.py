
import csv
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "gearshare.db"
DATA_DIR = BASE_DIR / "data"


# Read CSV files safely, including files containing a UTF-8 BOM.
def read_csv(filename):
    file_path = DATA_DIR / filename

    with open(file_path, newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def seed_database():
    conn = sqlite3.connect(DB_PATH)

    try:
        # Enable foreign-key validation.
        conn.execute("PRAGMA foreign_keys = ON")

        # Receive schema SQL through PowerShell standard input.
        schema_sql = sys.stdin.read()

        if not schema_sql.strip():
            raise ValueError("Schema SQL was not provided.")

        # Create database tables.
        conn.executescript(schema_sql)

        with conn:

            # --------------------------------
            # 1. MEMBERSHIP TIERS
            # --------------------------------

            tiers = [
                (1, "Basic", 2, 3, 50),
                (2, "Plus", 4, 5, 100),
                (3, "Pro", 8, 7, 150),
            ]

            conn.executemany("""
                INSERT INTO membership_tiers
                (tier_id, tier_name, max_items, rental_days, daily_late_fee)
                VALUES (?, ?, ?, ?, ?)
            """, tiers)

            # --------------------------------
            # 2. CATEGORIES
            # --------------------------------

            category_names = [
                "Photography",
                "Cameras",
                "Lenses",
                "Drones",
                "Tripods",
                "Audio",
                "Showcase",
                "Accessories"
            ]

            category_ids = {
                name: index + 1
                for index, name in enumerate(category_names)
            }

            category_data = [
                (category_ids["Photography"], "Photography", None),
                (
                    category_ids["Cameras"],
                    "Cameras",
                    category_ids["Photography"]
                ),
                (
                    category_ids["Lenses"],
                    "Lenses",
                    category_ids["Photography"]
                ),
                (category_ids["Drones"], "Drones", None),
                (category_ids["Tripods"], "Tripods", None),
                (category_ids["Audio"], "Audio", None),
                (category_ids["Showcase"], "Showcase", None),
                (category_ids["Accessories"], "Accessories", None),
            ]

            conn.executemany("""
                INSERT INTO categories
                (category_id, category_name, parent_category_id)
                VALUES (?, ?, ?)
            """, category_data)

            # --------------------------------
            # 3. CUSTOMERS
            # --------------------------------

            tier_ids = {
                "Basic": 1,
                "Plus": 2,
                "Pro": 3
            }

            customers = read_csv("customers.csv")

            conn.executemany("""
                INSERT INTO customers
                (customer_id, name, email, tier_id)
                VALUES (?, ?, ?, ?)
            """, [
                (
                    row["customer_id"],
                    row["name"],
                    row["email"],
                    tier_ids[row["membership_type"]]
                )
                for row in customers
            ])

            # --------------------------------
            # 4. ITEMS
            # --------------------------------

            items = read_csv("gear.csv")

            conn.executemany("""
                INSERT INTO items
                (sku, name, category_id, item_type,
                 weight_g, price, total_units)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    row["sku"],
                    row["name"],
                    category_ids[row["category"]],
                    row["item_type"],
                    int(row["weight_g"]),
                    float(row["price"]),
                    int(row["total_units"])
                )
                for row in items
            ])

            # --------------------------------
            # 5. TAGS
            # --------------------------------

            all_tags = sorted({
                tag.strip()
                for item in items
                for tag in item["tags"].split(";")
            })

            tag_ids = {
                tag: index + 1
                for index, tag in enumerate(all_tags)
            }

            conn.executemany("""
                INSERT INTO tags (tag_id, tag_name)
                VALUES (?, ?)
            """, [
                (tag_ids[tag], tag)
                for tag in all_tags
            ])

            # --------------------------------
            # 6. ITEM-TAG RELATIONSHIPS
            # --------------------------------

            conn.executemany("""
                INSERT INTO item_tags (sku, tag_id)
                VALUES (?, ?)
            """, [
                (item["sku"], tag_ids[tag.strip()])
                for item in items
                for tag in item["tags"].split(";")
            ])

            # --------------------------------
            # 7. RENTALS
            # --------------------------------

            rentals = read_csv("rentals.csv")

            conn.executemany("""
                INSERT INTO rentals
                (rental_id, customer_id, sku,
                 issue_date, due_date, return_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (
                    row["rental_id"],
                    row["customer_id"],
                    row["sku"],
                    row["issue_date"],
                    row["due_date"],
                    row["return_date"] or None
                )
                for row in rentals
            ])

            # --------------------------------
            # 8. FINES
            # --------------------------------

            fines = read_csv("fines.csv")

            conn.executemany("""
                INSERT INTO fines (rental_id, amount, paid)
                VALUES (?, ?, ?)
            """, [
                (
                    row["rental_id"],
                    float(row["amount"]),
                    1 if row["paid"].strip().lower() == "yes" else 0
                )
                for row in fines
            ])

        # --------------------------------
        # 9. VERIFICATION
        # --------------------------------

        print("\nDatabase seeded successfully!")

        tables = [
            "membership_tiers",
            "customers",
            "categories",
            "items",
            "tags",
            "item_tags",
            "rentals",
            "fines"
        ]

        print("\nRecord counts:")

        for table in tables:
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count}")

        open_rentals = conn.execute("""
            SELECT COUNT(*)
            FROM rentals
            WHERE return_date IS NULL
        """).fetchone()[0]

        print(f"Open rentals: {open_rentals}")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()
