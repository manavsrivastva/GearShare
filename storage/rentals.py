class RentalStorage:
    """Database operations for rentals and fines."""

    def __init__(self, connection):
        self.connection = connection

    def get_all(self):
        return self.connection.execute("""
            SELECT *
            FROM rentals
            ORDER BY rental_id
        """).fetchall()

    def get_by_id(self, rental_id):
        return self.connection.execute("""
            SELECT *
            FROM rentals
            WHERE rental_id = ?
        """, (rental_id,)).fetchone()

    def add(self, rental_data):
        self.connection.execute("""
            INSERT INTO rentals (
                rental_id, customer_id, sku,
                issue_date, due_date, return_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rental_data["rental_id"],
            rental_data["customer_id"],
            rental_data["sku"],
            rental_data["issue_date"],
            rental_data["due_date"],
            rental_data.get("return_date"),
        ))

    def update_due_date(self, rental_id, due_date):
        cursor = self.connection.execute("""
            UPDATE rentals
            SET due_date = ?
            WHERE rental_id = ?
        """, (due_date, rental_id))

        return cursor.rowcount

    def update_return_date(self, rental_id, return_date):
        cursor = self.connection.execute("""
            UPDATE rentals
            SET return_date = ?
            WHERE rental_id = ?
        """, (return_date, rental_id))

        return cursor.rowcount

    def add_fine(self, rental_id, amount, paid=False):
        self.connection.execute("""
            INSERT INTO fines (rental_id, amount, paid)
            VALUES (?, ?, ?)
        """, (rental_id, amount, int(paid)))

    def get_fines(self):
        return self.connection.execute("""
            SELECT rental_id, amount, paid
            FROM fines
            ORDER BY rental_id
        """).fetchall()

    def mark_fines_paid(self, rental_ids):
        updated = 0

        for rental_id in rental_ids:
            cursor = self.connection.execute("""
                UPDATE fines
                SET paid = 1
                WHERE rental_id = ? AND paid = 0
            """, (rental_id,))
            updated += cursor.rowcount

        return updated
