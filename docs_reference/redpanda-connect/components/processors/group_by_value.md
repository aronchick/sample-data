# Group By Value Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/group_by_value/

## Overview

The `group_by_value` processor "Splits a batch of messages into N batches, where each resulting batch contains a group of messages determined by a function interpolated string evaluated per message."

Available in both Cloud and Self-Managed Redpanda.

## Basic Configuration

```yaml
pipeline:
  processors:
    - group_by_value:
        value: ${! json("category") }
```

## Configuration Fields

### `value` (string, required)
The interpolated string to group based on. Supports interpolation functions.

Examples:
- `${! meta("kafka_key") }` - Group by Kafka message key
- `${! json("type") }` - Group by JSON field
- `${! json("foo.bar") }-${! meta("baz") }` - Combined grouping key

## Key Concepts

This processor depends on batched messages to function effectively. Grouping logic enables:
- Processing messages individually
- Directing them to different destinations based on group assignments
- Aggregating related messages together

## Use Cases

### Group by Kafka Key and Archive to S3

```yaml
input:
  kafka:
    addresses: ["localhost:9092"]
    topics: ["events"]
    consumer_group: archiver

pipeline:
  processors:
    - group_by_value:
        value: ${! meta("kafka_key") }
    - archive:
        format: tar
    - compress:
        algorithm: gzip

output:
  aws_s3:
    bucket: my-archive-bucket
    path: docs/${! meta("kafka_key") }/${! count("files") }-${! timestamp_unix_nano() }.tar.gz
```

### Group by Event Type

```yaml
pipeline:
  processors:
    - group_by_value:
        value: ${! json("event_type") }
    - mapping: |
        root = this
        root.batch_size = batch_size()
        root.grouped_by = json("event_type")
```

### Group by Customer and Aggregate

```yaml
pipeline:
  processors:
    - group_by_value:
        value: ${! json("customer_id") }
    - mapping: |
        root.customer_id = this.index(0).customer_id
        root.events = this.map_each(e -> e.without("customer_id"))
        root.event_count = batch_size()
        root.total_value = this.map_each(e -> e.value).sum()
```

### Group by Time Window

```yaml
pipeline:
  processors:
    - mapping: |
        root = this
        root.time_bucket = (this.timestamp / 3600).floor() * 3600
    - group_by_value:
        value: ${! json("time_bucket") }
    - archive:
        format: json_array
```

## Combining with Other Processors

```yaml
pipeline:
  processors:
    # First, batch messages
    - batching:
        count: 100
        period: 10s

    # Then group by category
    - group_by_value:
        value: ${! json("category") }

    # Archive each group
    - archive:
        format: json_array

    # Compress
    - compress:
        algorithm: gzip
```
