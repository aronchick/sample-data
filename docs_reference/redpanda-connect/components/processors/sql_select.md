# sql_select Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/sql_select/

## Overview

The `sql_select` processor executes SQL queries against databases, returning results as an array of objects. As stated in the documentation: "Runs an SQL select query against a database and returns the result as an array of objects, one for each row returned, containing a key for each column queried and its value." This component was introduced in version 3.59.0.

## Supported Database Drivers

Nine database systems are supported:
- MySQL
- PostgreSQL
- ClickHouse
- MSSQL
- SQLite
- Oracle
- Snowflake
- Trino
- Google Cosmos DB
- Google Cloud Spanner

## Essential Configuration Parameters

### Required Fields

**Driver**: Specifies the database system to connect with.

**DSN (Data Source Name)**: The connection string format varies by database type. Examples include:
- PostgreSQL: `postgres://user:pass@localhost:5432/db?sslmode=disable`
- MySQL: `user:password@tcp(localhost:3306)/database`
- ClickHouse: `clickhouse://user:pass@host:9000/db?dial_timeout=200ms`
- Oracle: `oracle://user:pass@localhost:1521/service_name`

**Table**: The target table name to query.

**Columns**: A list of columns to retrieve (supports wildcard `*`).

### Optional Fields

**Where Clause**: Filters results using placeholder syntax. The documentation notes: "Placeholder arguments are populated with the `args_mapping` field. Placeholders should always be question marks, and will automatically be converted to dollar syntax when the postgres or clickhouse drivers are used."

**args_mapping**: A Bloblang mapping evaluating to an array matching placeholder count in the WHERE clause.

## Advanced Configuration

Connection pooling options include:
- `conn_max_idle` (default: 2 connections)
- `conn_max_idle_time`
- `conn_max_life_time`
- `conn_max_open` (default: unlimited)

Database initialization features:
- `init_statement`: SQL executed on first connection
- `init_files`: File paths containing SQL statements (requires version 4.10.0+)

Query modification:
- `prefix`: Text prepended before SELECT
- `suffix`: Text appended after the query

## Usage Example

A PostgreSQL implementation demonstrates practical usage:

```yaml
pipeline:
  processors:
    - branch:
        processors:
          - sql_select:
              driver: postgres
              dsn: postgres://user:pass@localhost:5432/testdb?sslmode=disable
              table: footable
              columns: ['*']
              where: user_id = ?
              args_mapping: '[ this.user.id ]'
        result_map: 'root.foo_rows = this'
```

## Error Handling

Failed queries leave messages unchanged, allowing standard error handling methods to catch and process failures.
