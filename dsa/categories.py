
def factorial(n):
    """Calculate factorial recursively."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")

    if n == 0 or n == 1:
        return 1

    return n * factorial(n - 1)


def fibonacci(n):
    """Return the nth Fibonacci number recursively."""
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers.")

    if n <= 1:
        return n

    return fibonacci(n - 1) + fibonacci(n - 2)


def sum_of_digits(n):
    """Calculate the sum of digits recursively."""
    n = abs(n)

    if n < 10:
        return n

    return (n % 10) + sum_of_digits(n // 10)


def build_category_tree(items):
    """
    Build a nested category tree from catalogue items.

    Structure:
    {
        "Photography": {
            "Cameras": ["Canon EOS 200D"],
            "Lenses": ["Sony 50mm Lens"]
        }
    }
    """
    tree = {}

    for item in items:
        parent = item.parent_category or "Other"
        category = item.category or "Uncategorised"

        if parent not in tree:
            tree[parent] = {}

        if category not in tree[parent]:
            tree[parent][category] = []

        tree[parent][category].append(item.name)

    return tree


def print_category_tree(tree, level=0):
    """Print the category tree recursively."""
    for category, children in tree.items():
        print("  " * level + str(category))

        if isinstance(children, dict):
            print_category_tree(children, level + 1)

        elif isinstance(children, list):
            for item_name in children:
                print("  " * (level + 1) + str(item_name))


def count_category_items(tree):
    """Count all items in the category tree recursively."""
    total = 0

    for children in tree.values():
        if isinstance(children, dict):
            total += count_category_items(children)
        else:
            total += len(children)

    return total


def find_category_path(tree, target):
    """
    Find the path to a category or item recursively.

    Returns a list representing the path, or None.
    """
    for category, children in tree.items():

        if category == target:
            return [category]

        if isinstance(children, dict):
            result = find_category_path(children, target)

            if result is not None:
                return [category] + result

        elif target in children:
            return [category, target]

    return None


def count_category_items_iterative(tree):
    """Count category items without recursion."""
    total = 0
    stack = list(tree.values())

    while stack:
        children = stack.pop()

        if isinstance(children, dict):
            stack.extend(children.values())
        else:
            total += len(children)

    return total
