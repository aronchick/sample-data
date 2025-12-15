# Switch Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/switch/

## Overview

The switch processor conditionally executes processing logic based on message content evaluation. It's available in both Cloud and Self-Managed deployments.

**Core Function:** "Conditionally processes messages based on their contents."

## Basic Configuration

```yaml
label: ""
switch: [] # No default (required)
```

## How It Works

The processor evaluates each case sequentially using Bloblang queries. When a case's condition resolves to true (or when no condition is specified), its child processors execute against the message.

## Configuration Fields

### `check`
- **Type:** string
- **Default:** `""` (empty = always passes)
- **Purpose:** A Bloblang expression returning a boolean value

"If the check mapping throws an error the message will be flagged as having failed and will not be tested against any other cases."

**Example conditions:**
```yaml
check: this.type == "foo"
check: this.contents.urls.contains("https://benthos.dev/")
```

### `fallthrough`
- **Type:** boolean
- **Default:** `false`
- **Purpose:** When true, "the next case should also be executed" after a match

### `processors[]`
- **Type:** processor array
- **Default:** `[]`
- **Purpose:** List of processors to execute when a case matches

## Practical Example

Filtering messages by user identity:

```yaml
pipeline:
  processors:
    - switch:
        - check: this.user.name.first != "George"
          processors:
            - metric:
                type: counter
                name: MessagesWeCareAbout
        - processors:
            - metric:
                type: gauge
                name: GeorgesAnger
            - mapping: root = deleted()
```

## Batch Processing Behavior

When processing batches, messages are evaluated individually but processed together per-case. "At the end of switch processing the resulting batch will follow the same ordering as the batch was received."

For conditional grouping, use the `group_by` processor instead.
