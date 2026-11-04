
from collections import deque


class UndoManager:
    """Undo the most recent rent or return operation using a stack."""

    def __init__(self):
        self.history = []

    def record_rent(self, rental):
        """Record a newly created rental."""
        self.history.append({
            "action": "rent",
            "rental": rental
        })

    def record_return(self, rental, previous_return_date, added_fines):
        """Record a rental return and its generated fines."""
        self.history.append({
            "action": "return",
            "rental": rental,
            "previous_return_date": previous_return_date,
            "added_fines": added_fines
        })

    def undo(self, app):
        """Undo the most recent recorded rent or return."""
        if not self.history:
            return "Nothing to undo."

        operation = self.history.pop()

        if operation["action"] == "rent":
            rental = operation["rental"]

            if rental in app.rentals:
                app.rentals.remove(rental)

            return f"Undid rent: {rental.rental_id}"

        if operation["action"] == "return":
            rental = operation["rental"]

            rental.return_date = operation["previous_return_date"]

            for fine in operation["added_fines"]:
                if fine in app.fines:
                    app.fines.remove(fine)

            return f"Undid return: {rental.rental_id}"

        return "Unknown operation."


class WaitingQueue:
    """Manage customer waiting lists using FIFO order."""

    def __init__(self):
        self.queue = deque()

    def add_customer(self, customer_id):
        if customer_id not in self.queue:
            self.queue.append(customer_id)

    def serve_next(self):
        if not self.queue:
            return None

        return self.queue.popleft()

    def peek(self):
        if not self.queue:
            return None

        return self.queue[0]

    def is_empty(self):
        return len(self.queue) == 0


class Node:
    """One node in a singly linked list."""

    def __init__(self, rental):
        self.rental = rental
        self.next = None


class RentalHistory:
    """Store rental history with newest rental first."""

    def __init__(self):
        self.head = None

    def add_rental(self, rental):
        """Insert a rental at the beginning: O(1)."""
        new_node = Node(rental)
        new_node.next = self.head
        self.head = new_node

    def get_history(self):
        """Return rental records from newest to oldest."""
        result = []
        current = self.head

        while current is not None:
            result.append(current.rental)
            current = current.next

        return result

    def is_empty(self):
        return self.head is None


def benchmark_queues(number=100000):
    """Compare removing elements from a list and a deque."""
    import time

    list_queue = list(range(number))
    start = time.perf_counter()

    while list_queue:
        list_queue.pop(0)

    list_time = time.perf_counter() - start

    deque_queue = deque(range(number))
    start = time.perf_counter()

    while deque_queue:
        deque_queue.popleft()

    deque_time = time.perf_counter() - start

    return {
        "list_pop_0_seconds": list_time,
        "deque_popleft_seconds": deque_time
    }
