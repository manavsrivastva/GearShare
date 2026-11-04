PRAGMA foreign_keys = ON;

-- 1. Membership tiers
CREATE TABLE IF NOT EXISTS membership_tiers (
    tier_id INTEGER PRIMARY KEY,
    tier_name TEXT NOT NULL UNIQUE,
    max_items INTEGER NOT NULL CHECK (max_items >= 0),
    rental_days INTEGER NOT NULL CHECK (rental_days > 0),
    daily_late_fee REAL NOT NULL CHECK (daily_late_fee >= 0)
);

-- 2. Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    tier_id INTEGER NOT NULL,
    FOREIGN KEY (tier_id)
        REFERENCES membership_tiers(tier_id)
        ON DELETE RESTRICT
);

-- 3. Categories
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE,
    parent_category_id INTEGER,
    FOREIGN KEY (parent_category_id)
        REFERENCES categories(category_id)
        ON DELETE RESTRICT
);

-- 4. Items
CREATE TABLE IF NOT EXISTS items (
    sku TEXT PRIMARY KEY UNIQUE,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    item_type TEXT NOT NULL
        CHECK (item_type IN ('Equipment', 'Accessory', 'Display')),
    weight_g INTEGER NOT NULL CHECK (weight_g >= 0),
    price REAL NOT NULL CHECK (price >= 0),
    total_units INTEGER NOT NULL CHECK (total_units >= 0),
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE RESTRICT
);

-- 5. Tags
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY,
    tag_name TEXT NOT NULL UNIQUE
);

-- 6. Item-tag junction table
CREATE TABLE IF NOT EXISTS item_tags (
    sku TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (sku, tag_id),
    FOREIGN KEY (sku)
        REFERENCES items(sku)
        ON DELETE CASCADE,
    FOREIGN KEY (tag_id)
        REFERENCES tags(tag_id)
        ON DELETE CASCADE
);

-- 7. Rentals
CREATE TABLE IF NOT EXISTS rentals (
    rental_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    sku TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    extension_count INTEGER NOT NULL DEFAULT 0 CHECK (extension_count >= 0),
    CHECK (due_date >= issue_date),
    CHECK (return_date IS NULL OR return_date >= issue_date),
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE RESTRICT,
    FOREIGN KEY (sku)
        REFERENCES items(sku)
        ON DELETE RESTRICT
);

-- 8. Fines
CREATE TABLE IF NOT EXISTS fines (
    rental_id TEXT PRIMARY KEY,
    amount REAL NOT NULL CHECK (amount >= 0),
    paid INTEGER NOT NULL CHECK (paid IN (0, 1)),
    FOREIGN KEY (rental_id)
        REFERENCES rentals(rental_id)
        ON DELETE RESTRICT
);

-- 9. Waiting list
CREATE TABLE IF NOT EXISTS waiting_list (
    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    sku TEXT NOT NULL,
    joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (customer_id, sku),
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE CASCADE,
    FOREIGN KEY (sku)
        REFERENCES items(sku)
        ON DELETE CASCADE
);

-- 10. Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Phase 3: Performance indexes
CREATE INDEX IF NOT EXISTS idx_rentals_sku_return
ON rentals(sku, return_date);

CREATE INDEX IF NOT EXISTS idx_rentals_customer_issue
ON rentals(customer_id, issue_date);
