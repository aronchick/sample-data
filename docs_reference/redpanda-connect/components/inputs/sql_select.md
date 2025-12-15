# SQL Select Input Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/inputs/sql_select/

## Overview

The `sql_select` input component executes database queries and creates messages for each returned row. It automatically shuts down once rows are exhausted, enabling graceful pipeline termination.

## Basic Configuration

```yaml
input:
  sql_select:
    driver: ""        # Required
    dsn: ""           # Required
    table: ""         # Required
    columns: []       # Required
```

## Advanced Configuration

```yaml
input:
  sql_select:
    driver: ""
    dsn: ""
    table: ""
    columns: []
    where: ""
    args_mapping: ""
    prefix: ""
    suffix: ""
    init_statement: ""
    init_files: []
    conn_max_idle: 2
    conn_max_open: 0
    conn_max_idle_time: ""
    conn_max_life_time: ""
    auto_replay_nacks: true
```

## Supported Database Drivers

Nine drivers are available:
- **mysql** - MySQL and MariaDB
- **postgres** - PostgreSQL
- **clickhouse** - ClickHouse
- **mssql** - Microsoft SQL Server
- **sqlite** - SQLite
- **oracle** - Oracle Database
- **snowflake** - Snowflake
- **trino** - Trino
- **gocosmos** - Azure Cosmos DB

## Required Configuration Fields

### `driver` (string)
The database type to connect with.

### `dsn` (string)
Connection string containing authentication and database details.

### `table` (string)
Source table name.

### `columns` (array)
List of fields to retrieve. Supports wildcard syntax (`*`).

## Optional Configuration Fields

### Query Filtering

**`where`** (string)
WHERE clause with placeholder arguments.

**`args_mapping`** (string)
Bloblang expression to populate placeholder arguments.

```yaml
sql_select:
  driver: postgres
  dsn: postgres://user:pass@localhost:5432/db
  table: users
  columns: [id, name, email]
  where: "created_at > $1 AND status = $2"
  args_mapping: |
    root = [
      "2024-01-01",
      "active"
    ]
```

### Query Modification

**`prefix`** (string)
Text prepended before SELECT keyword.

**`suffix`** (string)
Text appended after query (e.g., ORDER BY, LIMIT).

### Connection Management

**`conn_max_idle`** (integer, default: 2)
Maximum idle connections in pool.

**`conn_max_open`** (integer, default: 0)
Maximum open connections (0 = unlimited).

**`conn_max_idle_time`** (string)
Duration before closing idle connections.

**`conn_max_life_time`** (string)
Maximum connection reuse duration.

### Initialization

**`init_statement`** (string)
SQL executed on first connection.

**`init_files`** (array)
File paths containing initialization SQL (requires v4.10.0+, supports glob patterns).

### Message Handling

**`auto_replay_nacks`** (boolean, default: true)
Controls rejection behavior for failed downstream processing.

## DSN Examples

```yaml
# PostgreSQL
dsn: postgres://user:pass@localhost:5432/database?sslmode=disable

# MySQL
dsn: user:password@tcp(localhost:3306)/database

# Oracle
dsn: oracle://user:pass@localhost:1521/service_name

# SQLite
dsn: file:/path/to/database.db

# ClickHouse
dsn: clickhouse://user:pass@localhost:9000/database

# Snowflake
dsn: user:pass@account/database/schema?warehouse=wh
```

## Usage Examples

### Basic Query

```yaml
input:
  sql_select:
    driver: postgres
    dsn: postgres://workshop:workshop123@localhost:5432/workshop
    table: customers
    columns: [id, name, email, created_at]
```

### Filtered Query with Arguments

```yaml
input:
  sql_select:
    driver: mysql
    dsn: workshop:workshop123@tcp(localhost:3306)/workshop
    table: orders
    columns: [order_id, customer_id, total, status]
    where: "status = ? AND total > ?"
    args_mapping: |
      root = ["pending", 100.00]
    suffix: "ORDER BY created_at DESC LIMIT 1000"
```

### With Initialization

```yaml
input:
  sql_select:
    driver: postgres
    dsn: postgres://user:pass@localhost:5432/db
    table: events
    columns: ["*"]
    init_statement: |
      SET search_path TO my_schema;
      SET statement_timeout = '30s';
```
