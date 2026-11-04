import csv
from pathlib import Path


class DatabaseSeeder:
    """Loads the project's CSV data into a normalized SQLite database."""

    def __init__(self, connection, data_folder="data"):
        self.connection = connection
        self.data_folder = Path(data_folder)

    def read_csv(self, filename):
        with (self.data_folder / filename).open(
            encoding="utf-8-sig",
            newline=""
        ) as file:
            return list(csv.DictReader(file))

    def seed_all(self):
        with self.connection:
            self.seed_tiers()
            self.seed_categories()
            self.seed_customers()
            self.seed_items_and_tags()
            self.seed_rentals()
            self.seed_fines()

    def seed_tiers(self):
        tiers = [
            ("Basic", 2, 3, 50),
            ("Plus", 4, 5, 100),
            ("Pro", 8, 7, 150),
        ]

        self.connection.executemany("""
            INSERT INTO membership_tiers
                (tier_name, max_items, rental_days, daily_late_fee)
            VALUES (?, ?, ?, ?)
        """, tiers)

    def seed_categories(self):
        rows = self.read_csv("gear.csv")

        # Insert parent categories first.
        parents = {
            row["parent_category"].strip()
            for row in rows
            if row.get("parent_category", "").strip()
        }

        for parent in sorted(parents):
            self.connection.execute("""
                INSERT OR IGNORE INTO categories (category_name)
                VALUES (?)
            """, (parent,))

        # Insert child categories with their parent IDs.
        for row in rows:
            category_name = row["category"].strip()
            parent_name = row.get("parent_category", "").strip()

            parent = self.connection.execute("""
                SELECT category_id
                FROM categories
                WHERE category_name = ?
            """, (parent_name,)).fetchone() if parent_name else None

            self.connection.execute("""
                INSERT OR IGNORE INTO categories (
                    category_name, parent_category_id
                )
                VALUES (?, ?)
            """, (
                category_name,
                parent["category_id"] if parent else None,
            ))

    def seed_customers(self):
        tier_ids = {
            row["tier_name"]: row["tier_id"]
            for row in self.connection.execute("""
                SELECT tier_id, tier_name
                FROM membership_tiers
            """)
        }

        for row in self.read_csv("customers.csv"):
            tier_name = row["membership_type"].strip()

            self.connection.execute("""
                INSERT INTO customers
                    (customer_id, name, email, tier_id)
                VALUES (?, ?, ?, ?)
            """, (
                row["customer_id"],
                row["name"],
                row["email"],
                tier_ids[tier_name],
            ))

    def seed_items_and_tags(self):
        for row in self.read_csv("gear.csv"):
            category = self.connection.execute("""
                SELECT category_id
                FROM categories
                WHERE category_name = ?
            """, (row["category"].strip(),)).fetchone()

            self.connection.execute("""
                INSERT INTO items (
                    sku, name, category_id, item_type,
                    weight_g, price, total_units
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["sku"],
                row["name"],
                category["category_id"],
                row["item_type"],
                row["weight_g"],
                row["price"],
                row["total_units"],
            ))

            for tag in row.get("tags", "").split(";"):
                tag = tag.strip().lower()
                if not tag:
                    continue

                self.connection.execute("""
                    INSERT OR IGNORE INTO tags (tag_name)
                    VALUES (?)
                """, (tag,))

                tag_id = self.connection.execute("""
                    SELECT tag_id FROM tags WHERE tag_name = ?
                """, (tag,)).fetchone()["tag_id"]

                self.connection.execute("""
                    INSERT INTO item_tags (sku, tag_id)
                    VALUES (?, ?)
                """, (row["sku"], tag_id))

    def seed_rentals(self):
        for row in self.read_csv("rentals.csv"):
            self.connection.execute("""
                INSERT INTO rentals (
                    rental_id, customer_id, sku,
                    issue_date, due_date, return_date
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row["rental_id"],
                row["customer_id"],
                row["sku"],
                row["issue_date"],
                row["due_date"],
                row.get("return_date") or None,
            ))

    def seed_fines(self):
        for row in self.read_csv("fines.csv"):
            self.connection.execute("""
                INSERT INTO fines (rental_id, amount, paid)
                VALUES (?, ?, ?)
            """, (
                row["rental_id"],
                row["amount"],
                1 if row["paid"].strip().lower() == "yes" else 0,
            ))

