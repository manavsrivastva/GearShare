class CustomerStorage:
    """Database operations for customers and membership tiers."""

    def __init__(self, connection):
        self.connection = connection

    def get_all(self):
        return self.connection.execute("""
            SELECT
                c.customer_id,
                c.name,
                c.email,
                t.tier_name,
                t.max_items,
                t.rental_days,
                t.daily_late_fee
            FROM customers AS c
            JOIN membership_tiers AS t
                ON c.tier_id = t.tier_id
            ORDER BY c.customer_id
        """).fetchall()

    def get_by_id(self, customer_id):
        return self.connection.execute("""
            SELECT
                c.customer_id,
                c.name,
                c.email,
                t.tier_name,
                t.max_items,
                t.rental_days,
                t.daily_late_fee
            FROM customers AS c
            JOIN membership_tiers AS t
                ON c.tier_id = t.tier_id
            WHERE c.customer_id = ?
        """, (customer_id,)).fetchone()

    def add(self, customer_data):
        self.connection.execute("""
            INSERT INTO customers (
                customer_id, name, email, tier_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            customer_data["customer_id"],
            customer_data["name"],
            customer_data["email"],
            customer_data["tier_id"],
        ))

    def update_email(self, customer_id, email):
        cursor = self.connection.execute("""
            UPDATE customers
            SET email = ?
            WHERE customer_id = ?
        """, (email, customer_id))

        return cursor.rowcount
