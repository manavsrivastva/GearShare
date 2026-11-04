import sqlite3

conn = sqlite3.connect("gearshare.db")
conn.execute("PRAGMA foreign_keys = ON")

try:
    # Check initial state.
    rental_count = conn.execute(
        "SELECT COUNT(*) FROM rentals WHERE rental_id = 'RN011'"
    ).fetchone()[0]

    audit_count = conn.execute(
        "SELECT COUNT(*) FROM audit_log"
    ).fetchone()[0]

    print("BEFORE TRANSACTION")
    print("RN011 rentals:", rental_count)
    print("Audit records:", audit_count)

    if rental_count != 0 or audit_count != 0:
        raise RuntimeError(
            "Expected a fresh transaction demo: RN011 and audit_log must be empty."
        )

    # ATTEMPT 1: Intentionally violate NOT NULL.
    print("\nATTEMPT 1: Deliberate failure")

    conn.execute("BEGIN")

    conn.execute("""
        INSERT INTO rentals
            (rental_id, customer_id, sku, issue_date, due_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "RN011", "C001", "1000000002",
        "2026-11-03", "2026-11-06"
    ))

    try:
        conn.execute("""
            INSERT INTO audit_log
                (action, entity_type, entity_id, details)
            VALUES (?, ?, ?, ?)
        """, ("RENT", "rental", "RN011", None))

    except sqlite3.IntegrityError as error:
        print("Expected error:", error)
        conn.rollback()
        print("Transaction rolled back.")

    # Verify rollback.
    rental_count = conn.execute(
        "SELECT COUNT(*) FROM rentals WHERE rental_id = 'RN011'"
    ).fetchone()[0]

    audit_count = conn.execute(
        "SELECT COUNT(*) FROM audit_log"
    ).fetchone()[0]

    print("\nAFTER ROLLBACK")
    print("RN011 rentals:", rental_count)
    print("Audit records:", audit_count)

    assert rental_count == 0
    assert audit_count == 0

    # ATTEMPT 2: Valid transaction.
    print("\nATTEMPT 2: Successful transaction")

    conn.execute("BEGIN")

    conn.execute("""
        INSERT INTO rentals
            (rental_id, customer_id, sku, issue_date, due_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "RN011", "C001", "1000000002",
        "2026-11-03", "2026-11-06"
    ))

    conn.execute("""
        INSERT INTO audit_log
            (action, entity_type, entity_id, details)
        VALUES (?, ?, ?, ?)
    """, (
        "RENT", "rental", "RN011",
        "Rental created successfully"
    ))

    conn.commit()
    print("Transaction committed.")

    # Verify commit.
    rental_count = conn.execute(
        "SELECT COUNT(*) FROM rentals WHERE rental_id = 'RN011'"
    ).fetchone()[0]

    audit_count = conn.execute(
        "SELECT COUNT(*) FROM audit_log"
    ).fetchone()[0]

    print("\nAFTER COMMIT")
    print("RN011 rentals:", rental_count)
    print("Audit records:", audit_count)

    assert rental_count == 1
    assert audit_count == 1

    print("\nTRANSACTION DEMO COMPLETED SUCCESSFULLY.")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()
