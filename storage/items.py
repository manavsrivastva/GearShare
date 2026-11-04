class ItemStorage:
    """Database operations for gear items."""

    def __init__(self, connection):
        self.connection = connection

    def get_all(self):
        return self.connection.execute("""
            SELECT
                i.sku,
                i.name,
                i.item_type,
                i.weight_g,
                i.price,
                i.total_units,
                c.category_name,
                p.category_name AS parent_category
            FROM items AS i
            JOIN categories AS c
                ON i.category_id = c.category_id
            LEFT JOIN categories AS p
                ON c.parent_category_id = p.category_id
            ORDER BY i.sku
        """).fetchall()

    def get_by_sku(self, sku):
        return self.connection.execute("""
            SELECT *
            FROM items
            WHERE sku = ?
        """, (sku,)).fetchone()

    def add(self, item_data):
        self.connection.execute("""
            INSERT INTO items (
                sku, name, category_id, item_type,
                weight_g, price, total_units
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            item_data["sku"],
            item_data["name"],
            item_data["category_id"],
            item_data["item_type"],
            item_data["weight_g"],
            item_data["price"],
            item_data["total_units"],
        ))

    def update_units(self, sku, total_units):
        cursor = self.connection.execute("""
            UPDATE items
            SET total_units = ?
            WHERE sku = ?
        """, (total_units, sku))

        return cursor.rowcount
