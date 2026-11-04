-- GearShare Phase 3 - Task 3.6
-- Demonstrates transaction rollback and commit.
-- Execute through tx_demo.py because the first audit INSERT
-- intentionally violates the NOT NULL constraint.

-- Check initial state
SELECT COUNT(*) FROM rentals WHERE rental_id = 'RN011';
SELECT COUNT(*) FROM audit_log;

-- ATTEMPT 1: Deliberately fail and roll back both inserts.
BEGIN;

INSERT INTO rentals
    (rental_id, customer_id, sku, issue_date, due_date)
VALUES
    ('RN011', 'C001', '1000000002', '2026-11-03', '2026-11-06');

-- This violates the NOT NULL constraint on details.
INSERT INTO audit_log
    (action, entity_type, entity_id, details)
VALUES
    ('RENT', 'rental', 'RN011', NULL);

ROLLBACK;

-- Both counts should still be zero.
SELECT COUNT(*) FROM rentals WHERE rental_id = 'RN011';
SELECT COUNT(*) FROM audit_log;


-- ATTEMPT 2: Insert valid records and commit.
BEGIN;

INSERT INTO rentals
    (rental_id, customer_id, sku, issue_date, due_date)
VALUES
    ('RN011', 'C001', '1000000002', '2026-11-03', '2026-11-06');

INSERT INTO audit_log
    (action, entity_type, entity_id, details)
VALUES
    ('RENT', 'rental', 'RN011', 'Rental created successfully');

COMMIT;

-- Both counts should now be one.
SELECT COUNT(*) FROM rentals WHERE rental_id = 'RN011';
SELECT COUNT(*) FROM audit_log;
