# Phase 3.2 - Database Normalization

## Starting point: Unnormalized flat file

The file gearshare_flat.csv contains one row per rental.

However, the tags column contains multiple values in one cell.

Example:

| rental_id | item_name | tags |
|---|---|---|
| RN002 | Canon EOS 200D | photo;dslr |
| RN007 | Canon EOS 200D | photo;dslr |

The tags field is not atomic. This makes the data unsuitable for First Normal Form.

## 1NF - First Normal Form

Rules:
- Each cell must contain one atomic value.
- Each row must be identifiable.
- Repeating groups must be removed.

Before 1NF:

| sku | item_name | tags |
|---|---|---|
| 1000000001 | Canon EOS 200D | photo;dslr |
| 1000000002 | Sony 50mm Lens | photo;lens |

After 1NF:

The tags are represented using two related tables.

### items

| sku (PK) | item_name |
|---|---|
| 1000000001 | Canon EOS 200D |
| 1000000002 | Sony 50mm Lens |

### tags

| tag_id (PK) | tag_name |
|---|---|
| 1 | photo |
| 2 | dslr |
| 3 | lens |

### item_tags

| sku (FK) | tag_id (FK) |
|---|---|
| 1000000001 | 1 |
| 1000000001 | 2 |
| 1000000002 | 1 |
| 1000000002 | 3 |

The composite primary key of item_tags is (sku, tag_id).

Each tag is now stored as an individual value.

## 2NF - Second Normal Form

Rules:
- The table must first satisfy 1NF.
- Every non-key attribute must depend on the whole candidate key.
- There must be no partial dependency on part of a composite key.

In the original flat file, rental_id uniquely identifies each rental. It is a single-column primary key.

Therefore, strictly speaking, the flat file has no partial-key dependency: a partial dependency requires a composite key.

However, customer and item details are repeated across multiple rental records. We separate facts about each entity into their own tables.

### customers

| customer_id (PK) | name | email | membership_type |
|---|---|---|---|
| C001 | Ananya Nair | ananya@example.com | Basic |
| C002 | Vikram Shah | vikram@example.com | Plus |

### items

| sku (PK) | name | category | weight_g | price |
|---|---|---|---|---|
| 1000000001 | Canon EOS 200D | Cameras | 450 | 45000 |
| 1000000002 | Sony 50mm Lens | Lenses | 280 | 18000 |

### rentals

| rental_id (PK) | customer_id (FK) | sku (FK) | issue_date | due_date | return_date |
|---|---|---|---|---|---|
| RN002 | C004 | 1000000001 | 2026-10-28 | 2026-10-31 | NULL |

Customer facts now belong to customers, item facts belong to items, and rental facts belong to rentals.

This avoids repeating customer and item descriptions in every rental record.

## 3NF - Third Normal Form

Rules:
- The table must satisfy 2NF.
- Non-key attributes must not depend on other non-key attributes.
- There must be no transitive dependencies.

### 1. Membership tiers

In the customer data, the membership tier determines the rental limits and fee.

For example:

Basic -> maximum items: 2, rental days: 3, daily late fee: 50

These values describe the tier, not an individual customer.

We therefore create:

membership_tiers(
    tier_id,
    tier_name,
    max_items,
    rental_days,
    daily_late_fee
)

customers stores tier_id as a foreign key.

### 2. Categories

An item's category may have a parent category.

For example:

Gear Hub
+-- Photography
    +-- Cameras
    +-- Lenses

The parent category is a property of the category, not a property that should be repeated for every item.

We create a categories table with a self-referencing parent_category_id foreign key.

categories(
    category_id,
    category_name,
    parent_category_id
)

items stores category_id as a foreign key.

## Final normalized table list

1. customers
2. membership_tiers
3. items
4. tags
5. item_tags
6. categories
7. rentals
8. fines
9. waiting_list
10. audit_log

## Summary

1NF removes repeating values from the tags field.

2NF analysis confirms that rental_id is a single-column key, so there is no partial dependency in the original flat file. Customer, item and rental facts are separated into their respective tables to reduce repeated data.

3NF removes transitive dependencies by moving membership rules into membership_tiers and category hierarchy information into categories.

The resulting design reduces duplication and helps prevent update, insert and delete anomalies.
