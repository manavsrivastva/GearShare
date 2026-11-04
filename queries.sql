-- GearShare Phase 3 - Task 3.5
-- Today: 2026-11-03

-- Q1: Find items tagged 'photo', displaying all tags belonging to those items.
-- JOIN: INNER JOIN connects matching items to their tags.
SELECT i.name, t.tag_name AS tag
FROM items i
JOIN item_tags it ON i.sku = it.sku
JOIN tags t ON it.tag_id = t.tag_id
WHERE i.sku IN (
    SELECT it2.sku
    FROM item_tags it2
    JOIN tags t2 ON it2.tag_id = t2.tag_id
    WHERE t2.tag_name = 'photo'
)
ORDER BY i.name, t.tag_name;


-- Q2: Show items currently on rental and the customers who have them.
-- JOIN: INNER JOIN is appropriate because only active rentals are requested.
SELECT r.rental_id, c.name AS customer, i.name AS item
FROM rentals r
JOIN customers c ON r.customer_id = c.customer_id
JOIN items i ON r.sku = i.sku
WHERE r.return_date IS NULL
ORDER BY r.rental_id;


-- Q3: Find overdue rentals and calculate the number of days overdue.
-- JOIN: INNER JOIN connects each active rental to its customer and item.
SELECT c.name AS customer,
       i.name AS item,
       r.due_date,
       CAST(julianday('2026-11-03') - julianday(r.due_date) AS INTEGER)
           AS days_overdue
FROM rentals r
JOIN customers c ON r.customer_id = c.customer_id
JOIN items i ON r.sku = i.sku
WHERE r.return_date IS NULL
  AND r.due_date < '2026-11-03'
ORDER BY r.due_date;


-- Q4: Find the top 3 items by number of rentals.
-- JOIN: INNER JOIN connects rental records to item names.
SELECT i.name AS item,
       COUNT(r.rental_id) AS rentals
FROM items i
JOIN rentals r ON i.sku = r.sku
GROUP BY i.sku, i.name
ORDER BY rentals DESC, i.name ASC
LIMIT 3;


-- Q5: Find items that have never been rented.
-- JOIN: LEFT JOIN retains items even when no rental exists.
SELECT i.name
FROM items i
LEFT JOIN rentals r ON i.sku = r.sku
WHERE r.rental_id IS NULL
ORDER BY i.name;


-- Q6: Find customers with no rental since 2026-08-05.
-- JOIN: LEFT JOIN keeps customers without a recent matching rental.
-- The date condition belongs in ON, not WHERE, to preserve unmatched customers.
SELECT c.name
FROM customers c
LEFT JOIN rentals r
    ON c.customer_id = r.customer_id
   AND r.issue_date >= '2026-08-05'
WHERE r.rental_id IS NULL
ORDER BY c.name;


-- Q7: Calculate total fines per membership tier per return month.
-- JOIN: INNER JOIN connects fines to rentals, customers and membership tiers.
SELECT mt.tier_name AS tier,
       strftime('%Y-%m', r.return_date) AS month,
       SUM(f.amount) AS total_fines
FROM fines f
JOIN rentals r ON f.rental_id = r.rental_id
JOIN customers c ON r.customer_id = c.customer_id
JOIN membership_tiers mt ON c.tier_id = mt.tier_id
WHERE r.return_date IS NOT NULL
GROUP BY mt.tier_name, strftime('%Y-%m', r.return_date)
ORDER BY month, tier;


-- Q8: Compare total fines paid against total fines pending.
-- No JOIN is needed because payment status and amount are in fines.
SELECT
    CASE
        WHEN paid = 1 THEN 'Paid'
        ELSE 'Pending'
    END AS status,
    SUM(amount) AS total
FROM fines
GROUP BY paid
ORDER BY paid DESC;


-- Q9: Find customers who have rented from at least 3 different categories.
-- JOIN: INNER JOIN connects customers, rentals and item categories.
SELECT c.name,
       COUNT(DISTINCT i.category_id) AS categories
FROM customers c
JOIN rentals r ON c.customer_id = r.customer_id
JOIN items i ON r.sku = i.sku
GROUP BY c.customer_id, c.name
HAVING COUNT(DISTINCT i.category_id) >= 3
ORDER BY c.name;


-- Q10: Find categories where the average completed rental lasts more than 4 days.
-- JOIN: INNER JOIN connects completed rentals to their items and categories.
SELECT cat.category_name AS category,
       ROUND(AVG(julianday(r.return_date) - julianday(r.issue_date)), 1)
           AS avg_days
FROM rentals r
JOIN items i ON r.sku = i.sku
JOIN categories cat ON i.category_id = cat.category_id
WHERE r.return_date IS NOT NULL
GROUP BY cat.category_id, cat.category_name
HAVING AVG(julianday(r.return_date) - julianday(r.issue_date)) > 4
ORDER BY cat.category_name;


-- Q11: Calculate currently available physical units for every item.
-- LEFT JOIN retains items with no active rentals.
-- Display items are included as physical stock, even though they cannot be rented.
SELECT i.name,
       i.total_units - COUNT(r.rental_id) AS available
FROM items i
LEFT JOIN rentals r
    ON i.sku = r.sku
   AND r.return_date IS NULL
GROUP BY i.sku, i.name, i.total_units
ORDER BY i.name;


-- Q12: Find the pair of items most often rented by the same customer.
-- Self JOIN pairs two different rentals belonging to the same customer.
-- COUNT(DISTINCT) counts each customer only once for an item pair.
SELECT
    CASE WHEN i1.name < i2.name THEN i1.name ELSE i2.name END AS item_a,
    CASE WHEN i1.name < i2.name THEN i2.name ELSE i1.name END AS item_b,
    COUNT(DISTINCT r1.customer_id) AS customers
FROM rentals r1
JOIN rentals r2
    ON r1.customer_id = r2.customer_id
   AND r1.rental_id < r2.rental_id
JOIN items i1 ON r1.sku = i1.sku
JOIN items i2 ON r2.sku = i2.sku
GROUP BY
    CASE WHEN i1.name < i2.name THEN i1.name ELSE i2.name END,
    CASE WHEN i1.name < i2.name THEN i2.name ELSE i1.name END
ORDER BY customers DESC, item_a, item_b
LIMIT 1;
