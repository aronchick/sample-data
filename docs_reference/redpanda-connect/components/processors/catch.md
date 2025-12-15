# Catch Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/catch/

## Overview

The catch processor handles error recovery by applying child processors exclusively to messages that have failed previous processing steps.

## Basic Configuration

```yaml
pipeline:
  processors:
    - resource: risky_processor
    - catch:
        - log:
            level: ERROR
            message: "Processing failed: ${! error() }"
```

## Configuration Fields

### `label` (string, optional)
Identifier for the processor.

### `catch` (array, required)
List of child processors to apply to failed messages.

## Functionality

The catch processor operates similarly to the `for_each` processor, applying a list of child processors to individual messages within a batch. However, **"processors are only applied to messages that failed a previous processing step prior to the catch."**

Upon exiting the catch block, **"their fail flags are cleared."**

## Use Cases

### Error Recovery

Recover failed messages through remedial processing:

```yaml
pipeline:
  processors:
    - mapping: |
        root = this.parse_json()  # May fail on invalid JSON
    - catch:
        - mapping: |
            root = {"raw": content().string(), "parse_error": true}
```

### Error Logging and Metrics

Execute specialized actions before message removal:

```yaml
pipeline:
  processors:
    - resource: transform_data
    - catch:
        - log:
            level: ERROR
            message: "Transform failed"
            fields_mapping: |
              root.error = error()
              root.message_id = json("id").or("unknown")
        - mapping: root = deleted()
```

### Dead Letter Queue

Route failed messages to a separate destination:

```yaml
pipeline:
  processors:
    - mapping: |
        root = this.thing.parse_json()
    - catch:
        - mapping: |
            root.original = content().string()
            root.error = error()
            root.failed_at = now()
        - output:
            resource: dead_letter_queue
        - mapping: root = deleted()
```

## Example Workflow

```yaml
pipeline:
  processors:
    - resource: foo
    - catch:
        - resource: bar
        - resource: baz
```

When processor `foo` encounters an error on a specific message:
1. That message enters the catch block
2. Passes through processors `bar` and `baz`
3. Error flag is cleared upon exit

Messages that process successfully skip the catch block entirely.

## Nested Error Handling

```yaml
pipeline:
  processors:
    - mapping: |
        root = this.parse_json()
    - catch:
        - log:
            level: WARN
            message: "JSON parse failed, trying XML"
        - mapping: |
            root = content().parse_xml()
        - catch:
            - log:
                level: ERROR
                message: "Both JSON and XML parsing failed"
            - mapping: root = deleted()
```

## Combined with Try Processor

```yaml
pipeline:
  processors:
    - try:
        - mapping: root = this.strict_transform()
        - mapping: root = this.validate()
    - catch:
        - mapping: |
            root.error = error()
            root.stage = "validation_pipeline"
        - output:
            resource: error_queue
        - mapping: root = deleted()
```
