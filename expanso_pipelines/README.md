# Expanso Data Cleaning Pipelines

This directory contains Expanso pipeline configurations that demonstrate how to
clean the intentionally bad data created by `bad_data_workshop.py`.

## Architecture Overview

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   BAD DATA TABLES   │────▶│  EXPANSO PIPELINES  │────▶│  CLEAN DATA TABLES  │
│   (Source - Read)   │     │   (Transform)       │     │  (Destination)      │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │   REJECTED RECORDS  │
                            │   (Dead Letter)     │
                            └─────────────────────┘
```

**Key Principle**: Original bad data remains untouched. All cleaning operations
write to new destination tables.

## Expanso Features Demonstrated

| Feature | Problem(s) Solved | Pipeline File |
|---------|------------------|---------------|
| **Mapping (Bloblang)** | Type conversion, date normalization, string cleaning | All pipelines |
| **Dedupe** | Duplicate records | `05_deduplicate.yaml` |
| **Schema Validation** | Invalid emails, data validation | `09_validate_emails.yaml` |
| **Content Routing (switch)** | Route valid/invalid records | `04_null_routing.yaml` |
| **Multi-Destination** | Clean data + dead letter queue | `10_range_validation.yaml` |
| **Branch Processing** | Parallel transformations | `13_normalize_god_table.yaml` |

## Pipeline Files

### Data Type & Format Cleaning
- `03_fix_data_types.yaml` - Convert string dates/numbers to proper types
- `06_normalize_dates.yaml` - Standardize date formats
- `07_normalize_casing.yaml` - Consistent string casing
- `08_trim_whitespace.yaml` - Remove leading/trailing whitespace
- `12_fix_encoding.yaml` - Handle special characters

### Data Quality
- `05_deduplicate.yaml` - Remove duplicate records
- `09_validate_emails.yaml` - Schema validation for email format
- `10_range_validation.yaml` - Filter out-of-range values

### Structural Issues
- `01_add_primary_keys.yaml` - Generate surrogate keys
- `02_fix_foreign_keys.yaml` - Resolve orphaned records
- `11_normalize_csv_columns.yaml` - Split CSV values to proper tables
- `13_normalize_god_table.yaml` - Break apart denormalized table
- `14_create_indexed_table.yaml` - Create properly indexed structure

### Advanced Patterns
- `15_type_coercion_fix.yaml` - Fix string/integer ID mismatches
- `all_in_one_demo.yaml` - Combined pipeline showing all features

## Running the Pipelines

```bash
# Install Expanso agent
curl -sSL https://get.expanso.io | bash

# Run a single pipeline
expanso run -c 03_fix_data_types.yaml

# Run with environment variables for database connection
DB_HOST=localhost DB_PORT=5432 DB_USER=workshop DB_PASS=workshop123 \
    expanso run -c 03_fix_data_types.yaml
```

## Database Schema

### Source Tables (Bad Data)
Located in schema: `bad_data_workshop`

### Destination Tables (Clean Data)
Located in schema: `bad_data_workshop_clean`

### Dead Letter Tables (Rejected Records)
Located in schema: `bad_data_workshop_rejected`
