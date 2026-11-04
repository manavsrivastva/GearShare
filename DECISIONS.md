
# Phase 2 - DSA and Performance Decisions

## Decision 1: Search Algorithms
- Implemented linear search by item name.
- Implemented binary search by SKU.
- Binary search requires the catalogue to be sorted by SKU before searching.
- Reason: Binary search provides O(log n) time compared with O(n) for linear search.

## Decision 2: Sorting Algorithms
- Implemented bubble sort, insertion sort and selection sort manually.
- Used Python's built-in sorted() as the performance comparison.
- Manual algorithms print the list after each pass for learning and demonstration.
- Reason: Comparing these algorithms demonstrates the difference between O(n�) and O(n log n) sorting.

## Decision 3: Hash-Based Data Structures
- Used a set for duplicate SKU detection.
- Used dictionaries for grouping items by tags and solving the two-sum packing challenge.
- Used Counter for calculating the most-rented items.
- Reason: Hash-based lookups provide efficient average-case performance.

## Decision 4: Queues, Stacks and Linked Lists
- Used a list as a stack for undo history.
- Used collections.deque for the waiting queue.
- Implemented a singly linked list for rental history.
- Reason: Each structure demonstrates a suitable data structure for its intended operation.

## Decision 5: Recursion
- Implemented recursive factorial, Fibonacci and sum-of-digits functions.
- Implemented recursive category-tree printing, counting and path finding.
- Added an iterative category-counting comparison.
- Reason: This demonstrates recursive problem solving and comparison with iteration.

## Decision 6: Performance Benchmarking
- Used time.perf_counter() to measure execution time.
- Used median measurements from repeated runs.
- Tested core operations at 1,000, 5,000, 10,000 and 50,000 records.
- Compared sorting algorithms at 1,000, 5,000 and 10,000 elements.
- Saved measurements in docs/benchmark_results.csv and analysis in docs/benchmark_report.md.
- Reason: Repeated measurements and median values provide a more reliable comparison than a single run.


# Phase 1 - Core Python and OOP Decisions

## Decision 1: Object-Oriented Design
- Created an abstract GearItem base class.
- Implemented Equipment, Accessory and DisplayItem as separate subclasses.
- Used an abstract Customer base class with BasicCustomer, PlusCustomer and ProCustomer subclasses.
- Reason: Inheritance and polymorphism reduce code duplication and keep item and membership-specific behaviour organised.

## Decision 2: CSV-Based Data Storage
- Used CSV files to store equipment, customers, rentals and fines.
- Loaded the CSV records into Python dictionaries and lists.
- Used SKU and customer ID as dictionary keys for efficient lookups.
- Reason: CSV provides a simple, readable storage format for the project's starter data.

## Decision 3: Validation and Custom Exceptions
- Created custom exceptions for invalid SKUs, unavailable items, display-item rentals, unpaid fines and membership-limit violations.
- Validated rental requests before creating rental records.
- Applied business rules such as rental limits, late fees and extension restrictions.
- Reason: Explicit validation makes the application easier to maintain and gives users meaningful error messages.

## Decision 4: Rental and Date Management
- Used Python's date and timedelta classes for issue dates, due dates and return dates.
- Implemented late-fee calculations with a replacement-price cap.
- Restricted extensions according to item type, membership and waiting-list status.
- Reason: Date arithmetic avoids manual date calculations and keeps rental rules consistent.


## Phase 3 - Database Design Decisions

### Availability: calculated rather than stored

Decision: Calculate available units using total_units minus the number of active rentals for an item.

Reason:
- Avoids storing a value that can become stale.
- Renting and returning an item automatically changes the calculated result.
- Reduces the risk of inconsistent availability counts.

Trade-off:
- Calculating availability requires querying active rentals.
- For a very large rental history, this query may become more expensive.

When I would choose differently:
- In a high-traffic system with millions of rentals, I might maintain a cached or denormalized availability count for faster reads.
- Such a count would need to be updated safely inside transactions.
- Display items are not rentable, so their availability needs special handling.


## Phase 3 - Decision 2: Database Seeding

- Used Python's sqlite3 module to create and populate the SQLite database.
- Used parameterized INSERT statements to prevent SQL injection.
- Loaded source records from the four CSV files.
- Normalized tags into tags and item_tags tables.
- Used foreign keys to maintain referential integrity.
- Verified expected record counts after seeding.
## Phase 3 - Decision 3: SQL Query Design

- Implemented all 12 required SQL queries.
- Used INNER JOIN for records requiring matching relationships.
- Used LEFT JOIN for finding items never rented and customers without recent rentals.
- Used GROUP BY and HAVING for aggregate reports.
- Used a self-join to identify item pairs rented by the same customer.
- Used parameter-free fixed dates for reproducible project sample results.
- Verified all 12 query outputs against the project specification.


## Phase 3 - Decision 4: Transaction Management

- Used SQLite transactions to group rental and audit-log inserts into one unit.
- Deliberately violated the NOT NULL constraint on audit_log.details.
- Confirmed that the failed audit insert caused the rental insert to roll back as well.
- Repeated the operation with valid data and committed both inserts.
- Verified database state before rollback, after rollback, and after commit.
- Used explicit rollback and commit operations to maintain data consistency.


## Phase 3 - Decision 5: Database Indexing

- Added composite index on rentals(sku, return_date).
- Added composite index on rentals(customer_id, issue_date).
- Verified both indexes using EXPLAIN QUERY PLAN.
- Both queries changed from full table scans to indexed searches.
- Added index definitions to schema.sql and storage/schema.py.
