# Cache Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/cache/

## Overview

The cache processor executes operations against cache resources for each message, enabling data storage and retrieval within message payloads.

## Basic Configuration

```yaml
pipeline:
  processors:
    - cache:
        resource: my_cache    # Required
        operator: set         # Required
        key: ${! json("id") } # Required
        value: ${! content() }
        ttl: 5m
```

## Configuration Fields

### `resource` (string, required)
The cache resource to target.

### `operator` (string, required)
The operation to perform. Options: `set`, `add`, `get`, `exists`, `delete`.

### `key` (string, required)
Cache key. Supports interpolation functions.

### `value` (string)
Cache value. Supports interpolation functions.

### `ttl` (string)
Time-to-live duration for items.

## Operators

### `set`
Overwrites existing keys or creates new entries in the cache.

```yaml
- cache:
    resource: my_cache
    operator: set
    key: ${! json("user_id") }
    value: ${! json("profile").format_json() }
    ttl: 1h
```

### `add`
Creates cache entries but fails if the key already exists. Useful for deduplication scenarios.

```yaml
- cache:
    resource: dedup_cache
    operator: add
    key: ${! json("event_id") }
    value: "seen"
```

### `get`
Retrieves cached content and replaces the message payload with the result.

```yaml
- cache:
    resource: lookup_cache
    operator: get
    key: ${! json("lookup_key") }
```

### `exists`
Returns `true` if a key exists, `false` otherwise.

```yaml
- cache:
    resource: my_cache
    operator: exists
    key: ${! json("id") }
```

### `delete`
Removes keys from cache without raising errors for missing entries.

```yaml
- cache:
    resource: my_cache
    operator: delete
    key: ${! json("id") }
```

## Use Cases

### Deduplication

Use the `add` operator to prevent duplicate messages:

```yaml
cache_resources:
  - label: dedup_cache
    memory:
      default_ttl: 1h

pipeline:
  processors:
    - cache:
        resource: dedup_cache
        operator: add
        key: ${! json("event_id") }
        value: "1"
    - catch:
        - log:
            level: DEBUG
            message: "Duplicate detected: ${! json(\"event_id\") }"
        - mapping: root = deleted()
```

### Hydration / Enrichment

Enrich message payloads by retrieving previously cached data:

```yaml
pipeline:
  processors:
    - branch:
        request_map: root = this.user_id
        processors:
          - cache:
              resource: user_cache
              operator: get
              key: ${! content() }
        result_map: root.user_profile = this
```

### Batch Deduplication

Deduplicate entire message batches using composite identifiers:

```yaml
pipeline:
  processors:
    - branch:
        request_map: |
          root = this.source + "-" + this.event_id
        processors:
          - cache:
              resource: batch_dedup
              operator: add
              key: ${! content() }
              value: "1"
        result_map: root.is_duplicate = errored()
    - mapping: |
        root = if this.is_duplicate { deleted() }
```

## Notable Features

- Supports dynamic keys and values based on message contents and metadata
- Interpolation functions enable flexible key/value generation per message
- Compatible with memory, Redis, Memcached, and other cache backends
