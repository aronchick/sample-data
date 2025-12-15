# Log Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/log/

## Overview

The log processor outputs a log event for each message while leaving messages unmodified. Supports custom formatting through Bloblang interpolations.

## Basic Configuration

```yaml
pipeline:
  processors:
    - log:
        level: INFO
        message: "Processing message: ${! json(\"id\") }"
```

## Configuration Fields

### `level` (string, default: INFO)
Log severity level. Options: `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`.

### `message` (string)
The text to output. Supports interpolation functions for dynamic content.

### `fields_mapping` (string)
Optional Bloblang mapping for adding structured fields to logs.

### `fields` (object)
Static fields to add to log output. Overrides matching `fields_mapping` entries.

## Log Levels

| Level | Use Case |
|-------|----------|
| `TRACE` | Detailed debugging, high volume |
| `DEBUG` | Development debugging |
| `INFO` | Normal operation events |
| `WARN` | Potential issues |
| `ERROR` | Errors that need attention |

## Examples

### Simple Message Logging

```yaml
- log:
    level: INFO
    message: "Received message with ID: ${! json(\"id\") }"
```

### Structured Logging

```yaml
- log:
    level: INFO
    message: "Processing event"
    fields_mapping: |
      root.event_id = json("id")
      root.event_type = json("type")
      root.user_id = json("user.id")
      root.kafka_topic = meta("kafka_topic")
      root.kafka_partition = meta("kafka_partition")
```

### Error Logging with Context

```yaml
- log:
    level: ERROR
    message: "Validation failed"
    fields_mapping: |
      root.reason = "Invalid data format"
      root.message_content = content().string()
      root.timestamp = now()
```

### Conditional Logging

```yaml
pipeline:
  processors:
    - switch:
        - check: this.priority == "high"
          processors:
            - log:
                level: WARN
                message: "High priority event: ${! json(\"id\") }"
        - processors:
            - log:
                level: DEBUG
                message: "Normal event: ${! json(\"id\") }"
```

### Debug Pipeline Flow

```yaml
pipeline:
  processors:
    - log:
        level: DEBUG
        message: "Stage 1: Raw input"
        fields_mapping: root.payload_size = content().length()

    - mapping: |
        root = this
        root.transformed = true

    - log:
        level: DEBUG
        message: "Stage 2: After transformation"
        fields_mapping: root.payload_size = content().length()
```

## Key Features

- Messages pass through unchanged after logging
- Supports both simple messages and complex field mappings
- Compatible with Redpanda Cloud and Self-Managed deployments
- Integrates seamlessly into pipelines for observability without altering data flow
