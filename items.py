from abc import ABC, abstractmethod


class GearItem(ABC):
    """Abstract base class for all gear items."""

    def __init__(
        self,
        sku,
        name,
        tags,
        category,
        parent_category,
        weight_g,
        price,
        total_units
    ):
        self.sku = sku
        self.name = name
        self.tags = tags
        self.category = category
        self.parent_category = parent_category
        self.weight_g = weight_g
        self.price = price
        self.total_units = total_units

    @property
    def sku(self):
        return self._sku

    @sku.setter
    def sku(self, value):
        value = str(value).strip()

        if not value.isdigit() or len(value) != 10:
            raise ValueError("SKU must contain exactly 10 digits.")

        self._sku = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()

        if not value:
            raise ValueError("Item name cannot be empty.")

        self._name = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        if isinstance(value, str):
            value = value.split(";")

        self._tags = [
            tag.strip().lower()
            for tag in value
            if tag.strip()
        ]

    @property
    def weight_g(self):
        return self._weight_g

    @weight_g.setter
    def weight_g(self, value):
        value = int(value)

        if value < 0:
            raise ValueError("Weight cannot be negative.")

        self._weight_g = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        value = float(value)

        if value <= 0:
            raise ValueError("Price must be greater than zero.")

        self._price = value

    @property
    def total_units(self):
        return self._total_units

    @total_units.setter
    def total_units(self, value):
        value = int(value)

        if value < 0:
            raise ValueError("Total units cannot be negative.")

        self._total_units = value

    @abstractmethod
    def can_be_rented(self):
        """Return whether this item can be rented."""

    @abstractmethod
    def rental_days(self, customer):
        """Return the allowed rental duration."""

    @abstractmethod
    def can_be_extended(self):
        """Return whether this item supports extensions."""

    def __str__(self):
        return (
            f"{self.name} | SKU: {self.sku} | "
            f"Price: Rs.{self.price:.2f} | "
            f"Units: {self.total_units}"
        )


class Equipment(GearItem):

    def can_be_rented(self):
        return True

    def rental_days(self, customer):
        return customer.rental_period_days

    def can_be_extended(self):
        return True


class Accessory(GearItem):

    def can_be_rented(self):
        return True

    def rental_days(self, customer):
        return 2

    def can_be_extended(self):
        return False


class DisplayItem(GearItem):

    def can_be_rented(self):
        return False

    def rental_days(self, customer):
        return 0

    def can_be_extended(self):
        return False