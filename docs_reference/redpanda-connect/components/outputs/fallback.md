# Fallback Output Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/outputs/fallback/

## Overview

The fallback output attempts to send messages sequentially through child outputs. If one fails, the next in the list is tried. Introduced in version 3.58.0, useful for rerouting messages when primary targets become unavailable.

## Basic Configuration

```yaml
output:
  fallback:
    - http_client:
        url: http://primary:4195/post
    - http_client:
        url: http://secondary:4196/post
    - file:
        path: /tmp/fallback.jsonl
```

## Configuration Fields

### `fallback` (array, required)
Ordered list of output configurations to try sequentially.

## Key Features

### Metadata Support
Failed outputs pass a `fallback_error` metadata value containing error details to subsequent outputs:

```yaml
output:
  fallback:
    - http_client:
        url: http://primary:4195/post
    - http_client:
        url: http://secondary:4196/post
      processors:
        - mapping: |
            root = this
            root.primary_error = meta("fallback_error")
```

### Batching Handling
The system attempts to identify which individual messages within a batch failed and forwards only those. When individual message failure cannot be determined, the entire batch transfers to maintain delivery guarantees.

## Use Cases

### Primary/Secondary with File Backup

```yaml
output:
  fallback:
    - http_client:
        url: http://foo:4195/post/might/become/unreachable
        retries: 3
        retry_period: 1s
    - http_client:
        url: http://bar:4196/somewhere/else
        retries: 3
        retry_period: 1s
      processors:
        - mapping: 'root = "failed to send to foo: " + content()'
    - file:
        path: /usr/local/benthos/everything_failed.jsonl
```

### Database with S3 Backup

```yaml
output:
  fallback:
    - sql_insert:
        driver: postgres
        dsn: postgres://user:pass@primary:5432/db
        table: events
        columns: [id, data, created_at]
        args_mapping: |
          root = [this.id, this.format_json(), now()]
    - sql_insert:
        driver: postgres
        dsn: postgres://user:pass@secondary:5432/db
        table: events
        columns: [id, data, created_at]
        args_mapping: |
          root = [this.id, this.format_json(), now()]
    - aws_s3:
        bucket: failover-bucket
        path: events/${! timestamp_unix() }/${! uuid_v4() }.json
```

### Kafka with Local Buffer

```yaml
output:
  fallback:
    - kafka:
        addresses: ["kafka1:9092", "kafka2:9092"]
        topic: events
        max_retries: 3
    - file:
        path: /var/spool/events/${! timestamp_unix_nano() }.json
      processors:
        - mapping: |
            meta kafka_error = meta("fallback_error")
```

### Multi-Region Failover

```yaml
output:
  fallback:
    - aws_sqs:
        url: https://sqs.us-east-1.amazonaws.com/123456789/primary-queue
        region: us-east-1
    - aws_sqs:
        url: https://sqs.us-west-2.amazonaws.com/123456789/backup-queue
        region: us-west-2
    - aws_sqs:
        url: https://sqs.eu-west-1.amazonaws.com/123456789/dr-queue
        region: eu-west-1
```

## Error Enrichment Example

```yaml
output:
  fallback:
    - http_client:
        url: http://api.example.com/events
      processors:
        - mapping: |
            root = this
            root.attempt = 1
    - http_client:
        url: http://backup.example.com/events
      processors:
        - mapping: |
            root = this
            root.attempt = 2
            root.previous_error = meta("fallback_error")
    - file:
        path: /var/log/failed_events.jsonl
      processors:
        - mapping: |
            root = this
            root.all_attempts_failed = true
            root.last_error = meta("fallback_error")
            root.failed_at = now()
```
