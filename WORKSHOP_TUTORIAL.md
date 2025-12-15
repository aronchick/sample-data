# Bad Data Workshop: Cleaning with Expanso Pipelines

This workshop demonstrates how to use [Expanso](https://docs.expanso.io) data
pipelines to clean intentionally problematic data. You'll learn real-world
patterns for data quality, schema enforcement, deduplication, and more.

## Workshop Overview

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   BAD DATA TABLES   │────▶│  EXPANSO PIPELINES  │────▶│  CLEAN DATA TABLES  │
│   (15 Problems)     │     │   (Bloblang, etc)   │     │  (Validated Data)   │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │   REJECTED RECORDS  │
                            │   (Dead Letter)     │
                            └─────────────────────┘
```

**Key Principle**: Original data is NEVER modified. All cleaning writes to new
destination tables, preserving the raw data for audit trails.

## Prerequisites

1. **Docker** (for local database)
2. **uv** (Python package manager)
3. **Expanso agent** (or use the YAML configs as reference)

## Part 1: Setup the Environment

### Step 1: Start the Database

```bash
cd sample-data
docker compose up -d postgres
```

### Step 2: Create Bad Data

```bash
# Generate workshop data (use 'tiny' for quick testing)
uv run --script bad_data_workshop.py setup \
    --db-type postgres \
    --host localhost \
    --database workshop \
    --user workshop \
    --password workshop123 \
    --scale tiny
```

### Step 3: Create Clean Destination Tables

```bash
# Run the schema setup SQL
docker exec -i bdw-postgres psql -U workshop -d workshop \
    < expanso_pipelines/setup_clean_schema.sql
```

### Step 4: Explore the Bad Data

Run these diagnostic queries to see the problems:

```bash
uv run --script bad_data_workshop.py diagnose --db-type postgres
```

---

## Part 2: Expanso Features Deep Dive

### Feature 1: Data Type Transformation (Bloblang Mapping)

**Problem**: Dates and numbers stored as strings with inconsistent formats.

**Pipeline**: `expanso_pipelines/03_fix_data_types.yaml`

**Key Concepts**:
- `mapping` processor with Bloblang language
- `ts_parse()` for date parsing with fallback chain
- `number()` for string-to-number conversion
- `catch()` for error handling

```yaml
# Bloblang transformation example
root.transaction_date = this.transaction_date.ts_parse("2006-01-02").catch(
  this.transaction_date.ts_parse("01/02/2006").catch(
    now()  # Fallback to current time
  )
)
```

**Run it**:
```bash
expanso run -c expanso_pipelines/03_fix_data_types.yaml
```

---

### Feature 2: Deduplication (Cache + Dedupe Processor)

**Problem**: Duplicate records with no unique constraints.

**Pipeline**: `expanso_pipelines/05_deduplicate.yaml`

**Key Concepts**:
- `dedupe` processor with cache backend
- Composite key generation for matching
- `cache_resources` configuration

```yaml
pipeline:
  processors:
    - mapping: |
        root.dedupe_key = "%s_%s".format(this.user_id, this.email.lowercase())
    - dedupe:
        cache: user_dedupe_cache
        key: ${! this.dedupe_key }

cache_resources:
  - label: user_dedupe_cache
    memory:
      default_ttl: 1h
```

**Run it**:
```bash
expanso run -c expanso_pipelines/05_deduplicate.yaml
```

---

### Feature 3: Schema Validation (Regex + Conditional Routing)

**Problem**: Invalid email formats in subscriber data.

**Pipeline**: `expanso_pipelines/09_validate_emails.yaml`

**Key Concepts**:
- `re_match()` for regex validation
- Conditional routing with `switch` output
- Multi-destination: valid → clean table, invalid → rejected table

```yaml
# Email validation with regex
let email_regex = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
root.email_valid = this.email.re_match($email_regex)

# Route based on validation
output:
  switch:
    - check: this.is_valid == true
      output: # → clean table
    - output: # → rejected table (dead letter)
```

---

### Feature 4: Content-Based Routing (Switch + Priority Queues)

**Problem**: Out-of-range values requiring different handling by severity.

**Pipeline**: `expanso_pipelines/10_range_validation.yaml`

**Key Concepts**:
- Business rule validation in Bloblang
- Severity classification
- Priority-based routing to different queues
- `broker` output with `fan_out` pattern

```yaml
# Classify severity based on error count
root.severity = if root.validation_errors.length() == 0 {
  "none"
} else if root.validation_errors.length() <= 3 {
  "medium"
} else {
  "high"
}

# Route by severity
output:
  broker:
    pattern: fan_out
    outputs:
      - switch:
          - check: this.is_valid == true
            output: # → clean table
          - check: this.severity == "high"
            output: # → high priority review
          - output: # → standard review queue
```

---

### Feature 5: Branch Processing (Parallel Transformations)

**Problem**: Denormalized "god table" with 30+ columns.

**Pipeline**: `expanso_pipelines/13_normalize_god_table.yaml`

**Key Concepts**:
- `branch` processor for parallel extraction
- Extract multiple entity types simultaneously
- Dedupe each entity type independently
- Write to 4 normalized tables from 1 input

```yaml
pipeline:
  processors:
    - branch:
        processors:
          - mapping: |
              root.entity_type = "customer"
              root.customer_id = this.customer_id
              # ... extract customer fields
        result_map: |
          root.customer = this

    - branch:
        processors:
          - mapping: |
              root.entity_type = "product"
              # ... extract product fields
        result_map: |
          root.product = this
```

---

### Feature 6: Exploding Arrays (Unarchive Processor)

**Problem**: Comma-separated values violating First Normal Form.

**Pipeline**: `expanso_pipelines/11_normalize_csv_columns.yaml`

**Key Concepts**:
- `split()` to parse CSV strings
- `map_each()` for array transformations
- `unarchive` processor to explode arrays into messages
- Junction tables for many-to-many relationships

```yaml
# Parse CSV to array
root.tags_array = this.tags.split(",").map_each(t -> t.trim())

# Create array of pairs
root = this.tags_array.map_each(tag -> {
  "article_id": this.article_id,
  "tag": tag
})

# Explode to individual messages
- unarchive:
    format: json_array
```

---

### Feature 7: String Normalization

**Problem**: Inconsistent casing and whitespace.

**Pipelines**:
- `expanso_pipelines/07_normalize_casing.yaml`
- `expanso_pipelines/08_trim_whitespace.yaml`

**Key Concepts**:
- `capitalize()`, `lowercase()`, `uppercase()`
- `trim()` for whitespace removal
- `re_replace_all()` for pattern replacement

```yaml
# Normalize casing
root.first_name = this.first_name.capitalize()
root.email = this.email.lowercase()

# Clean whitespace
root.sku = this.sku.trim().re_replace_all("[\t\n\r]+", " ")
```

---

## Part 3: Running the Complete Workshop

### Run All Pipelines

```bash
# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=workshop
export DB_USER=workshop
export DB_PASS=workshop123

# Run each pipeline
for pipeline in expanso_pipelines/*.yaml; do
    echo "Running $pipeline..."
    expanso run -c "$pipeline"
done
```

### Verify Results

```sql
-- Compare source vs clean counts
SELECT 'transactions' as table_name,
       (SELECT COUNT(*) FROM bad_data_workshop.transactions_bad_types) as source,
       (SELECT COUNT(*) FROM bad_data_workshop_clean.transactions_typed) as clean,
       (SELECT COUNT(*) FROM bad_data_workshop_rejected.transactions_parse_failures) as rejected;

SELECT 'users' as table_name,
       (SELECT COUNT(*) FROM bad_data_workshop.users_duplicates) as source,
       (SELECT COUNT(*) FROM bad_data_workshop_clean.users_unique) as clean;

SELECT 'subscribers' as table_name,
       (SELECT COUNT(*) FROM bad_data_workshop.subscribers_bad_emails) as source,
       (SELECT COUNT(*) FROM bad_data_workshop_clean.subscribers_valid) as clean,
       (SELECT COUNT(*) FROM bad_data_workshop_rejected.subscribers_invalid_emails) as rejected;
```

---

## Part 4: Cleanup

```bash
# Remove all workshop data
uv run --script bad_data_workshop.py teardown \
    --db-type postgres \
    --host localhost \
    --database workshop \
    --user workshop \
    --password workshop123

# Stop Docker
docker compose down -v
```

---

## Expanso Feature Summary

| Feature | Processor/Component | Use Case |
|---------|---------------------|----------|
| **Data Transformation** | `mapping` (Bloblang) | Type conversion, parsing, normalization |
| **Deduplication** | `dedupe` + cache | Remove duplicate records |
| **Validation** | `mapping` + regex | Schema enforcement, format validation |
| **Content Routing** | `switch` | Route based on data content |
| **Multi-Destination** | `broker` (fan_out) | Write to multiple tables simultaneously |
| **Parallel Processing** | `branch` | Extract multiple entity types at once |
| **Array Explosion** | `unarchive` | Split arrays into individual messages |
| **Error Handling** | `.catch()` | Graceful fallbacks for parsing errors |

## Additional Resources

- [Expanso Documentation](https://docs.expanso.io)
- [Expanso Examples](https://examples.expanso.io)
- [Bloblang Reference](https://docs.expanso.io/components/)
- [Component Catalog](https://docs.expanso.io/components/)
