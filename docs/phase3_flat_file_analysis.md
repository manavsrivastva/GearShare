# Phase 3.1 - Flat File Analysis

## Approach

Combined the four starter CSV files into gearshare_flat.csv.

The rental file is the main file. Customer details are matched using
customer_id, item details using SKU, and fine details using rental_id.

The resulting file contains one row per rental and 16 columns.

## Update Anomaly

Rohan Das (C004) appears in RN002, RN009 and RN010.

His email address is repeated in all three rows. If his email changes,
every matching rental row must be updated. If one row is missed,
the database contains inconsistent customer information.

## Insert Anomaly

Pooja Menon (C005) exists in customers.csv but has never rented an item.

In a rental-based flat file, there is no row in which her customer
information can be stored unless an artificial rental is created.

This means a new customer cannot be independently inserted.

## Delete Anomaly

RN005 is the only rental involving SD Card 128GB (SKU 1000000007).

If RN005 is deleted from the flat file, the only record containing
the SD Card's item details is also lost.

This demonstrates why customer, item and rental information should
be stored separately.

## Conclusion

The flat file repeats customer and item information across rental
records. This creates update, insert and delete anomalies.

The next step is to normalize the data into relational tables.
