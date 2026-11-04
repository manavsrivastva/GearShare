
def linear_search_by_name(items, target):
    """
    Search for an item by name (case-insensitive).

    Returns the matching item or None.

    Time Complexity: O(n)
    Space Complexity: O(1)
    """

    target = target.strip().lower()

    for item in items:
        if item.name.lower() == target:
            return item

    return None


def binary_search_by_sku(items, target):
    """
    Search for an item by SKU.

    IMPORTANT: items must already be sorted by SKU.

    Returns the matching item or None.

    Time Complexity: O(log n)
    Space Complexity: O(1)
    """

    target = str(target)

    low = 0
    high = len(items) - 1

    while low <= high:

        mid = (low + high) // 2
        current_sku = items[mid].sku

        if current_sku == target:
            return items[mid]

        elif current_sku < target:
            low = mid + 1

        else:
            high = mid - 1

    return None
