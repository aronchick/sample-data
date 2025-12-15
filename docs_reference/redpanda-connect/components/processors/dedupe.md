# Dedupe Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/dedupe/

## Overview

The dedupe processor removes duplicate messages by storing message keys in a cache. When a key already exists in the cache, the message is discarded. This component is available in both Cloud and Self-Managed versions of Redpanda Connect.

## Basic Configuration

```yaml
label: ""
dedupe:
  cache: "" # Required
  key: ${! meta("kafka_key") } # Required
  drop_on_err: true
```

## Required Fields

**Cache**: "The cache resource to target with this processor." This must be configured separately as a resource. Refer to cache documentation for setup details.

**Key**: "An interpolated string yielding the key to deduplicate by for each message." This field supports interpolation functions and can extract values from message metadata or content.

## Optional Fields

**drop_on_err**: Boolean field (default: `true`) that determines whether messages should be discarded when the cache encounters errors like network issues.

## Important Considerations

### Delivery Guarantees
Using distributed caches for deduplication compromises at-least-once delivery guarantees. Messages marked as duplicates remain in the cache even if they fail to reach the output, potentially causing data loss during outages.

### Mitigation Strategies
To address this concern, consider:
- Using in-memory caches with horizontally scaled pipelines partitioned by deduplication keys
- Implementing idempotent behavior at pipeline edges rather than relying on deduplication

### Batch Processing
This processor operates on individual messages only. For batch or window-level deduplication, use the cache processor instead.

### Output Configuration
Always wrap output targets in an indefinite retry block to prevent message reprocessing during failures.

## Configuration Example

```yaml
pipeline:
  processors:
    - dedupe:
        cache: keycache
        key: ${! meta("kafka_key") }

cache_resources:
  - label: keycache
    memory:
      default_ttl: 60s
```

This example deduplicates based on Kafka keys using an in-memory cache with 60-second TTL.
