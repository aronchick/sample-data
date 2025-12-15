# Redpanda Connect Processors Index

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/

## Overview

Processors transform, filter, and route messages within pipelines. They can be applied at input, pipeline, or output levels.

## Transformation Processors

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `mapping` | Bloblang transformations creating new documents | [mapping.md](mapping.md) |
| `mutation` | In-place Bloblang transformations | [mutation.md](mutation.md) |
| `jmespath` | JMESPath query transformations | - |
| `jq` | jq query transformations | - |
| `awk` | AWK program execution | - |
| `javascript` | JavaScript code execution | - |
| `protobuf` | Protocol buffer encoding/decoding | - |
| `avro` | Avro encoding/decoding | - |
| `msgpack` | MessagePack encoding/decoding | - |
| `xml` | XML parsing and formatting | - |

## Flow Control Processors

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `switch` | Conditional processor routing | [switch.md](switch.md) |
| `branch` | Parallel processor branches | [branch.md](branch.md) |
| `for_each` | Apply processors to each message | - |
| `try` | Conditional execution on success | [try.md](try.md) |
| `catch` | Error recovery processing | [catch.md](catch.md) |
| `while` | Loop until condition met | - |
| `workflow` | DAG-based processor workflows | - |

## Batching Processors

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `group_by_value` | Group messages by field value | [group_by_value.md](group_by_value.md) |
| `group_by` | Group messages by Bloblang query | - |
| `split` | Split messages into multiple | - |
| `archive` | Archive messages (tar, zip, json_array) | - |
| `unarchive` | Extract archived messages | [unarchive.md](unarchive.md) |
| `compress` | Compress message content | - |
| `decompress` | Decompress message content | - |

## Deduplication & Caching

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `dedupe` | Remove duplicate messages | [dedupe.md](dedupe.md) |
| `cache` | Cache operations (get, set, add, delete) | [cache.md](cache.md) |

## Database Processors

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `sql_select` | Execute SELECT queries | [sql_select.md](sql_select.md) |
| `sql_insert` | Execute INSERT statements | [sql_insert.md](sql_insert.md) |
| `sql_raw` | Execute raw SQL | - |
| `redis` | Redis commands | - |
| `mongodb` | MongoDB operations | - |

## HTTP & Network

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `http` | HTTP requests | - |
| `grok` | Grok pattern parsing | - |
| `parse_log` | Structured log parsing | - |

## Observability

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `log` | Log messages | [log.md](log.md) |
| `metric` | Custom metrics | - |
| `opentelemetry_span` | OpenTelemetry spans | - |

## Utility Processors

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `resource` | Reference processor resources | - |
| `noop` | No operation (pass-through) | - |
| `sleep` | Pause processing | - |
| `rate_limit` | Rate limiting | - |
| `bounds_check` | Message size validation | - |

## Schema Validation

| Processor | Description | Local Doc |
|-----------|-------------|-----------|
| `json_schema` | JSON Schema validation | - |
| `schema_registry_decode` | Decode with schema registry | - |
| `schema_registry_encode` | Encode with schema registry | - |

## Common Patterns

### Transform and Filter
```yaml
pipeline:
  processors:
    - mapping: |
        root = this
        root.processed = true
    - mapping: |
        root = if this.valid { this } else { deleted() }
```

### Error Handling
```yaml
pipeline:
  processors:
    - try:
        - resource: risky_transform
    - catch:
        - log:
            level: ERROR
            message: "Failed: ${! error() }"
        - mapping: root = deleted()
```

### Deduplication
```yaml
pipeline:
  processors:
    - dedupe:
        cache: dedup_cache
        key: ${! json("id") }
```

### Content Routing
```yaml
pipeline:
  processors:
    - switch:
        - check: this.type == "order"
          processors:
            - resource: order_transform
        - check: this.type == "user"
          processors:
            - resource: user_transform
```
