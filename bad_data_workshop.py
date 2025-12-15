#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich>=13.7.0",
#     "faker>=28.0.0",
#     "psycopg2-binary>=2.9.9",
#     "pymysql>=1.1.0",
#     "redshift-connector>=2.1.0",
# ]
# ///
"""
Bad Data Workshop Generator

Creates a database full of intentionally problematic data for training workshops.
Supports PostgreSQL, MySQL, and Amazon Redshift.

Features 15 common data quality problems:
1. Tables without primary keys
2. Missing foreign key constraints (orphaned records)
3. Wrong data types (dates/numbers stored as strings)
4. Missing NOT NULL constraints
5. Duplicate records (no unique constraints)
6. Inconsistent date formats
7. Inconsistent string casing
8. Leading/trailing whitespace
9. Invalid email formats
10. Out-of-range values
11. Comma-separated values in columns (1NF violation)
12. Mixed encodings and special characters
13. God table with excessive denormalization
14. Missing indexes on frequently queried columns
15. Implicit type coercion traps

Usage:
    # Setup workshop database
    uv run --script bad_data_workshop.py setup \\
        --db-type postgres \\
        --host localhost \\
        --port 5432 \\
        --database workshop \\
        --user postgres \\
        --password secret

    # Teardown (complete cleanup)
    uv run --script bad_data_workshop.py teardown \\
        --db-type postgres \\
        --host localhost \\
        --database workshop \\
        --user postgres \\
        --password secret

    # Show diagnostic queries
    uv run --script bad_data_workshop.py diagnose --db-type postgres
"""

from __future__ import annotations

import argparse
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from faker import Faker
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

console = Console()
fake = Faker()
Faker.seed(42)
random.seed(42)

DBType = Literal["postgres", "mysql", "redshift"]

SCHEMA_NAME = "bad_data_workshop"


# =============================================================================
# Database Abstraction Layer
# =============================================================================
@dataclass
class DBConfig:
    """Database connection configuration."""

    db_type: DBType
    host: str
    port: int
    database: str
    user: str
    password: str


class DatabaseAdapter(ABC):
    """Abstract base class for database operations."""

    def __init__(self, config: DBConfig):
        self.config = config
        self.connection = None
        self.cursor = None

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    def create_schema(self) -> None:
        """Create the workshop schema."""
        pass

    @abstractmethod
    def drop_schema(self) -> None:
        """Drop the workshop schema and all objects."""
        pass

    def execute(self, sql: str, params: tuple | None = None) -> None:
        """Execute a SQL statement."""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)

    def executemany(self, sql: str, params_list: list[tuple]) -> None:
        """Execute a SQL statement with multiple parameter sets."""
        self.cursor.executemany(sql, params_list)

    def commit(self) -> None:
        """Commit the current transaction."""
        self.connection.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    @abstractmethod
    def get_auto_increment_syntax(self) -> str:
        """Return the auto-increment column syntax."""
        pass

    @abstractmethod
    def get_table_prefix(self) -> str:
        """Return the schema/table prefix for queries."""
        pass

    @abstractmethod
    def get_boolean_type(self) -> str:
        """Return the boolean type for this database."""
        pass


