# SQL Insert Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/sql_insert/

## Overview

The `sql_insert` processor is a Redpanda Connect component that "inserts rows into an SQL database for each message, and leaves the message unchanged." Introduced in version 3.59.0, this processor is available in both Cloud and Self-Managed deployments.

## Required Configuration

Four fields are mandatory when configuring this processor:

- **driver**: The database system being targeted
- **dsn**: Connection string with authentication and database details
- **table**: Target table name
- **columns**: List of column names for insertion
- **args_mapping**: Bloblang expression that evaluates to value array

## Supported Database Drivers

The processor supports nine database systems: MySQL, PostgreSQL, ClickHouse, MSSQL, SQLite, Oracle, Snowflake, Trino, and Cosmos DB.

## Configuration Examples

### MySQL Implementation

A basic MySQL configuration demonstrates how to extract values from message content and metadata:

```yaml
sql_insert:
  driver: mysql
  dsn: foouser:foopassword@tcp(localhost:3306)/foodb
  table: footable
  columns: [ id, name, topic ]
  args_mapping: |
    root = [
      this.user.id,
      this.user.name,
      meta("kafka_topic"),
    ]
```

## Key Configuration Fields

**Connection Management:**
- `conn_max_idle`: Maximum idle connections (default: 2)
- `conn_max_open`: Maximum open connections
- `conn_max_idle_time`: Maximum idle duration before closure
- `conn_max_life_time`: Maximum connection reuse duration

**Initialization:**
- `init_statement`: SQL executed on first connection
- `init_files`: File paths containing initialization SQL (supports glob patterns)

**Query Modification:**
- `prefix`: Text prepended before INSERT keyword
- `suffix`: Text appended after query (useful for conflict resolution)
- `options`: Keywords inserted before INTO clause

## Error Handling

If an insert operation fails, "the message will still remain unchanged and the error can be caught using error handling methods."
