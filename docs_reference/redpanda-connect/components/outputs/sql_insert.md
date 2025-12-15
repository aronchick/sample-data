# SQL Insert Output Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/outputs/sql_insert/

## Overview

The `sql_insert` output component inserts a row into an SQL database for each message. Introduced in version 3.59.0, available in both Cloud and Self-Managed environments.

## Basic Configuration

```yaml
output:
  sql_insert:
    driver: ""         # Required
    dsn: ""            # Required
    table: ""          # Required
    columns: []        # Required
    args_mapping: ""   # Required
```

## Advanced Configuration

```yaml
output:
  sql_insert:
    driver: ""
    dsn: ""
    table: ""
    columns: []
    args_mapping: ""
    prefix: ""
    suffix: ""
    options: ""
    init_statement: ""
    init_files: []
    conn_max_idle: 2
    conn_max_open: 0
    conn_max_idle_time: ""
    conn_max_life_time: ""
    max_in_flight: 64
    batching:
      count: 0
      byte_size: 0
      period: ""
      check: ""
      processors: []
```

## Supported Database Drivers

- **mysql** - MySQL and MariaDB
- **postgres** - PostgreSQL
- **clickhouse** - ClickHouse
- **mssql** - Microsoft SQL Server
- **sqlite** - SQLite
- **oracle** - Oracle Database
- **snowflake** - Snowflake
- **trino** - Trino
- **gocosmos** - Azure Cosmos DB
- **spanner** - Google Cloud Spanner

## Required Configuration Fields

### `driver` (string)
Database type to connect with.

### `dsn` (string)
Connection string with database credentials and host details.

### `table` (string)
Target table name.

### `columns` (array)
List of columns to populate.

### `args_mapping` (string)
"A Bloblang mapping which should evaluate to an array of values matching in size to the number of columns specified."

## Connection Pooling Options

### `conn_max_idle` (integer, default: 2)
Maximum idle connections in pool.

### `conn_max_open` (integer, default: 0)
Maximum open connections (no limit if ≤ 0).

### `conn_max_idle_time` (string)
Duration before closing idle connections.

### `conn_max_life_time` (string)
Maximum connection reuse duration.

## Batching Configuration

"Allows you to configure a batching policy" with these parameters:

### `count` (integer, default: 0)
Flush after N messages.

### `byte_size` (integer, default: 0)
Flush after accumulating X bytes.

### `period` (string)
Time-based flush interval.

### `check` (string)
Bloblang query determining batch completion.

### `processors` (array)
Post-flush aggregation/archival operations.

## Advanced Features

### `max_in_flight` (integer, default: 64)
Parallel insert limit.

### `init_statement` / `init_files`
SQL execution on first connection.

### `prefix` / `suffix`
Query customization (e.g., conflict handling).

### `options`
Keywords like DELAYED or IGNORE inserted before INTO clause.

## Usage Examples

### Basic MySQL Insert

```yaml
output:
  sql_insert:
    driver: mysql
    dsn: workshop:workshop123@tcp(localhost:3306)/workshop
    table: cleaned_users
    columns: [id, name, email, created_at]
    args_mapping: |
      root = [
        this.id,
        this.name,
        this.email,
        this.created_at
      ]
```

### PostgreSQL with Upsert (ON CONFLICT)

```yaml
output:
  sql_insert:
    driver: postgres
    dsn: postgres://workshop:workshop123@localhost:5432/workshop
    table: customers
    columns: [customer_id, name, email, updated_at]
    args_mapping: |
      root = [
        this.customer_id,
        this.name,
        this.email,
        now()
      ]
    suffix: |
      ON CONFLICT (customer_id)
      DO UPDATE SET
        name = EXCLUDED.name,
        email = EXCLUDED.email,
        updated_at = EXCLUDED.updated_at
```

### With Batching for High Throughput

```yaml
output:
  sql_insert:
    driver: postgres
    dsn: postgres://user:pass@localhost:5432/db
    table: events
    columns: [event_id, event_type, payload, timestamp]
    args_mapping: |
      root = [
        this.id,
        this.type,
        this.data.format_json(),
        this.timestamp
      ]
    max_in_flight: 128
    batching:
      count: 1000
      period: 5s
```

### With Initialization Script

```yaml
output:
  sql_insert:
    driver: postgres
    dsn: postgres://user:pass@localhost:5432/db
    table: audit_log
    columns: [action, user_id, details, created_at]
    args_mapping: |
      root = [
        this.action,
        this.user_id,
        this.details,
        now()
      ]
    init_statement: |
      SET search_path TO audit_schema;
    init_files:
      - ./sql/create_tables.sql
```