class PostgresAdapter(DatabaseAdapter):
    """PostgreSQL database adapter."""

    def connect(self) -> None:
        import psycopg2

        self.connection = psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
        )
        self.connection.autocommit = False
        self.cursor = self.connection.cursor()

    def create_schema(self) -> None:
        self.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
        self.commit()

    def drop_schema(self) -> None:
        self.execute(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE")
        self.commit()

    def get_auto_increment_syntax(self) -> str:
        return "SERIAL"

    def get_table_prefix(self) -> str:
        return f"{SCHEMA_NAME}."

    def get_boolean_type(self) -> str:
        return "BOOLEAN"


class MySQLAdapter(DatabaseAdapter):
    """MySQL database adapter."""

    def connect(self) -> None:
        import pymysql

        self.connection = pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
            autocommit=False,
            charset="utf8mb4",
        )
        self.cursor = self.connection.cursor()

    def create_schema(self) -> None:
        # MySQL: schema = database, so we create tables in current DB
        # We'll use a table prefix instead
        pass

    def drop_schema(self) -> None:
        # Drop all tables with our prefix
        self.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name LIKE 'bdw_%'
        """)
        tables = self.cursor.fetchall()
        for (table_name,) in tables:
            self.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.commit()

    def get_auto_increment_syntax(self) -> str:
        return "INT AUTO_INCREMENT"

    def get_table_prefix(self) -> str:
        return "bdw_"  # bad_data_workshop prefix

    def get_boolean_type(self) -> str:
        return "TINYINT(1)"


class RedshiftAdapter(DatabaseAdapter):
    """Amazon Redshift database adapter."""

    def connect(self) -> None:
        import redshift_connector

        self.connection = redshift_connector.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
        )
        self.connection.autocommit = False
        self.cursor = self.connection.cursor()

    def create_schema(self) -> None:
        self.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
        self.commit()

    def drop_schema(self) -> None:
        self.execute(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE")
        self.commit()

    def get_auto_increment_syntax(self) -> str:
        return "INTEGER IDENTITY(1,1)"

    def get_table_prefix(self) -> str:
        return f"{SCHEMA_NAME}."

    def get_boolean_type(self) -> str:
        return "BOOLEAN"


def get_adapter(config: DBConfig) -> DatabaseAdapter:
    """Factory function to get the appropriate database adapter."""
    adapters = {
        "postgres": PostgresAdapter,
        "mysql": MySQLAdapter,
        "redshift": RedshiftAdapter,
    }
    return adapters[config.db_type](config)


# =============================================================================
# Data Problem Generators
# =============================================================================


def problem_01_no_primary_key(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 1: Tables without primary keys.

    Creates a table with no primary key, making it impossible to uniquely
    identify rows. This causes issues with updates, deletes, and joins.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}customers_no_pk (
            customer_id INTEGER,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(255),
            created_at TIMESTAMP
        )
    """)

    # Insert data including some exact duplicates
    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            row = (
                i + 1,
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.date_time_between(start_date="-2y", end_date="now"),
            )
            rows.append(row)
            # Add some exact duplicates (10% chance)
            if random.random() < 0.1:
                rows.append(row)

        db.executemany(
            f"""
            INSERT INTO {prefix}customers_no_pk
            (customer_id, first_name, last_name, email, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_02_missing_foreign_keys(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 2: Missing foreign key constraints (orphaned records).

    Creates orders that reference non-existent customers and products,
    demonstrating referential integrity violations.
    """
    prefix = db.get_table_prefix()
    auto_inc = db.get_auto_increment_syntax()

    # Create products table (with some products)
    db.execute(f"""
        CREATE TABLE {prefix}products (
            product_id {auto_inc} PRIMARY KEY,
            product_name VARCHAR(200),
            price DECIMAL(10,2)
        )
    """)

    # Insert some products (only 100)
    products = [
        (fake.catch_phrase(), round(random.uniform(10, 500), 2))
        for _ in range(100)
    ]
    db.executemany(
        f"INSERT INTO {prefix}products (product_name, price) VALUES (%s, %s)",
        products,
    )

    # Create orders table WITHOUT foreign key constraints
    db.execute(f"""
        CREATE TABLE {prefix}orders_no_fk (
            order_id {auto_inc} PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date TIMESTAMP
        )
    """)

    # Insert orders with many orphaned references
    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for _ in range(batch_start, batch_end):
            # 30% of orders reference non-existent customers
            customer_id = (
                random.randint(900000, 999999)
                if random.random() < 0.3
                else random.randint(1, 10000)
            )
            # 20% of orders reference non-existent products
            product_id = (
                random.randint(500, 999)
                if random.random() < 0.2
                else random.randint(1, 100)
            )
            rows.append((
                customer_id,
                product_id,
                random.randint(1, 10),
                fake.date_time_between(start_date="-1y", end_date="now"),
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}orders_no_fk
            (customer_id, product_id, quantity, order_date)
            VALUES (%s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_03_wrong_data_types(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 3: Wrong data types (dates/numbers stored as strings).

    Stores dates and numbers as VARCHAR, causing sorting issues,
    preventing date arithmetic, and wasting storage.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}transactions_bad_types (
            transaction_id VARCHAR(50),
            amount VARCHAR(50),
            transaction_date VARCHAR(50),
            quantity VARCHAR(20),
            is_refund VARCHAR(10),
            customer_age VARCHAR(10)
        )
    """)

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            # Store numbers as strings with inconsistent formatting
            amount_formats = [
                f"{random.uniform(10, 1000):.2f}",
                f"${random.uniform(10, 1000):.2f}",
                f"{random.uniform(10, 1000):.4f}",
                str(int(random.uniform(10, 1000))),
            ]

            # Store dates as strings with different formats
            date_val = fake.date_between(start_date="-2y", end_date="today")
            date_formats = [
                date_val.strftime("%Y-%m-%d"),
                date_val.strftime("%m/%d/%Y"),
                date_val.strftime("%d-%m-%Y"),
                date_val.strftime("%B %d, %Y"),
                date_val.strftime("%Y%m%d"),
            ]

            rows.append((
                str(i + 1),
                random.choice(amount_formats),
                random.choice(date_formats),
                str(random.randint(1, 100)),
                random.choice(["true", "false", "True", "False", "1", "0", "yes", "no"]),
                str(random.randint(18, 80)),
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}transactions_bad_types
            (transaction_id, amount, transaction_date, quantity, is_refund, customer_age)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_04_missing_not_null(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 4: Missing NOT NULL constraints with NULLs everywhere.

    Critical fields that should never be NULL contain NULL values,
    causing application errors and incorrect aggregations.
    """
    prefix = db.get_table_prefix()
    auto_inc = db.get_auto_increment_syntax()

    db.execute(f"""
        CREATE TABLE {prefix}employees_nulls (
            employee_id {auto_inc} PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(255),
            department VARCHAR(100),
            salary DECIMAL(10,2),
            hire_date DATE,
            manager_id INTEGER,
            is_active {db.get_boolean_type()}
        )
    """)

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for _ in range(batch_start, batch_end):
            # Randomly NULL out fields that shouldn't be NULL
            rows.append((
                fake.first_name() if random.random() > 0.1 else None,
                fake.last_name() if random.random() > 0.1 else None,
                fake.email() if random.random() > 0.15 else None,
                fake.job()[:100] if random.random() > 0.2 else None,
                round(random.uniform(30000, 150000), 2)
                if random.random() > 0.25
                else None,
                fake.date_between(start_date="-10y", end_date="today")
                if random.random() > 0.1
                else None,
                random.randint(1, 100) if random.random() > 0.3 else None,
                random.choice([True, False]) if random.random() > 0.2 else None,
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}employees_nulls
            (first_name, last_name, email, department, salary, hire_date,
             manager_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_05_duplicate_records(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 5: Duplicate records (no unique constraints).

    Same business entities stored multiple times with no way to
    prevent or detect duplicates.
    """
    prefix = db.get_table_prefix()
    auto_inc = db.get_auto_increment_syntax()

    db.execute(f"""
        CREATE TABLE {prefix}users_duplicates (
            row_id {auto_inc} PRIMARY KEY,
            user_id INTEGER,
            username VARCHAR(100),
            email VARCHAR(255),
            phone VARCHAR(50),
            created_at TIMESTAMP
        )
    """)

    # Generate base users
    base_users = []
    for i in range(num_rows // 3):  # Base set is 1/3 of total
        base_users.append({
            "user_id": i + 1,
            "username": fake.user_name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "created_at": fake.date_time_between(start_date="-2y", end_date="now"),
        })

    batch_size = 1000
    rows = []

    # Insert base users plus duplicates
    for user in base_users:
        # Add the original
        rows.append((
            user["user_id"],
            user["username"],
            user["email"],
            user["phone"],
            user["created_at"],
        ))
        # Add 1-3 duplicates for ~50% of users
        if random.random() < 0.5:
            for _ in range(random.randint(1, 3)):
                rows.append((
                    user["user_id"],
                    user["username"],
                    user["email"],
                    user["phone"],
                    user["created_at"],
                ))

        if len(rows) >= batch_size:
            db.executemany(
                f"""
                INSERT INTO {prefix}users_duplicates
                (user_id, username, email, phone, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                rows,
            )
            rows = []

    if rows:
        db.executemany(
            f"""
            INSERT INTO {prefix}users_duplicates
            (user_id, username, email, phone, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_06_inconsistent_dates(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 6: Inconsistent date formats in string columns.

    Dates stored as strings in many different formats, making
    parsing, sorting, and comparison extremely difficult.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}events_bad_dates (
            event_id INTEGER,
            event_name VARCHAR(200),
            start_date VARCHAR(50),
            end_date VARCHAR(50),
            registration_deadline VARCHAR(50)
        )
    """)

    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%Y%m%d",
        "%d.%m.%Y",
    ]

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            start = fake.date_between(start_date="-1y", end_date="+1y")
            end = start + timedelta(days=random.randint(1, 30))
            deadline = start - timedelta(days=random.randint(7, 60))

            rows.append((
                i + 1,
                fake.catch_phrase(),
                start.strftime(random.choice(date_formats)),
                end.strftime(random.choice(date_formats)),
                deadline.strftime(random.choice(date_formats)),
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}events_bad_dates
            (event_id, event_name, start_date, end_date, registration_deadline)
            VALUES (%s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_07_inconsistent_casing(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 7: Inconsistent string casing (names, emails).

    Same data stored with different casing, causing join failures
    and deduplication issues.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}contacts_bad_casing (
            contact_id INTEGER,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(255),
            company VARCHAR(200),
            country VARCHAR(100)
        )
    """)

    def randomize_case(s: str) -> str:
        """Apply random casing to a string."""
        case_type = random.choice(["lower", "upper", "title", "mixed", "original"])
        if case_type == "lower":
            return s.lower()
        elif case_type == "upper":
            return s.upper()
        elif case_type == "title":
            return s.title()
        elif case_type == "mixed":
            return "".join(
                c.upper() if random.random() > 0.5 else c.lower() for c in s
            )
        return s

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            rows.append((
                i + 1,
                randomize_case(fake.first_name()),
                randomize_case(fake.last_name()),
                randomize_case(fake.email()),
                randomize_case(fake.company()),
                randomize_case(fake.country()),
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}contacts_bad_casing
            (contact_id, first_name, last_name, email, company, country)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_08_whitespace_issues(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 8: Leading/trailing whitespace in data.

    Fields contain invisible whitespace that breaks joins,
    lookups, and equality comparisons.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}inventory_whitespace (
            sku VARCHAR(100),
            product_name VARCHAR(200),
            category VARCHAR(100),
            supplier VARCHAR(200),
            warehouse_location VARCHAR(50)
        )
    """)

    def add_random_whitespace(s: str) -> str:
        """Add random leading/trailing whitespace."""
        whitespace_chars = [" ", "  ", "   ", "\t", " \t", "\n", " \n "]
        result = s
        if random.random() < 0.4:  # 40% chance of leading whitespace
            result = random.choice(whitespace_chars) + result
        if random.random() < 0.4:  # 40% chance of trailing whitespace
            result = result + random.choice(whitespace_chars)
        return result

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            rows.append((
                add_random_whitespace(f"SKU-{i + 1:06d}"),
                add_random_whitespace(fake.catch_phrase()[:200]),
                add_random_whitespace(
                    random.choice(
                        ["Electronics", "Clothing", "Food", "Furniture", "Tools"]
                    )
                ),
                add_random_whitespace(fake.company()[:200]),
                add_random_whitespace(f"W{random.randint(1, 10)}-R{random.randint(1, 50)}-S{random.randint(1, 100)}"),
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}inventory_whitespace
            (sku, product_name, category, supplier, warehouse_location)
            VALUES (%s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_09_invalid_emails(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 9: Invalid email formats.

    Email field contains values that aren't valid emails,
    causing delivery failures and data quality issues.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}subscribers_bad_emails (
            subscriber_id INTEGER,
            name VARCHAR(200),
            email VARCHAR(255),
            subscribed_at TIMESTAMP
        )
    """)

    def generate_bad_email() -> str:
        """Generate an invalid or malformed email."""
        bad_patterns = [
            lambda: fake.user_name(),  # No @ or domain
            lambda: f"{fake.user_name()}@",  # No domain
            lambda: f"@{fake.domain_name()}",  # No local part
            lambda: f"{fake.user_name()}@@{fake.domain_name()}",  # Double @
            lambda: f"{fake.user_name()} @{fake.domain_name()}",  # Space
            lambda: f"{fake.user_name()}@{fake.word()}",  # No TLD
            lambda: f"{fake.user_name()}@.{fake.domain_name()}",  # Leading dot
            lambda: f".{fake.user_name()}@{fake.domain_name()}",  # Leading dot local
            lambda: f"{fake.user_name()}@{fake.domain_name()}.",  # Trailing dot
            lambda: "N/A",
            lambda: "none",
            lambda: "-",
            lambda: "",
            lambda: fake.phone_number(),  # Phone number in email field
        ]
        return random.choice(bad_patterns)()

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            # 30% bad emails
            email = generate_bad_email() if random.random() < 0.3 else fake.email()
            rows.append((
                i + 1,
                fake.name(),
                email,
                fake.date_time_between(start_date="-2y", end_date="now"),
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}subscribers_bad_emails
            (subscriber_id, name, email, subscribed_at)
            VALUES (%s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_10_out_of_range(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 10: Out-of-range values (negative prices, future dates).

    Data contains values that are technically valid for the data type
    but make no business sense.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}sales_bad_values (
            sale_id INTEGER,
            product_name VARCHAR(200),
            unit_price DECIMAL(10,2),
            quantity INTEGER,
            discount_percent DECIMAL(5,2),
            sale_date DATE,
            customer_age INTEGER,
            rating DECIMAL(3,1)
        )
    """)

    batch_size = 1000
    now = datetime.now(timezone.utc).date()

    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            # Occasionally insert bad values
            if random.random() < 0.2:  # 20% bad data
                bad_type = random.choice([
                    "negative_price",
                    "negative_quantity",
                    "huge_discount",
                    "future_date",
                    "impossible_age",
                    "bad_rating",
                ])

                if bad_type == "negative_price":
                    price = -round(random.uniform(1, 100), 2)
                    quantity = random.randint(1, 10)
                    discount = round(random.uniform(0, 30), 2)
                    date = fake.date_between(start_date="-1y", end_date="today")
                    age = random.randint(18, 80)
                    rating = round(random.uniform(1, 5), 1)
                elif bad_type == "negative_quantity":
                    price = round(random.uniform(10, 500), 2)
                    quantity = -random.randint(1, 100)
                    discount = round(random.uniform(0, 30), 2)
                    date = fake.date_between(start_date="-1y", end_date="today")
                    age = random.randint(18, 80)
                    rating = round(random.uniform(1, 5), 1)
                elif bad_type == "huge_discount":
                    price = round(random.uniform(10, 500), 2)
                    quantity = random.randint(1, 10)
                    discount = round(random.uniform(100, 500), 2)  # > 100%
                    date = fake.date_between(start_date="-1y", end_date="today")
                    age = random.randint(18, 80)
                    rating = round(random.uniform(1, 5), 1)
                elif bad_type == "future_date":
                    price = round(random.uniform(10, 500), 2)
                    quantity = random.randint(1, 10)
                    discount = round(random.uniform(0, 30), 2)
                    date = now + timedelta(days=random.randint(1, 365))
                    age = random.randint(18, 80)
                    rating = round(random.uniform(1, 5), 1)
                elif bad_type == "impossible_age":
                    price = round(random.uniform(10, 500), 2)
                    quantity = random.randint(1, 10)
                    discount = round(random.uniform(0, 30), 2)
                    date = fake.date_between(start_date="-1y", end_date="today")
                    age = random.choice([-5, 0, 150, 999])
                    rating = round(random.uniform(1, 5), 1)
                else:  # bad_rating
                    price = round(random.uniform(10, 500), 2)
                    quantity = random.randint(1, 10)
                    discount = round(random.uniform(0, 30), 2)
                    date = fake.date_between(start_date="-1y", end_date="today")
                    age = random.randint(18, 80)
                    rating = random.choice([-1.0, 0.0, 6.0, 10.0])
            else:
                price = round(random.uniform(10, 500), 2)
                quantity = random.randint(1, 10)
                discount = round(random.uniform(0, 30), 2)
                date = fake.date_between(start_date="-1y", end_date="today")
                age = random.randint(18, 80)
                rating = round(random.uniform(1, 5), 1)

            rows.append((
                i + 1,
                fake.catch_phrase()[:200],
                price,
                quantity,
                discount,
                date,
                age,
                rating,
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}sales_bad_values
            (sale_id, product_name, unit_price, quantity, discount_percent,
             sale_date, customer_age, rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_11_csv_in_columns(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 11: Comma-separated values in columns (1NF violation).

    Multi-valued attributes stored as comma-separated strings,
    violating First Normal Form and making queries painful.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}articles_csv_tags (
            article_id INTEGER,
            title VARCHAR(300),
            author VARCHAR(200),
            tags VARCHAR(500),
            categories VARCHAR(500),
            related_ids VARCHAR(200)
        )
    """)

    all_tags = [
        "python",
        "javascript",
        "sql",
        "database",
        "web",
        "api",
        "security",
        "cloud",
        "devops",
        "testing",
        "frontend",
        "backend",
        "mobile",
        "ai",
        "ml",
    ]
    all_categories = [
        "Tutorial",
        "News",
        "Opinion",
        "Review",
        "Guide",
        "Reference",
    ]

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            # Create comma-separated tags (1-7 tags)
            tags = ",".join(random.sample(all_tags, random.randint(1, 7)))
            # Create comma-separated categories (1-3 categories)
            cats = ",".join(random.sample(all_categories, random.randint(1, 3)))
            # Create comma-separated related IDs
            related = ",".join(
                str(random.randint(1, num_rows)) for _ in range(random.randint(0, 5))
            )

            rows.append((
                i + 1,
                fake.sentence(nb_words=8)[:300],
                fake.name(),
                tags,
                cats,
                related,
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}articles_csv_tags
            (article_id, title, author, tags, categories, related_ids)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_12_encoding_issues(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 12: Mixed encodings and special characters.

    Data contains special characters, unicode, and potentially
    corrupted encoding that causes display and processing issues.
    """
    prefix = db.get_table_prefix()

    db.execute(f"""
        CREATE TABLE {prefix}international_data (
            record_id INTEGER,
            customer_name VARCHAR(300),
            address VARCHAR(500),
            notes VARCHAR(1000)
        )
    """)

    # Various problematic strings
    special_chars = [
        "Café résumé naïve",
        "日本語テスト",
        "Тест кириллицы",
        "مرحبا بالعالم",
        "שלום עולם",
        "🎉 Party 🎊 Time 🎈",
        "Line1\nLine2\nLine3",
        'Quote "test" here',
        "Tab\there\ttoo",
        "NULL",
        "null",
        "<script>alert('xss')</script>",
        "O'Brien's café",
        "50% off — limited time!",
        "Price: €100 or £80",
        "Ñoño",
        "\x00 null byte",  # Null byte
        "末末末",
        "Beyoncé",
    ]

    fake_locales = Faker(["en_US", "de_DE", "fr_FR", "ja_JP", "zh_CN", "ru_RU"])

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            if random.random() < 0.3:  # 30% special chars
                name = random.choice(special_chars)
                address = random.choice(special_chars)
                notes = " | ".join(random.sample(special_chars, 3))
            else:
                name = fake_locales.name()
                address = fake_locales.address().replace("\n", ", ")
                notes = fake_locales.text(max_nb_chars=200)

            rows.append((
                i + 1,
                name[:300],
                address[:500],
                notes[:1000],
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}international_data
            (record_id, customer_name, address, notes)
            VALUES (%s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_13_god_table(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 13: God table with excessive denormalization.

    One massive table with 30+ columns containing everything,
    causing massive data redundancy and update anomalies.
    """
    prefix = db.get_table_prefix()

    # Create a massively denormalized table
    db.execute(f"""
        CREATE TABLE {prefix}god_table (
            id INTEGER,
            -- Customer info (repeated for every order)
            customer_id INTEGER,
            customer_first_name VARCHAR(100),
            customer_last_name VARCHAR(100),
            customer_email VARCHAR(255),
            customer_phone VARCHAR(50),
            customer_address_line1 VARCHAR(200),
            customer_address_line2 VARCHAR(200),
            customer_city VARCHAR(100),
            customer_state VARCHAR(50),
            customer_zip VARCHAR(20),
            customer_country VARCHAR(100),
            customer_created_at TIMESTAMP,
            -- Order info
            order_id INTEGER,
            order_date TIMESTAMP,
            order_status VARCHAR(50),
            order_total DECIMAL(10,2),
            order_shipping_cost DECIMAL(10,2),
            order_tax DECIMAL(10,2),
            -- Product info (repeated for every line item)
            product_id INTEGER,
            product_name VARCHAR(200),
            product_description VARCHAR(1000),
            product_category VARCHAR(100),
            product_subcategory VARCHAR(100),
            product_brand VARCHAR(100),
            product_unit_price DECIMAL(10,2),
            product_cost DECIMAL(10,2),
            -- Line item
            quantity INTEGER,
            line_total DECIMAL(10,2),
            -- Shipping info
            shipping_carrier VARCHAR(100),
            shipping_tracking VARCHAR(100),
            shipping_method VARCHAR(50),
            estimated_delivery DATE,
            actual_delivery DATE
        )
    """)

    # Generate denormalized data
    customers = []
    for i in range(100):  # 100 unique customers
        customers.append({
            "id": i + 1,
            "first": fake.first_name(),
            "last": fake.last_name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "addr1": fake.street_address(),
            "addr2": fake.secondary_address() if random.random() > 0.7 else "",
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.zipcode(),
            "country": "USA",
            "created": fake.date_time_between(start_date="-3y", end_date="-1y"),
        })

    products = []
    for i in range(50):  # 50 unique products
        products.append({
            "id": i + 1,
            "name": fake.catch_phrase()[:200],
            "desc": fake.text(max_nb_chars=500),
            "cat": random.choice(
                ["Electronics", "Clothing", "Home", "Sports", "Books"]
            ),
            "subcat": fake.word(),
            "brand": fake.company()[:100],
            "price": round(random.uniform(10, 500), 2),
            "cost": round(random.uniform(5, 250), 2),
        })

    batch_size = 1000
    rows = []
    for i in range(num_rows):
        cust = random.choice(customers)
        prod = random.choice(products)
        qty = random.randint(1, 5)
        order_date = fake.date_time_between(start_date="-1y", end_date="now")

        rows.append((
            i + 1,
            cust["id"],
            cust["first"],
            cust["last"],
            cust["email"],
            cust["phone"],
            cust["addr1"],
            cust["addr2"],
            cust["city"],
            cust["state"],
            cust["zip"],
            cust["country"],
            cust["created"],
            random.randint(10000, 99999),
            order_date,
            random.choice(["pending", "shipped", "delivered", "returned"]),
            round(prod["price"] * qty * 1.1, 2),  # total with tax estimate
            round(random.uniform(5, 20), 2),
            round(prod["price"] * qty * 0.08, 2),
            prod["id"],
            prod["name"],
            prod["desc"],
            prod["cat"],
            prod["subcat"],
            prod["brand"],
            prod["price"],
            prod["cost"],
            qty,
            round(prod["price"] * qty, 2),
            random.choice(["UPS", "FedEx", "USPS", "DHL"]),
            fake.uuid4()[:20],
            random.choice(["standard", "express", "overnight"]),
            (order_date + timedelta(days=random.randint(3, 14))).date(),
            (order_date + timedelta(days=random.randint(3, 20))).date()
            if random.random() > 0.3
            else None,
        ))

        if len(rows) >= batch_size:
            db.executemany(
                f"""
                INSERT INTO {prefix}god_table
                (id, customer_id, customer_first_name, customer_last_name,
                 customer_email, customer_phone, customer_address_line1,
                 customer_address_line2, customer_city, customer_state,
                 customer_zip, customer_country, customer_created_at,
                 order_id, order_date, order_status, order_total,
                 order_shipping_cost, order_tax, product_id, product_name,
                 product_description, product_category, product_subcategory,
                 product_brand, product_unit_price, product_cost, quantity,
                 line_total, shipping_carrier, shipping_tracking,
                 shipping_method, estimated_delivery, actual_delivery)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
            rows = []

    if rows:
        db.executemany(
            f"""
            INSERT INTO {prefix}god_table
            (id, customer_id, customer_first_name, customer_last_name,
             customer_email, customer_phone, customer_address_line1,
             customer_address_line2, customer_city, customer_state,
             customer_zip, customer_country, customer_created_at,
             order_id, order_date, order_status, order_total,
             order_shipping_cost, order_tax, product_id, product_name,
             product_description, product_category, product_subcategory,
             product_brand, product_unit_price, product_cost, quantity,
             line_total, shipping_carrier, shipping_tracking,
             shipping_method, estimated_delivery, actual_delivery)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_14_missing_indexes(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 14: Missing indexes on frequently queried columns.

    Large table with no indexes on columns commonly used in
    WHERE, JOIN, and ORDER BY clauses.
    """
    prefix = db.get_table_prefix()
    auto_inc = db.get_auto_increment_syntax()

    # Create table explicitly WITHOUT indexes on foreign keys and filter columns
    db.execute(f"""
        CREATE TABLE {prefix}audit_log_no_index (
            log_id {auto_inc} PRIMARY KEY,
            user_id INTEGER,
            action_type VARCHAR(50),
            resource_type VARCHAR(50),
            resource_id INTEGER,
            ip_address VARCHAR(45),
            user_agent VARCHAR(500),
            created_at TIMESTAMP,
            session_id VARCHAR(100),
            status VARCHAR(20)
        )
    """)

    action_types = ["VIEW", "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "EXPORT"]
    resource_types = ["user", "order", "product", "report", "setting", "document"]
    statuses = ["success", "failure", "pending", "timeout"]

    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for _ in range(batch_start, batch_end):
            rows.append((
                random.randint(1, 10000),
                random.choice(action_types),
                random.choice(resource_types),
                random.randint(1, 100000),
                fake.ipv4(),
                fake.user_agent()[:500],
                fake.date_time_between(start_date="-90d", end_date="now"),
                fake.uuid4(),
                random.choice(statuses),
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}audit_log_no_index
            (user_id, action_type, resource_type, resource_id, ip_address,
             user_agent, created_at, session_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


def problem_15_type_coercion(db: DatabaseAdapter, num_rows: int) -> None:
    """
    Problem 15: Implicit type coercion traps in data.

    Numeric IDs stored as strings with leading zeros, causing
    join failures when compared to integer columns.
    """
    prefix = db.get_table_prefix()

    # Table 1: IDs as integers
    db.execute(f"""
        CREATE TABLE {prefix}accounts_int_id (
            account_id INTEGER PRIMARY KEY,
            account_name VARCHAR(200),
            balance DECIMAL(15,2)
        )
    """)

    # Table 2: IDs as strings (with leading zeros!)
    db.execute(f"""
        CREATE TABLE {prefix}transactions_str_id (
            txn_id INTEGER,
            account_id VARCHAR(20),
            amount DECIMAL(10,2),
            txn_date DATE
        )
    """)

    # Insert accounts with integer IDs
    accounts = [(i + 1, fake.company()[:200], round(random.uniform(100, 100000), 2)) for i in range(1000)]
    db.executemany(
        f"INSERT INTO {prefix}accounts_int_id (account_id, account_name, balance) VALUES (%s, %s, %s)",
        accounts,
    )

    # Insert transactions with STRING IDs (some with leading zeros)
    batch_size = 1000
    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        rows = []
        for i in range(batch_start, batch_end):
            acct_id = random.randint(1, 1000)
            # 40% chance of leading zeros
            if random.random() < 0.4:
                acct_id_str = f"{acct_id:010d}"  # Pad to 10 digits
            else:
                acct_id_str = str(acct_id)

            rows.append((
                i + 1,
                acct_id_str,
                round(random.uniform(-1000, 1000), 2),
                fake.date_between(start_date="-1y", end_date="today"),
            ))
        db.executemany(
            f"""
            INSERT INTO {prefix}transactions_str_id
            (txn_id, account_id, amount, txn_date)
            VALUES (%s, %s, %s, %s)
            """,
            rows,
        )
    db.commit()


# =============================================================================
# Diagnostic Queries
# =============================================================================

DIAGNOSTIC_QUERIES = {
    "problem_01": {
        "name": "Tables without Primary Keys",
        "description": "Find duplicate rows that can't be uniquely identified",
        "query": """
-- Find exact duplicate rows
SELECT customer_id, first_name, last_name, email, COUNT(*) as count
FROM {prefix}customers_no_pk
GROUP BY customer_id, first_name, last_name, email
HAVING COUNT(*) > 1
ORDER BY count DESC
LIMIT 20;
""",
    },
    "problem_02": {
        "name": "Orphaned Foreign Key Records",
        "description": "Find orders referencing non-existent customers/products",
        "query": """
-- Find orders with non-existent customers
SELECT COUNT(*) as orphaned_customer_orders
FROM {prefix}orders_no_fk o
LEFT JOIN {prefix}customers_no_pk c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Find orders with non-existent products
SELECT COUNT(*) as orphaned_product_orders
FROM {prefix}orders_no_fk o
LEFT JOIN {prefix}products p ON o.product_id = p.product_id
WHERE p.product_id IS NULL;
""",
    },
    "problem_03": {
        "name": "Wrong Data Types",
        "description": "Identify strings that should be dates/numbers",
        "query": """
-- Show the variety of date formats stored as strings
SELECT transaction_date, COUNT(*) as count
FROM {prefix}transactions_bad_types
GROUP BY transaction_date
ORDER BY count DESC
LIMIT 20;

-- Show amount formats
SELECT amount, COUNT(*) as count
FROM {prefix}transactions_bad_types
GROUP BY amount
ORDER BY count DESC
LIMIT 20;
""",
    },
    "problem_04": {
        "name": "NULL Values in Critical Fields",
        "description": "Count NULLs in fields that shouldn't be NULL",
        "query": """
SELECT
    COUNT(*) as total_rows,
    SUM(CASE WHEN first_name IS NULL THEN 1 ELSE 0 END) as null_first_name,
    SUM(CASE WHEN last_name IS NULL THEN 1 ELSE 0 END) as null_last_name,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as null_email,
    SUM(CASE WHEN salary IS NULL THEN 1 ELSE 0 END) as null_salary,
    SUM(CASE WHEN hire_date IS NULL THEN 1 ELSE 0 END) as null_hire_date
FROM {prefix}employees_nulls;
""",
    },
    "problem_05": {
        "name": "Duplicate Records",
        "description": "Find users that appear multiple times",
        "query": """
SELECT user_id, username, email, COUNT(*) as occurrences
FROM {prefix}users_duplicates
GROUP BY user_id, username, email
HAVING COUNT(*) > 1
ORDER BY occurrences DESC
LIMIT 20;
""",
    },
    "problem_06": {
        "name": "Inconsistent Date Formats",
        "description": "Show the chaos of date format variations",
        "query": """
SELECT start_date, COUNT(*) as count
FROM {prefix}events_bad_dates
GROUP BY start_date
ORDER BY count DESC
LIMIT 30;
""",
    },
    "problem_07": {
        "name": "Inconsistent String Casing",
        "description": "Find same value with different casing",
        "query": """
SELECT LOWER(country) as normalized_country,
       COUNT(DISTINCT country) as case_variations,
       COUNT(*) as total_records
FROM {prefix}contacts_bad_casing
GROUP BY LOWER(country)
HAVING COUNT(DISTINCT country) > 1
ORDER BY case_variations DESC;
""",
    },
    "problem_08": {
        "name": "Whitespace Issues",
        "description": "Find values with leading/trailing whitespace",
        "query": """
SELECT sku,
       LENGTH(sku) as length_with_whitespace,
       LENGTH(TRIM(sku)) as length_trimmed,
       LENGTH(sku) - LENGTH(TRIM(sku)) as whitespace_chars
FROM {prefix}inventory_whitespace
WHERE LENGTH(sku) != LENGTH(TRIM(sku))
LIMIT 20;
""",
    },
    "problem_09": {
        "name": "Invalid Email Formats",
        "description": "Find emails that don't match basic patterns",
        "query": """
-- Emails without @ symbol
SELECT email, COUNT(*) as count
FROM {prefix}subscribers_bad_emails
WHERE email NOT LIKE '%@%' OR email = '' OR email IS NULL
GROUP BY email
ORDER BY count DESC
LIMIT 20;
""",
    },
    "problem_10": {
        "name": "Out of Range Values",
        "description": "Find business-logic violations",
        "query": """
SELECT
    SUM(CASE WHEN unit_price < 0 THEN 1 ELSE 0 END) as negative_prices,
    SUM(CASE WHEN quantity < 0 THEN 1 ELSE 0 END) as negative_quantities,
    SUM(CASE WHEN discount_percent > 100 THEN 1 ELSE 0 END) as impossible_discounts,
    SUM(CASE WHEN sale_date > CURRENT_DATE THEN 1 ELSE 0 END) as future_dates,
    SUM(CASE WHEN customer_age < 0 OR customer_age > 120 THEN 1 ELSE 0 END) as impossible_ages,
    SUM(CASE WHEN rating < 1 OR rating > 5 THEN 1 ELSE 0 END) as invalid_ratings
FROM {prefix}sales_bad_values;
""",
    },
    "problem_11": {
        "name": "CSV Values in Columns (1NF Violation)",
        "description": "Show multi-valued fields that should be separate tables",
        "query": """
-- Count articles by number of tags
SELECT
    (LENGTH(tags) - LENGTH(REPLACE(tags, ',', '')) + 1) as num_tags,
    COUNT(*) as article_count
FROM {prefix}articles_csv_tags
WHERE tags IS NOT NULL AND tags != ''
GROUP BY (LENGTH(tags) - LENGTH(REPLACE(tags, ',', '')) + 1)
ORDER BY num_tags;
""",
    },
    "problem_12": {
        "name": "Encoding and Special Characters",
        "description": "Find records with special characters",
        "query": """
SELECT customer_name, LENGTH(customer_name) as length
FROM {prefix}international_data
WHERE customer_name LIKE '%�%'
   OR customer_name LIKE '%\\n%'
   OR customer_name LIKE '%\\t%'
LIMIT 20;
""",
    },
    "problem_13": {
        "name": "God Table Redundancy",
        "description": "Show data redundancy in denormalized table",
        "query": """
-- Same customer info repeated many times
SELECT customer_id, customer_email,
       COUNT(*) as times_repeated,
       COUNT(DISTINCT order_id) as unique_orders
FROM {prefix}god_table
GROUP BY customer_id, customer_email
ORDER BY times_repeated DESC
LIMIT 10;
""",
    },
    "problem_14": {
        "name": "Missing Indexes Impact",
        "description": "Show query that would benefit from indexes",
        "query": """
-- This query scans full table without indexes
-- In a real workshop, compare EXPLAIN plans before/after adding index
SELECT user_id, action_type, COUNT(*) as count
FROM {prefix}audit_log_no_index
WHERE created_at > CURRENT_DATE - INTERVAL '7 days'
  AND action_type = 'LOGIN'
  AND status = 'success'
GROUP BY user_id, action_type
ORDER BY count DESC
LIMIT 10;
""",
    },
    "problem_15": {
        "name": "Type Coercion Join Failures",
        "description": "Show how string/int ID mismatch breaks joins",
        "query": """
-- This join may fail or produce wrong results due to type mismatch
SELECT
    a.account_id as int_id,
    t.account_id as str_id,
    a.account_name,
    t.amount
FROM {prefix}accounts_int_id a
JOIN {prefix}transactions_str_id t
    ON a.account_id = CAST(t.account_id AS INTEGER)
WHERE t.account_id LIKE '0%'
LIMIT 10;

-- Count of transactions that won't join properly with direct comparison
SELECT COUNT(*) as problematic_transactions
FROM {prefix}transactions_str_id
WHERE account_id LIKE '0%';
""",
    },
}


def show_diagnostics(db_type: DBType) -> None:
    """Display diagnostic queries for all problems."""
    prefix = "bdw_" if db_type == "mysql" else f"{SCHEMA_NAME}."

    console.print()
    console.print(
        Panel(
            "[bold cyan]Bad Data Workshop - Diagnostic Queries[/bold cyan]\n\n"
            "Run these queries to discover and analyze the data problems.",
            border_style="cyan",
        )
    )

    for problem_id, info in DIAGNOSTIC_QUERIES.items():
        console.print()
        console.print(f"[bold yellow]═══ {info['name']} ═══[/bold yellow]")
        console.print(f"[dim]{info['description']}[/dim]")
        console.print()

        # Replace prefix placeholder
        query = info["query"].replace("{prefix}", prefix)
        console.print(Panel(query.strip(), border_style="dim"))


# =============================================================================
# Main Setup and Teardown
# =============================================================================


def setup_workshop(config: DBConfig, scale: str = "small") -> None:
    """Set up the workshop database with all problems."""
    # Scale determines row counts
    scales = {
        "tiny": 100,  # For quick testing
        "small": 10_000,  # ~50MB
        "medium": 100_000,  # ~500MB
        "large": 500_000,  # ~2.5GB
        "xlarge": 1_000_000,  # ~5GB
    }
    base_rows = scales.get(scale, 10_000)

    problems = [
        ("Problem 1: No Primary Keys", problem_01_no_primary_key, base_rows),
        ("Problem 2: Missing Foreign Keys", problem_02_missing_foreign_keys, base_rows),
        ("Problem 3: Wrong Data Types", problem_03_wrong_data_types, base_rows),
        ("Problem 4: Missing NOT NULL", problem_04_missing_not_null, base_rows),
        ("Problem 5: Duplicate Records", problem_05_duplicate_records, base_rows),
        ("Problem 6: Inconsistent Dates", problem_06_inconsistent_dates, base_rows),
        ("Problem 7: Inconsistent Casing", problem_07_inconsistent_casing, base_rows),
        ("Problem 8: Whitespace Issues", problem_08_whitespace_issues, base_rows),
        ("Problem 9: Invalid Emails", problem_09_invalid_emails, base_rows),
        ("Problem 10: Out of Range Values", problem_10_out_of_range, base_rows),
        ("Problem 11: CSV in Columns", problem_11_csv_in_columns, base_rows),
        ("Problem 12: Encoding Issues", problem_12_encoding_issues, base_rows),
        ("Problem 13: God Table", problem_13_god_table, base_rows * 2),
        ("Problem 14: Missing Indexes", problem_14_missing_indexes, base_rows * 5),
        ("Problem 15: Type Coercion", problem_15_type_coercion, base_rows),
    ]

    db = get_adapter(config)

    try:
        console.print()
        console.print(
            Panel(
                f"[bold green]Bad Data Workshop Setup[/bold green]\n\n"
                f"Database: [cyan]{config.db_type}[/cyan]\n"
                f"Host: [cyan]{config.host}:{config.port}[/cyan]\n"
                f"Scale: [cyan]{scale}[/cyan] ({base_rows:,} base rows)",
                border_style="green",
            )
        )

        console.print("\n[cyan]Connecting to database...[/cyan]")
        db.connect()
        console.print("[green]✓ Connected[/green]")

        console.print("[cyan]Creating schema...[/cyan]")
        db.create_schema()
        console.print("[green]✓ Schema created[/green]")

        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            overall = progress.add_task(
                "[cyan]Setting up problems...", total=len(problems)
            )

            for name, func, rows in problems:
                progress.update(overall, description=f"[cyan]{name}...")
                func(db, rows)
                progress.advance(overall)

        console.print()
        console.print(
            Panel(
                "[bold green]✓ Workshop setup complete![/bold green]\n\n"
                f"Created {len(problems)} problem tables.\n"
                f"Run with [cyan]diagnose[/cyan] command to see diagnostic queries.",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}")
        raise
    finally:
        db.close()


def teardown_workshop(config: DBConfig) -> None:
    """Remove all workshop data and schema."""
    db = get_adapter(config)

    try:
        console.print()
        console.print(
            Panel(
                f"[bold red]Bad Data Workshop Teardown[/bold red]\n\n"
                f"Database: [cyan]{config.db_type}[/cyan]\n"
                f"Host: [cyan]{config.host}:{config.port}[/cyan]",
                border_style="red",
            )
        )

        console.print("\n[cyan]Connecting to database...[/cyan]")
        db.connect()
        console.print("[green]✓ Connected[/green]")

        console.print("[red]Dropping schema and all objects...[/red]")
        db.drop_schema()
        console.print("[green]✓ Schema dropped[/green]")

        console.print()
        console.print(
            Panel(
                "[bold green]✓ Teardown complete![/bold green]\n\n"
                "All workshop data has been removed.",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}")
        raise
    finally:
        db.close()


# =============================================================================
# CLI
# =============================================================================


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Bad Data Workshop Generator - Create databases full of "
        "intentional data quality problems for training.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup workshop database (PostgreSQL)
  uv run --script bad_data_workshop.py setup \\
      --db-type postgres --host localhost --port 5432 \\
      --database workshop --user postgres --password secret

  # Setup with large dataset (~2.5GB)
  uv run --script bad_data_workshop.py setup \\
      --db-type postgres --host localhost --database workshop \\
      --user postgres --password secret --scale large

  # Teardown (complete cleanup)
  uv run --script bad_data_workshop.py teardown \\
      --db-type postgres --host localhost --database workshop \\
      --user postgres --password secret

  # Show diagnostic queries
  uv run --script bad_data_workshop.py diagnose --db-type postgres
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up workshop database")
    setup_parser.add_argument(
        "--db-type",
        choices=["postgres", "mysql", "redshift"],
        required=True,
        help="Database type",
    )
    setup_parser.add_argument("--host", required=True, help="Database host")
    setup_parser.add_argument(
        "--port", type=int, default=None, help="Database port (default: auto)"
    )
    setup_parser.add_argument("--database", required=True, help="Database name")
    setup_parser.add_argument("--user", required=True, help="Database user")
    setup_parser.add_argument("--password", required=True, help="Database password")
    setup_parser.add_argument(
        "--scale",
        choices=["tiny", "small", "medium", "large", "xlarge"],
        default="small",
        help="Data scale (default: small, ~50MB)",
    )

    # Teardown command
    teardown_parser = subparsers.add_parser(
        "teardown", help="Remove all workshop data"
    )
    teardown_parser.add_argument(
        "--db-type",
        choices=["postgres", "mysql", "redshift"],
        required=True,
        help="Database type",
    )
    teardown_parser.add_argument("--host", required=True, help="Database host")
    teardown_parser.add_argument(
        "--port", type=int, default=None, help="Database port"
    )
    teardown_parser.add_argument("--database", required=True, help="Database name")
    teardown_parser.add_argument("--user", required=True, help="Database user")
    teardown_parser.add_argument("--password", required=True, help="Database password")

    # Diagnose command
    diagnose_parser = subparsers.add_parser(
        "diagnose", help="Show diagnostic queries"
    )
    diagnose_parser.add_argument(
        "--db-type",
        choices=["postgres", "mysql", "redshift"],
        required=True,
        help="Database type (affects query syntax)",
    )

    return parser


def get_default_port(db_type: DBType) -> int:
    """Get default port for database type."""
    defaults = {"postgres": 5432, "mysql": 3306, "redshift": 5439}
    return defaults[db_type]


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        if args.command == "diagnose":
            show_diagnostics(args.db_type)
            return 0

        port = args.port or get_default_port(args.db_type)

        config = DBConfig(
            db_type=args.db_type,
            host=args.host,
            port=port,
            database=args.database,
            user=args.user,
            password=args.password,
        )

        if args.command == "setup":
            setup_workshop(config, args.scale)
        elif args.command == "teardown":
            teardown_workshop(config)

        return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
