
import csv
from collections import Counter


def find_duplicate_skus(csv_file):
    """
    Detect duplicate SKUs in a CSV file.

    Returns a list of tuples:
    (duplicate_sku, line_number)

    Uses a set for efficient duplicate detection.
    """
    seen_skus = set()
    duplicates = []

    with open(csv_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):
            sku = row["sku"].strip()

            if sku in seen_skus:
                duplicates.append((sku, line_number))
            else:
                seen_skus.add(sku)

    return duplicates


def group_by_tag(items):
    """
    Group item names by their tags.

    Returns a dictionary:
    {
        "photo": ["Canon EOS 200D", ...],
        "audio": ["Rode Wireless Mic", ...]
    }
    """
    grouped = {}

    for item in items:
        for tag in item.tags:
            if tag not in grouped:
                grouped[tag] = []

            grouped[tag].append(item.name)

    return grouped


def most_rented(rentals, items, limit=3):
    """
    Find the most-rented items.

    Only counts rentals that have actually been issued.
    Ties are resolved alphabetically by item name.

    Returns a list of (item_name, rental_count) tuples.
    """
    counts = Counter(rental.sku for rental in rentals)

    sku_to_item = {
        item.sku: item
        for item in items
    }

    results = []

    for sku, count in counts.items():
        if sku in sku_to_item:
            item = sku_to_item[sku]
            results.append((item.name, count))

    results.sort(key=lambda entry: (-entry[1], entry[0].lower()))

    return results[:limit]


def packing_challenge(items, target_weight):
    """
    Find two different rentable items whose combined weight
    equals the target weight.

    Uses a dictionary for one-pass lookup.
    Returns a tuple of two items, or None.
    """
    seen_weights = {}

    for item in items:
        if not item.can_be_rented():
            continue

        required_weight = target_weight - item.weight_g

        if required_weight in seen_weights:
            return seen_weights[required_weight], item

        seen_weights[item.weight_g] = item

    return None
