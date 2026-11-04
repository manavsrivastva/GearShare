# Phase 3 - Database Indexing Report

## Objective
Compare SQLite query execution plans before and after adding indexes.

## Query 1: Active rentals by SKU

Query:
SELECT * FROM rentals
WHERE sku = ? AND return_date IS NULL;

Index:
idx_rentals_sku_return ON rentals(sku, return_date)

Before: SCAN rentals
After: SEARCH rentals USING INDEX idx_rentals_sku_return

## Query 2: Customer rentals by issue date

Query:
SELECT * FROM rentals
WHERE customer_id = ? AND issue_date >= ?;

Index:
idx_rentals_customer_issue ON rentals(customer_id, issue_date)

Before: SCAN rentals
After: SEARCH rentals USING INDEX idx_rentals_customer_issue

## Analysis
Before indexing, SQLite performed full table scans for both queries.

After indexing, SQLite used indexed searches for both queries.

The indexes reduce the need to examine unrelated rows as the rentals table grows.

The sample database is small, so this demonstrates query-plan improvements rather than a statistically meaningful execution-time reduction.

## Conclusion
Both indexes were successfully created and verified using EXPLAIN QUERY PLAN.

The index definitions are included in schema.sql and storage/schema.py.
