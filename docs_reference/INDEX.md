# Local Documentation Reference Index

This directory contains local copies of Expanso and Redpanda Connect documentation for offline reference and pipeline development.

## Directory Structure

```
docs_reference/
├── INDEX.md                          # This file
├── docs.expanso.io/                  # Expanso documentation
│   └── getting-started/
│       ├── overview.md
│       ├── quick-start.md
│       └── installation.md
├── examples.expanso.io/              # Expanso pipeline examples
│   └── INDEX.md                      # Examples index
└── redpanda-connect/                 # Redpanda Connect documentation
    ├── bloblang/                     # Bloblang language reference
    │   ├── about.md                  # Language overview
    │   ├── functions.md              # Function reference
    │   └── methods.md                # Method reference
    ├── configuration/
    │   └── resources.md              # Resource configuration
    └── components/
        ├── inputs/
        │   ├── INDEX.md              # All input components
        │   └── sql_select.md
        ├── outputs/
        │   ├── INDEX.md              # All output components
        │   ├── broker.md
        │   ├── fallback.md
        │   ├── sql_insert.md
        │   └── switch.md
        ├── processors/
        │   ├── INDEX.md              # All processors
        │   ├── branch.md
        │   ├── cache.md
        │   ├── catch.md
        │   ├── dedupe.md
        │   ├── group_by_value.md
        │   ├── log.md
        │   ├── mapping.md
        │   ├── mutation.md
        │   ├── sql_insert.md
        │   ├── sql_select.md
        │   ├── switch.md
        │   ├── try.md
        │   └── unarchive.md
        └── caches/
            └── memory.md
```

## Quick Reference

### Bloblang Language

| Topic | File | Description |
|-------|------|-------------|
| Overview | [bloblang/about.md](redpanda-connect/bloblang/about.md) | Language concepts and syntax |
| Functions | [bloblang/functions.md](redpanda-connect/bloblang/functions.md) | uuid_v4, now, content, etc. |
| Methods | [bloblang/methods.md](redpanda-connect/bloblang/methods.md) | String, array, object methods |

### Common Processors

| Processor | File | Use Case |
|-----------|------|----------|
| mapping | [processors/mapping.md](redpanda-connect/components/processors/mapping.md) | Data transformation |
| dedupe | [processors/dedupe.md](redpanda-connect/components/processors/dedupe.md) | Remove duplicates |
| branch | [processors/branch.md](redpanda-connect/components/processors/branch.md) | Parallel processing |
| switch | [processors/switch.md](redpanda-connect/components/processors/switch.md) | Conditional routing |
| cache | [processors/cache.md](redpanda-connect/components/processors/cache.md) | Caching operations |

### Common Outputs

| Output | File | Use Case |
|--------|------|----------|
| broker | [outputs/broker.md](redpanda-connect/components/outputs/broker.md) | Fan-out to multiple destinations |
| switch | [outputs/switch.md](redpanda-connect/components/outputs/switch.md) | Content-based routing |
| fallback | [outputs/fallback.md](redpanda-connect/components/outputs/fallback.md) | Failover handling |
| sql_insert | [outputs/sql_insert.md](redpanda-connect/components/outputs/sql_insert.md) | Database inserts |

### Error Handling

| Processor | File | Use Case |
|-----------|------|----------|
| try | [processors/try.md](redpanda-connect/components/processors/try.md) | Conditional execution |
| catch | [processors/catch.md](redpanda-connect/components/processors/catch.md) | Error recovery |
| log | [processors/log.md](redpanda-connect/components/processors/log.md) | Debug logging |

## Example Patterns

### 1. Read from Database, Transform, Write to Multiple Destinations

```yaml
input:
  sql_select:
    driver: postgres
    dsn: postgres://user:pass@localhost:5432/db
    table: events
    columns: ["*"]

pipeline:
  processors:
    - mapping: |
        root = this
        root.processed_at = now()

output:
  broker:
    pattern: fan_out
    outputs:
      - kafka:
          addresses: ["localhost:9092"]
          topic: events
      - aws_s3:
          bucket: archive
          path: events/${! timestamp_unix() }.json
```

### 2. Deduplicate and Route by Content

```yaml
cache_resources:
  - label: dedup
    memory:
      default_ttl: 1h

pipeline:
  processors:
    - dedupe:
        cache: dedup
        key: ${! json("id") }

output:
  switch:
    cases:
      - check: this.priority == "high"
        output:
          resource: high_priority_output
      - output:
          resource: default_output
```

### 3. Error Handling with Dead Letter Queue

```yaml
pipeline:
  processors:
    - try:
        - mapping: root = this.parse_json()
        - mapping: root = this.validate()
    - catch:
        - mapping: |
            root.original = content().string()
            root.error = error()
        - output:
            resource: dead_letter_queue
        - mapping: root = deleted()
```

## Sources

- **Expanso Documentation**: https://docs.expanso.io/
- **Expanso Examples**: https://examples.expanso.io/
- **Redpanda Connect**: https://docs.redpanda.com/redpanda-connect/
