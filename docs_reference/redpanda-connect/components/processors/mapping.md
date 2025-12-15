# Redpanda Connect: Mapping Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/mapping/

## Overview

The mapping processor executes Bloblang transformations on messages, generating new documents that replace or filter originals. Introduced in version 4.5.0, it's available in both Cloud and Self-Managed environments.

## Configuration

```yaml
label: ""
mapping: "" # No default (required)
```

The `mapping` field is mandatory and contains the transformation logic.

## Key Features

### File-Based Mappings

Large mappings can be stored separately using: `from "<path>"` where paths are absolute or relative to the Redpanda Connect execution location.

### Input Immutability

The processor creates entirely new objects during assignments, preserving the original document as queryable throughout transformation. This enables simultaneous operations on unchanged source data while building modified output structures.

Example illustrating this principle:

```coffeescript
root.id = this.id
root.invitees = this.invitees.filter(i -> i.mood >= 0.5)
root.rejected = this.invitees.filter(i -> i.mood < 0.5)
```

Both filtered versions reference the original unchanged array, demonstrating the immutability advantage.

### Error Handling

Failed Bloblang mappings keep messages unchanged while logging errors and flagging them as failed, supporting standard error handling patterns. Bloblang includes built-in fallback mechanisms for preventing failures.

## Practical Examples

### Example 1: Fan Filtering

**Input:**
```json
{
  "id":"foo",
  "description":"a show about foo",
  "fans":[
    {"name":"bev","obsession":0.57},
    {"name":"grace","obsession":0.21},
    {"name":"ali","obsession":0.89},
    {"name":"vic","obsession":0.43}
  ]
}
```

**Configuration:**
```yaml
pipeline:
  processors:
    - mapping: |
        root.id = this.id
        root.fans = this.fans.filter(fan -> fan.obsession > 0.5)
```

**Output:** Retains ID and fans scoring above 0.5 obsession threshold.

### Example 2: Geographic Data Aggregation

**Input:**
```json
{
  "locations": [
    {"name": "Seattle", "state": "WA"},
    {"name": "New York", "state": "NY"},
    {"name": "Bellevue", "state": "WA"},
    {"name": "Olympia", "state": "WA"}
  ]
}
```

**Configuration:**
```yaml
pipeline:
  processors:
    - mapping: |
        root.Cities = this.locations.
                        filter(loc -> loc.state == "WA").
                        map_each(loc -> loc.name).
                        sort().join(", ")
```

**Output:** `{"Cities": "Bellevue, Olympia, Seattle"}`

## Related Components

The mapping processor is functionally equivalent to the Bloblang processor, which faces deprecation in future releases. For minor document alterations, consider the mutation processor as a more efficient alternative.
