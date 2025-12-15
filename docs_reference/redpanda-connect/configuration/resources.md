# Redpanda Connect Resources Configuration

> Source: https://docs.redpanda.com/redpanda-connect/configuration/resources/

## Overview

Resources in Redpanda Connect are reusable components declared with unique labels. "Only one instance of each named resource is created, but it is safe to use it in multiple places as they can be shared without consequence."

## Resource Types

The system supports four main resource categories:

### Input Resources
```yaml
input_resources:
  - label: my_kafka_input
    kafka:
      addresses: ["localhost:9092"]
      topics: ["my-topic"]
```

### Processor Resources
```yaml
processor_resources:
  - label: my_transform
    mapping: |
      root = this
      root.processed_at = now()
```

### Cache Resources
```yaml
cache_resources:
  - label: my_cache
    memory:
      default_ttl: 5m
```

### Output Resources
```yaml
output_resources:
  - label: my_s3_output
    aws_s3:
      bucket: my-bucket
      path: "data/${!timestamp_unix()}.json"
```

## Usage Pattern

Reference resources by label:

```yaml
input:
  resource: my_kafka_input

pipeline:
  processors:
    - resource: my_transform
    - cache:
        resource: my_cache
        operator: set
        key: ${! json("id") }
        value: ${! content() }

output:
  resource: my_s3_output
```

## Implementation Benefits

### Reusability
Rather than duplicating large component configurations, define them once as resources and reference them multiple times throughout your pipeline.

### Feature Toggling
Resources enable environment-specific configurations through two approaches:

**Environment Variables:**
```yaml
output:
  resource: ${OUTPUT_RESOURCE}
```

**File Imports:**
```bash
rpk connect run -r ./staging/resources.yaml ./config.yaml
rpk connect run -r ./production/*.yaml ./config.yaml
```

The import method supports wildcards for loading entire directories of resource files.

## Cache and Rate Limit Resources

Certain components like caches and rate limits can *only* be created as resources:

```yaml
cache_resources:
  - label: dedup_cache
    memory:
      default_ttl: 1h

rate_limit_resources:
  - label: api_limiter
    local:
      count: 100
      interval: 1m
```

Reference in processors:

```yaml
pipeline:
  processors:
    - dedupe:
        cache: dedup_cache
        key: ${! json("id") }
    - rate_limit:
        resource: api_limiter
```

## Complete Example

```yaml
# Resource definitions
cache_resources:
  - label: lookup_cache
    memory:
      default_ttl: 10m
      init_values:
        status_1: "active"
        status_2: "pending"

processor_resources:
  - label: enrich_status
    mapping: |
      root = this
      root.status_name = this.status_code.cache_get("lookup_cache").or("unknown")

output_resources:
  - label: primary_output
    kafka:
      addresses: ["localhost:9092"]
      topic: processed-events
  - label: backup_output
    aws_s3:
      bucket: backup-bucket
      path: "events/${!timestamp_unix()}.json"

# Main pipeline
input:
  kafka:
    addresses: ["localhost:9092"]
    topics: ["raw-events"]

pipeline:
  processors:
    - resource: enrich_status

output:
  broker:
    pattern: fan_out
    outputs:
      - resource: primary_output
      - resource: backup_output
```
