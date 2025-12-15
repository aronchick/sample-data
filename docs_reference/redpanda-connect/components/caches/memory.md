# Memory Cache Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/caches/memory/

## Overview

The memory cache component stores key/value pairs in an in-memory map within Redpanda Connect. Data persists only during service runtime and resets on restart.

## Basic Configuration

```yaml
cache_resources:
  - label: my_cache
    memory:
      default_ttl: 5m
      compaction_interval: 60s
```

## Configuration Fields

### `default_ttl` (string, default: `5m`)
Sets the standard expiration duration for cache items before they become eligible for removal.

### `compaction_interval` (string, default: `60s`)
Controls cleanup frequency for expired entries. "The compaction interval determines how often the cache is cleared of expired items, and this process is only triggered on writes to the cache."

Setting this to an empty string disables TTL expiration entirely.

### `init_values` (object, default: `{}`)
Prepopulates the cache with static key/value pairs exempt from TTLs.

```yaml
cache_resources:
  - label: lookup_cache
    memory:
      default_ttl: 10m
      init_values:
        status_active: "ACTIVE"
        status_pending: "PENDING"
        status_closed: "CLOSED"
```

### `shards` (integer, default: `1`)
Distributes keys across logical shards to improve performance when handling large datasets.

## Key Behaviors

- Access is blocked during compaction operations
- Pre-initialized values can be overridden during execution, after which standard TTL rules apply
- Useful for creating lookup tables with minimal configuration overhead

## Usage Example: Deduplication Cache

```yaml
cache_resources:
  - label: dedup_cache
    memory:
      default_ttl: 1h
      compaction_interval: 5m
      shards: 4

pipeline:
  processors:
    - dedupe:
        cache: dedup_cache
        key: ${! json("id") }
```

## Usage Example: Lookup Table

```yaml
cache_resources:
  - label: country_codes
    memory:
      init_values:
        US: "United States"
        GB: "United Kingdom"
        DE: "Germany"
        FR: "France"

pipeline:
  processors:
    - mapping: |
        root = this
        root.country_name = this.country_code.cache_get("country_codes").or(this.country_code)
```
