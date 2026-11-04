import os
from collections import defaultdict, deque
from datetime import date, timedelta
from functools import wraps

from dsa.history import UndoManager

from items import Equipment, Accessory, DisplayItem
from customers import BasicCustomer, PlusCustomer, ProCustomer
from rentals import Rental

from errors import (
    CustomerNotFoundError,
    InvalidSKUError,
    DisplayItemRentalError,
    UnpaidFineError,
    TierLimitError,
    DuplicateRentalError,
    ItemUnavailableError,
)

from storage.database import Database
from storage.seed import DatabaseSeeder
from storage.schema import SCHEMA_SQL


def audit_action(function):
    """Persist successful actions and their audit records atomically."""

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        try:
            with self.db.transaction() as connection:
                result = function(self, *args, **kwargs)

                message = (
                    f"{function.__name__} called "
                    f"with args={args}, kwargs={kwargs}"
                )

                if function.__name__ == "rent_item":
                    entity_id = result.rental_id
                else:
                    entity_id = str(args[0]) if args else "unknown"

                connection.execute(
                    """
                    INSERT INTO audit_log
                    (action, entity_type, entity_id, details)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        function.__name__,
                        "rental",
                        str(entity_id),
                        message,
                    ),
                )

            self.audit_log.append(message)
            return result

        except ItemUnavailableError:
            # A failed rental can still add the customer to the queue.
            # Persist that queue change after the failed transaction rolls back.
            if function.__name__ == "rent_item" and len(args) >= 2:
                with self.db.transaction():
                    self._save_waiting_list(str(args[1]).strip())

            raise

    return wrapper


class GearShare:
    """Main GearShare service backed by SQLite."""

    def __init__(self, data_folder="data", db_path=":memory:"):

        self.data_folder = data_folder
        self.db = Database(db_path)

        self.items = {}
        self.customers = {}
        self.rentals = []
        self.fines = []

        self.waiting_lists = defaultdict(deque)
        self.audit_log = []
        self.undo_manager = UndoManager()

        self.today = date.fromisoformat(
            os.getenv("TODAY", "2026-11-03")
        )

        self._initialize_database()
        self.load_data()

    # --------------------------------------------------
    # DATABASE INITIALIZATION
    # --------------------------------------------------

    def _initialize_database(self):
        """Create tables, apply a safe migration and seed an empty database."""

        self.db.initialize(SCHEMA_SQL)

        connection = self.db.connection

        # Existing databases may have been created before extension_count
        # was added to the schema. Add it without deleting existing data.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(rentals)"
            ).fetchall()
        }

        if "extension_count" not in columns:
            connection.execute(
                """
                ALTER TABLE rentals
                ADD COLUMN extension_count INTEGER NOT NULL DEFAULT 0
                CHECK (extension_count >= 0)
                """
            )

        # Seed only when the database has no catalogue items.
        item_count = connection.execute(
            "SELECT COUNT(*) FROM items"
        ).fetchone()[0]

        if item_count == 0:
            DatabaseSeeder(
                connection,
                self.data_folder
            ).seed_all()

    # --------------------------------------------------
    # DATA LOADING
    # --------------------------------------------------

    def load_data(self):
        """Load application objects from SQLite."""

        connection = self.db.connection

        self.items.clear()
        self.customers.clear()
        self.rentals.clear()
        self.fines.clear()
        self.waiting_lists.clear()
        self.audit_log.clear()

        item_rows = connection.execute(
            """
            SELECT
                i.sku,
                i.name,
                i.item_type,
                i.weight_g,
                i.price,
                i.total_units,
                c.category_name,
                p.category_name AS parent_category
            FROM items i
            JOIN categories c
                ON i.category_id = c.category_id
            LEFT JOIN categories p
                ON c.parent_category_id = p.category_id
            ORDER BY i.sku
            """
        ).fetchall()

        item_classes = {
            "Equipment": Equipment,
            "Accessory": Accessory,
            "Display": DisplayItem,
        }

        for row in item_rows:

            tag_rows = connection.execute(
                """
                SELECT t.tag_name
                FROM item_tags it
                JOIN tags t ON it.tag_id = t.tag_id
                WHERE it.sku = ?
                ORDER BY t.tag_name
                """,
                (row["sku"],),
            ).fetchall()

            tags = ";".join(
                tag["tag_name"] for tag in tag_rows
            )

            item_class = item_classes[row["item_type"]]

            item = item_class(
                row["sku"],
                row["name"],
                tags,
                row["category_name"],
                row["parent_category"] or "",
                row["weight_g"],
                row["price"],
                row["total_units"],
            )

            self.items[item.sku] = item

        customer_rows = connection.execute(
            """
            SELECT
                c.customer_id,
                c.name,
                c.email,
                mt.tier_name
            FROM customers c
            JOIN membership_tiers mt
                ON c.tier_id = mt.tier_id
            ORDER BY c.customer_id
            """
        ).fetchall()

        customer_classes = {
            "Basic": BasicCustomer,
            "Plus": PlusCustomer,
            "Pro": ProCustomer,
        }

        for row in customer_rows:

            customer_class = customer_classes[row["tier_name"]]

            customer = customer_class(
                row["customer_id"],
                row["name"],
                row["email"],
            )

            self.customers[customer.customer_id] = customer

        rental_rows = connection.execute(
            """
            SELECT
                rental_id,
                customer_id,
                sku,
                issue_date,
                due_date,
                return_date,
                extension_count
            FROM rentals
            ORDER BY rental_id
            """
        ).fetchall()

        for row in rental_rows:

            rental = Rental(
                row["rental_id"],
                row["customer_id"],
                row["sku"],
                row["issue_date"],
                row["due_date"],
                row["return_date"],
            )

            rental.extension_count = row["extension_count"]
            self.rentals.append(rental)

        fine_rows = connection.execute(
            """
            SELECT rental_id, amount, paid
            FROM fines
            ORDER BY rental_id
            """
        ).fetchall()

        for row in fine_rows:
            self.fines.append({
                "rental_id": row["rental_id"],
                "amount": float(row["amount"]),
                "paid": bool(row["paid"]),
            })

        queue_rows = connection.execute(
            """
            SELECT customer_id, sku
            FROM waiting_list
            ORDER BY queue_id
            """
        ).fetchall()

        for row in queue_rows:
            self.waiting_lists[row["sku"]].append(
                row["customer_id"]
            )

        audit_rows = connection.execute(
            """
            SELECT action, entity_type, entity_id, details
            FROM audit_log
            ORDER BY log_id
            """
        ).fetchall()

        for row in audit_rows:
            self.audit_log.append(row["details"])

    # --------------------------------------------------
    # WAITING-LIST DATABASE SUPPORT
    # --------------------------------------------------

    def _save_waiting_list(self, sku):
        """Replace one item's stored queue while preserving FIFO order."""

        sku = str(sku)
        connection = self.db.connection

        connection.execute(
        "DELETE FROM waiting_list WHERE sku = ?",
        (sku,),
        )

        for customer_id in self.waiting_lists[sku]:
            connection.execute(
                """
                INSERT INTO waiting_list (customer_id, sku)
                VALUES (?, ?)
                """,
                (customer_id, sku),
        )

    def _save_all_waiting_lists(self):
        """Persist every in-memory waiting queue."""

        with self.db.transaction() as connection:

            connection.execute("DELETE FROM waiting_list")

            for sku, queue in self.waiting_lists.items():
                for customer_id in queue:
                    connection.execute(
                        """
                        INSERT INTO waiting_list (customer_id, sku)
                        VALUES (?, ?)
                        """,
                        (customer_id, sku),
                    )

    # --------------------------------------------------
    # HELPER METHODS
    # --------------------------------------------------

    def get_unpaid_fines(self, customer_id):
        """Calculate a customer's outstanding fines."""

        customer_rental_ids = {
            rental.rental_id
            for rental in self.rentals
            if rental.customer_id == customer_id
        }

        return sum(
            fine["amount"]
            for fine in self.fines
            if fine["rental_id"] in customer_rental_ids
            and not fine["paid"]
        )

    def get_active_rentals(self, customer_id):
        return [
            rental
            for rental in self.rentals
            if rental.customer_id == customer_id
            and rental.is_active
        ]

    def get_active_item_count(self, customer_id):
        return len(self.get_active_rentals(customer_id))

    def get_active_units(self, sku):
        return sum(
            1
            for rental in self.rentals
            if rental.sku == sku and rental.is_active
        )

    def get_available_units(self, sku):
        item = self.items[sku]

        return item.total_units - self.get_active_units(sku)

    # --------------------------------------------------
    # RENT AN ITEM
    # --------------------------------------------------

    @audit_action
    def rent_item(self, customer_id, sku):

        if customer_id not in self.customers:
            raise CustomerNotFoundError(
                f"Customer {customer_id} does not exist."
            )

        customer = self.customers[customer_id]
        sku = str(sku).strip()

        if not sku.isdigit() or len(sku) != 10:
            raise InvalidSKUError(
                "SKU must contain exactly 10 digits."
            )

        if sku not in self.items:
            raise InvalidSKUError(
                f"Item with SKU {sku} does not exist."
            )

        item = self.items[sku]

        if not item.can_be_rented():
            raise DisplayItemRentalError(
                "Display items cannot be rented."
            )

        unpaid = self.get_unpaid_fines(customer_id)

        if unpaid > 500:
            raise UnpaidFineError(
                f"Outstanding fines are Rs.{unpaid:.2f}."
            )

        active_rentals = self.get_active_rentals(customer_id)

        if len(active_rentals) >= customer.max_items:
            raise TierLimitError(
                "You have reached your membership rental limit."
            )

        if any(r.sku == sku for r in active_rentals):
            raise DuplicateRentalError(
                "You already have this item rented."
            )

        queue = self.waiting_lists[sku]

        if queue and queue[0] != customer_id:

            if customer_id not in queue:
                queue.append(customer_id)

            raise ItemUnavailableError(
                "A waiting list already exists. "
                "You have been placed in the queue."
            )

        if self.get_available_units(sku) <= 0:

            if customer_id not in queue:
                queue.append(customer_id)

            raise ItemUnavailableError(
                "Item unavailable. You have been placed in the queue."
            )

        issue_date = self.today

        due_date = issue_date + timedelta(
            days=item.rental_days(customer)
        )

        rental_id = f"RN{len(self.rentals) + 1:03d}"

        rental = Rental(
            rental_id,
            customer_id,
            sku,
            issue_date,
            due_date,
        )

        self.db.connection.execute(
            """
            INSERT INTO rentals
            (
                rental_id, customer_id, sku,
                issue_date, due_date, return_date,
                extension_count
            )
            VALUES (?, ?, ?, ?, ?, NULL, 0)
            """,
            (
                rental.rental_id,
                rental.customer_id,
                rental.sku,
                rental.issue_date.isoformat(),
                rental.due_date.isoformat(),
            ),
        )

        self.rentals.append(rental)
        self.undo_manager.record_rent(rental)

        if queue and queue[0] == customer_id:
            queue.popleft()

        self._save_waiting_list(sku)

        return rental

    # --------------------------------------------------
    # EXTEND A RENTAL
    # --------------------------------------------------

    @audit_action
    def extend_rental(self, rental_id):

        rental = next(
            (
                r for r in self.rentals
                if r.rental_id == rental_id
            ),
            None,
        )

        if rental is None:
            raise ValueError("Rental not found.")

        customer = self.customers[rental.customer_id]
        item = self.items[rental.sku]

        waiting_list_exists = bool(
            self.waiting_lists[rental.sku]
        )

        new_due_date = rental.extend(
            customer,
            item,
            waiting_list_exists=waiting_list_exists,
        )

        self.db.connection.execute(
            """
            UPDATE rentals
            SET due_date = ?, extension_count = ?
            WHERE rental_id = ?
            """,
            (
                rental.due_date.isoformat(),
                rental.extension_count,
                rental.rental_id,
            ),
        )

        return new_due_date

    # --------------------------------------------------
    # OVERDUE RENTALS
    # --------------------------------------------------

    def overdue_rentals(self):

        for rental in self.rentals:
            if (
                rental.is_active
                and rental.days_late(self.today) > 0
            ):
                yield rental

    # --------------------------------------------------
    # CATALOGUE AND CUSTOMER REPORT
    # --------------------------------------------------

    def catalogue(self):
        return list(self.items.values())

    def customer_report(self, customer_id):

        if customer_id not in self.customers:
            raise CustomerNotFoundError(
                f"Customer {customer_id} does not exist."
            )

        customer = self.customers[customer_id]

        return {
            "customer": customer.name,
            "membership": customer.__class__.__name__,
            "active_rentals": self.get_active_item_count(customer_id),
            "unpaid_fines": self.get_unpaid_fines(customer_id),
        }

    # --------------------------------------------------
    # RETURN AN ITEM
    # --------------------------------------------------

    @audit_action
    def return_item(self, rental_id):

        rental = next(
            (
                r for r in self.rentals
                if r.rental_id == rental_id
            ),
            None,
        )

        if rental is None:
            raise ValueError("Rental not found.")

        if not rental.is_active:
            raise ValueError("Rental has already been returned.")

        previous_return_date = rental.return_date
        previous_fines = list(self.fines)

        rental.return_date = self.today

        customer = self.customers[rental.customer_id]
        item = self.items[rental.sku]

        late_fee = rental.calculate_late_fee(
            customer,
            item,
            self.today,
        )

        if late_fee > 0:
            new_fine = {
                "rental_id": rental.rental_id,
                "amount": late_fee,
                "paid": False,
            }

            self.fines.append(new_fine)

            self.db.connection.execute(
                """
                INSERT INTO fines (rental_id, amount, paid)
                VALUES (?, ?, 0)
                """,
                (rental.rental_id, late_fee),
            )

        self.db.connection.execute(
            """
            UPDATE rentals
            SET return_date = ?
            WHERE rental_id = ?
            """,
            (
                rental.return_date.isoformat(),
                rental.rental_id,
            ),
        )

        self._process_waiting_list(rental.sku)
        self._save_waiting_list(rental.sku)

        added_fines = [
            fine for fine in self.fines
            if fine not in previous_fines
        ]

        self.undo_manager.record_return(
            rental,
            previous_return_date,
            added_fines,
        )

        return {
            "rental_id": rental.rental_id,
            "return_date": rental.return_date,
            "late_fee": late_fee,
        }

    # --------------------------------------------------
    # WAITING LIST
    # --------------------------------------------------

    def _process_waiting_list(self, sku):

        queue = self.waiting_lists[sku]

        while queue and self.get_available_units(sku) > 0:

            customer_id = queue[0]

            if customer_id not in self.customers:
                queue.popleft()
                continue

            customer = self.customers[customer_id]
            active = self.get_active_rentals(customer_id)

            if len(active) >= customer.max_items:
                break

            if any(r.sku == sku for r in active):
                queue.popleft()
                continue

            if self.get_unpaid_fines(customer_id) > 500:
                break

            break

    # --------------------------------------------------
    # PAY FINES
    # --------------------------------------------------

    @audit_action
    def pay_fine(self, rental_id):

        matching_fines = [
            fine
            for fine in self.fines
            if fine["rental_id"] == rental_id
            and not fine["paid"]
        ]

        if not matching_fines:
            raise ValueError(
                "No unpaid fine found for this rental."
            )

        total = sum(
            fine["amount"]
            for fine in matching_fines
        )

        for fine in matching_fines:
            fine["paid"] = True

        self.db.connection.execute(
            """
            UPDATE fines
            SET paid = 1
            WHERE rental_id = ?
            """,
            (rental_id,),
        )

        return total

    # --------------------------------------------------
    # UNDO LAST ACTION
    # --------------------------------------------------

    def undo_last_action(self):
        """Undo the latest rent or return and persist the restored state."""

        previous_rental_ids = {
            rental.rental_id for rental in self.rentals
        }

        previous_fine_ids = {
            fine["rental_id"] for fine in self.fines
        }

        result = self.undo_manager.undo(self)

        current_rental_ids = {
            rental.rental_id for rental in self.rentals
        }

        current_fine_ids = {
            fine["rental_id"] for fine in self.fines
        }

        with self.db.transaction() as connection:

            # Remove rentals that were undone.
            removed_rentals = previous_rental_ids - current_rental_ids

            for rental_id in removed_rentals:
                connection.execute(
                    "DELETE FROM rentals WHERE rental_id = ?",
                    (rental_id,),
                )

            # Restore return dates for rentals still in memory.
            for rental in self.rentals:
                connection.execute(
                    """
                    UPDATE rentals
                    SET return_date = ?
                    WHERE rental_id = ?
                    """,
                    (
                        rental.return_date.isoformat()
                        if rental.return_date else None,
                        rental.rental_id,
                    ),
                )

            # Remove fines that were undone.
            removed_fines = previous_fine_ids - current_fine_ids

            for rental_id in removed_fines:
                connection.execute(
                    "DELETE FROM fines WHERE rental_id = ?",
                    (rental_id,),
                )

        return result

    # --------------------------------------------------
    # CLEANUP
    # --------------------------------------------------
    def add_item(
            self,
            sku,
            name,
            category,
            item_type,
            price,
            total_units,
            weight_g=0,
            tags=None,
        ):
            """Add a new catalogue item and persist it in SQLite."""
    
            item_classes = {
                "Equipment": Equipment,
                "Accessory": Accessory,
                "Display": DisplayItem,
            }
    
            if item_type not in item_classes:
                raise ValueError(
                    "Item type must be Equipment, Accessory or Display."
                )
    
            normalized_tags = tags or []
    
            if isinstance(normalized_tags, str):
                normalized_tags = normalized_tags.replace(",", ";").split(";")
    
            # Constructing the object applies the existing model validation.
            item = item_classes[item_type](
                sku,
                name,
                ";".join(normalized_tags),
                category,
                "",
                weight_g,
                price,
                total_units,
            )
    
            with self.db.transaction() as connection:
    
                # Prevent duplicate SKUs.
                existing_item = connection.execute(
                    "SELECT sku FROM items WHERE sku = ?",
                    (item.sku,),
                ).fetchone()
    
                if existing_item:
                    raise ValueError(
                        f"An item with SKU {item.sku} already exists."
                    )
    
                # Find or create the category.
                category_row = connection.execute(
                    """
                    SELECT category_id
                    FROM categories
                    WHERE category_name = ?
                    """,
                    (item.category,),
                ).fetchone()
    
                if category_row is None:
                    cursor = connection.execute(
                        """
                        INSERT INTO categories (category_name)
                        VALUES (?)
                        """,
                        (item.category,),
                    )
                    category_id = cursor.lastrowid
                else:
                    category_id = category_row["category_id"]
    
                # Insert the item.
                connection.execute(
                    """
                    INSERT INTO items (
                        sku,
                        name,
                        category_id,
                        item_type,
                        weight_g,
                        price,
                        total_units
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item.sku,
                        item.name,
                        category_id,
                        item_type,
                        item.weight_g,
                        item.price,
                        item.total_units,
                    ),
                )
    
                # Insert tags and their item relationships.
                for tag in item.tags:
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO tags (tag_name)
                        VALUES (?)
                        """,
                        (tag,),
                    )
    
                    tag_row = connection.execute(
                        """
                        SELECT tag_id
                        FROM tags
                        WHERE tag_name = ?
                        """,
                        (tag,),
                    ).fetchone()
    
                    connection.execute(
                        """
                        INSERT INTO item_tags (sku, tag_id)
                        VALUES (?, ?)
                        """,
                        (item.sku, tag_row["tag_id"]),
                    )
    
                # Record the operation.
                connection.execute(
                    """
                    INSERT INTO audit_log (
                        action,
                        entity_type,
                        entity_id,
                        details
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        "add_item",
                        "item",
                        item.sku,
                        f"Added catalogue item: {item.name}",
                    ),
                )
    
            # Update the in-memory catalogue after the transaction succeeds.
            self.items[item.sku] = item
    
            return item
    
    def close(self):
        """Close the SQLite connection."""

        self.db.close()