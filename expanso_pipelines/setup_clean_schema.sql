-- =============================================================================
-- Setup Script: Create Clean Destination Schemas and Tables
-- =============================================================================
-- Run this before executing Expanso pipelines to create the destination tables.
-- The original bad data remains untouched in bad_data_workshop schema.
-- =============================================================================

-- Create schemas for clean and rejected data
CREATE SCHEMA IF NOT EXISTS bad_data_workshop_clean;
CREATE SCHEMA IF NOT EXISTS bad_data_workshop_rejected;

-- =============================================================================
-- CLEAN DESTINATION TABLES
-- =============================================================================

-- Problem 3: Fixed data types
CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.transactions_typed (
    transaction_id INTEGER PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    quantity INTEGER NOT NULL,
    is_refund BOOLEAN NOT NULL,
    customer_age INTEGER NOT NULL
);

-- Problem 5: Deduplicated users
CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.users_unique (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),
    created_at TIMESTAMP NOT NULL
);

-- Problem 7: Normalized casing
CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.contacts_normalized (
    contact_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company VARCHAR(200),
    country VARCHAR(100)
);

-- Problem 8: Trimmed whitespace
CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.inventory_trimmed (
    sku VARCHAR(100) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    supplier VARCHAR(200),
    warehouse_location VARCHAR(50)
);

-- Problem 9: Validated emails
CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.subscribers_valid (
    subscriber_id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subscribed_at TIMESTAMP NOT NULL
);

-- Problem 10: Validated sales
CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.sales_validated (
    sale_id INTEGER PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    discount_percent DECIMAL(5,2) CHECK (discount_percent >= 0 AND discount_percent <= 100),
    sale_date DATE NOT NULL CHECK (sale_date <= CURRENT_DATE),
    customer_age INTEGER CHECK (customer_age > 0 AND customer_age <= 120),
    rating DECIMAL(3,1) CHECK (rating >= 1 AND rating <= 5)
);

-- Problem 11: Normalized articles (from CSV columns)
CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.articles (
    article_id INTEGER PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    author VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.article_tags (
    article_id INTEGER NOT NULL,
    tag VARCHAR(50) NOT NULL,
    PRIMARY KEY (article_id, tag),
    FOREIGN KEY (article_id) REFERENCES bad_data_workshop_clean.articles(article_id)
);

CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.article_categories (
    article_id INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL,
    PRIMARY KEY (article_id, category),
    FOREIGN KEY (article_id) REFERENCES bad_data_workshop_clean.articles(article_id)
);

CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.article_relations (
    article_id INTEGER NOT NULL,
    related_article_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, related_article_id),
    FOREIGN KEY (article_id) REFERENCES bad_data_workshop_clean.articles(article_id)
);

-- Problem 13: Normalized from god table
CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.customers_normalized (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    country VARCHAR(100),
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.products_normalized (
    product_id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    unit_price DECIMAL(10,2),
    cost DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.orders_normalized (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TIMESTAMP NOT NULL,
    status VARCHAR(50),
    total DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    tax DECIMAL(10,2),
    shipping_carrier VARCHAR(100),
    shipping_tracking VARCHAR(100),
    shipping_method VARCHAR(50),
    estimated_delivery DATE,
    actual_delivery DATE,
    FOREIGN KEY (customer_id) REFERENCES bad_data_workshop_clean.customers_normalized(customer_id)
);

CREATE TABLE IF NOT EXISTS bad_data_workshop_clean.order_line_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2),
    line_total DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES bad_data_workshop_clean.orders_normalized(order_id),
    FOREIGN KEY (product_id) REFERENCES bad_data_workshop_clean.products_normalized(product_id)
);

-- =============================================================================
-- REJECTED/DEAD LETTER TABLES
-- =============================================================================

-- Problem 3: Parse failures
CREATE TABLE IF NOT EXISTS bad_data_workshop_rejected.transactions_parse_failures (
    id SERIAL PRIMARY KEY,
    original_data JSONB NOT NULL,
    rejection_reason VARCHAR(500) NOT NULL,
    rejected_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Problem 9: Invalid emails
CREATE TABLE IF NOT EXISTS bad_data_workshop_rejected.subscribers_invalid_emails (
    id SERIAL PRIMARY KEY,
    subscriber_id INTEGER,
    name VARCHAR(200),
    original_email VARCHAR(255),
    rejection_reason VARCHAR(500) NOT NULL,
    rejected_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Problem 10: High priority validation failures
CREATE TABLE IF NOT EXISTS bad_data_workshop_rejected.sales_high_priority (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER,
    original_data JSONB NOT NULL,
    validation_errors VARCHAR(500) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    rejected_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Problem 10: Review queue (low/medium severity)
CREATE TABLE IF NOT EXISTS bad_data_workshop_rejected.sales_review_queue (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER,
    original_data JSONB NOT NULL,
    validation_errors VARCHAR(500) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    rejected_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes on rejected tables for efficient querying
CREATE INDEX IF NOT EXISTS idx_rejected_transactions_date
    ON bad_data_workshop_rejected.transactions_parse_failures(rejected_at);
CREATE INDEX IF NOT EXISTS idx_rejected_emails_date
    ON bad_data_workshop_rejected.subscribers_invalid_emails(rejected_at);
CREATE INDEX IF NOT EXISTS idx_rejected_sales_priority
    ON bad_data_workshop_rejected.sales_high_priority(severity, rejected_at);
CREATE INDEX IF NOT EXISTS idx_rejected_sales_queue
    ON bad_data_workshop_rejected.sales_review_queue(severity, rejected_at);

-- =============================================================================
-- Verification queries to compare source vs clean record counts
-- =============================================================================

-- Use these after running pipelines to verify results:

-- SELECT 'transactions' as table_name,
--        (SELECT COUNT(*) FROM bad_data_workshop.transactions_bad_types) as source_count,
--        (SELECT COUNT(*) FROM bad_data_workshop_clean.transactions_typed) as clean_count,
--        (SELECT COUNT(*) FROM bad_data_workshop_rejected.transactions_parse_failures) as rejected_count;

-- SELECT 'users' as table_name,
--        (SELECT COUNT(*) FROM bad_data_workshop.users_duplicates) as source_count,
--        (SELECT COUNT(*) FROM bad_data_workshop_clean.users_unique) as clean_count;

COMMENT ON SCHEMA bad_data_workshop_clean IS 'Clean, normalized data output from Expanso pipelines';
COMMENT ON SCHEMA bad_data_workshop_rejected IS 'Rejected records for review and remediation';
