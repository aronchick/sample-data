# Try Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/try/

## Overview

The try processor executes child processors conditionally, allowing messages to skip subsequent processors if prior ones have failed.

## Basic Configuration

```yaml
pipeline:
  processors:
    - try:
        - resource: step1
        - resource: step2
        - resource: step3
```

## Configuration Fields

### `label` (string, optional)
Identifier for the processor.

### `try` (array, required)
List of child processors to execute conditionally.

## Core Functionality

The processor operates similarly to `for_each`, applying child processors to individual batch messages. However, it implements conditional execution: "if a message has failed any prior processor (before or during the try block) then that message will skip all following processors."

## How It Works

```yaml
pipeline:
  processors:
    - resource: foo
    - try:
        - resource: bar
        - resource: baz
        - resource: buz
```

- If `bar` fails, the message bypasses `baz` and `buz`
- If `foo` fails initially, none of the try block processors execute for that message
- Successful messages proceed through all processors normally

## Use Cases

The processor excels when child processors depend on successful output from previous steps.

### Dependent Processing Chain

```yaml
pipeline:
  processors:
    - try:
        - mapping: |
            root = this.parse_json()
        - mapping: |
            root.validated = this.json_schema(file("schema.json"))
        - mapping: |
            root.enriched = true
            root.processed_at = now()
```

### Combined with Catch

```yaml
pipeline:
  processors:
    - try:
        - resource: parse_data
        - resource: validate_data
        - resource: transform_data
    - catch:
        - log:
            level: ERROR
            message: "Processing failed: ${! error() }"
        - mapping: root = deleted()
```

## Nesting Within Catch Blocks

When nesting try within catch, insert an empty catch block first to clear errors:

```yaml
pipeline:
  processors:
    - resource: primary_processor
    - catch:
        - log:
            level: ERROR
            message: "Primary failed: ${! error() }"
        - catch: []  # Clears prior error
        - try:
            - resource: fallback_step1
            - resource: fallback_step2
```

## Practical Example: Multi-Format Parsing

```yaml
pipeline:
  processors:
    - try:
        # Try JSON first
        - mapping: |
            root = content().parse_json()
            root.format = "json"
    - catch:
        - catch: []  # Clear error
        - try:
            # Try XML if JSON fails
            - mapping: |
                root = content().parse_xml()
                root.format = "xml"
    - catch:
        - catch: []
        - try:
            # Try CSV if XML fails
            - mapping: |
                root = content().parse_csv()
                root.format = "csv"
    - catch:
        - log:
            level: ERROR
            message: "All parsing attempts failed"
        - mapping: root = deleted()
```
