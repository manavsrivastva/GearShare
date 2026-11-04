from datetime import date, timedelta

from errors import ExtensionNotAllowedError


class Rental:
    """Represents one gear rental."""

    def __init__(
        self,
        rental_id,
        customer_id,
        sku,
        issue_date,
        due_date,
        return_date=None
    ):
        self.rental_id = str(rental_id)
        self.customer_id = str(customer_id)
        self.sku = str(sku)

        self.issue_date = self._parse_date(issue_date)
        self.due_date = self._parse_date(due_date)

        self.return_date = (
            self._parse_date(return_date)
            if return_date
            else None
        )

        if self.due_date < self.issue_date:
            raise ValueError("Due date cannot be before issue date.")

        if self.return_date and self.return_date < self.issue_date:
            raise ValueError("Return date cannot be before issue date.")

        self.extension_count = 0

    @staticmethod
    def _parse_date(value):
        """Convert a date string into a Python date object."""
        if isinstance(value, date):
            return value

        return date.fromisoformat(str(value))

    @property
    def is_active(self):
        return self.return_date is None

    def days_late(self, today=None):
        """Calculate the number of days beyond the due date."""

        if today is None:
            today = date.today()
        else:
            today = self._parse_date(today)

        effective_date = self.return_date or today

        return max(0, (effective_date - self.due_date).days)

    def calculate_late_fee(self, customer, item, today=None):
        """Calculate late fee, capped at replacement price."""

        late_days = self.days_late(today)

        fee = late_days * customer.daily_late_fee

        return min(fee, item.price)

    def extend(self, customer, item, waiting_list_exists=False):
        """Extend an equipment rental."""

        if not item.can_be_extended():
            raise ExtensionNotAllowedError(
                "This item cannot be extended."
            )

        if not self.is_active:
            raise ExtensionNotAllowedError(
                "Returned rentals cannot be extended."
            )

        if self.extension_count >= 2:
            raise ExtensionNotAllowedError(
                "A rental can only be extended twice."
            )

        if waiting_list_exists:
            raise ExtensionNotAllowedError(
                "Cannot extend because a waiting list exists."
            )

        extension_days = customer.rental_period_days

        self.due_date += timedelta(days=extension_days)
        self.extension_count += 1

        return self.due_date

    def __str__(self):
        return (
            f"Rental {self.rental_id} | "
            f"Customer: {self.customer_id} | "
            f"SKU: {self.sku} | "
            f"Due: {self.due_date} | "
            f"Active: {self.is_active}"
        )