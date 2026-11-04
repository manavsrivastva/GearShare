from abc import ABC, abstractmethod


class Customer(ABC):
    """Abstract base class for GearShare customers."""

    def __init__(self, customer_id, name, email):
        self.customer_id = customer_id
        self.name = name
        self.email = email

    @property
    def customer_id(self):
        return self._customer_id

    @customer_id.setter
    def customer_id(self, value):
        value = str(value).strip()

        if not value:
            raise ValueError("Customer ID cannot be empty.")

        self._customer_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()

        if not value:
            raise ValueError("Customer name cannot be empty.")

        self._name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        value = str(value).strip()

        if "@" not in value or "." not in value:
            raise ValueError("Invalid email address.")

        self._email = value

    @property
    @abstractmethod
    def max_items(self):
        pass

    @property
    @abstractmethod
    def rental_period_days(self):
        pass

    @property
    @abstractmethod
    def daily_late_fee(self):
        pass

    def __str__(self):
        return (
            f"{self.name} ({self.customer_id}) | "
            f"{self.__class__.__name__}"
        )


class BasicCustomer(Customer):

    @property
    def max_items(self):
        return 2

    @property
    def rental_period_days(self):
        return 3

    @property
    def daily_late_fee(self):
        return 50


class PlusCustomer(Customer):

    @property
    def max_items(self):
        return 4

    @property
    def rental_period_days(self):
        return 5

    @property
    def daily_late_fee(self):
        return 100


class ProCustomer(Customer):

    @property
    def max_items(self):
        return 8

    @property
    def rental_period_days(self):
        return 7

    @property
    def daily_late_fee(self):
        return 150