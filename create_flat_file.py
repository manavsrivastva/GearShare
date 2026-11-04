import csv

DATA = "data"

def read_csv(filename):
    with open(f"{DATA}/{filename}", "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


customers = {
    row["customer_id"]: row
    for row in read_csv("customers.csv")
}

items = {
    row["sku"]: row
    for row in read_csv("gear.csv")
}

fines = {
    row["rental_id"]: row
    for row in read_csv("fines.csv")
}

rentals = read_csv("rentals.csv")

columns = [
    "rental_id",
    "customer_name",
    "email",
    "tier",
    "item_name",
    "tags",
    "sku",
    "category",
    "parent_category",
    "weight_g",
    "price",
    "issue_date",
    "due_date",
    "return_date",
    "fine",
    "fine_paid",
]

flat_rows = []

for rental in rentals:
    customer = customers[rental["customer_id"]]
    item = items[rental["sku"]]
    fine = fines.get(rental["rental_id"], {})

    flat_rows.append({
        "rental_id": rental["rental_id"],
        "customer_name": customer["name"],
        "email": customer["email"],
        "tier": customer["membership_type"],
        "item_name": item["name"],
        "tags": item["tags"],
        "sku": item["sku"],
        "category": item["category"],
        "parent_category": item["parent_category"],
        "weight_g": item["weight_g"],
        "price": item["price"],
        "issue_date": rental["issue_date"],
        "due_date": rental["due_date"],
        "return_date": rental["return_date"],
        "fine": fine.get("amount", ""),
        "fine_paid": fine.get("paid", ""),
    })

with open("gearshare_flat.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(flat_rows)

print(f"Created gearshare_flat.csv with {len(flat_rows)} rental records.")
