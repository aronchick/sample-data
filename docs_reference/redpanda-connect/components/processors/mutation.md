# Mutation Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/mutation/

## Overview

The mutation processor executes Bloblang mappings to directly transform message contents. Introduced in version 4.5.0, available in both Cloud and Self-Managed deployments.

## Basic Configuration

```yaml
pipeline:
  processors:
    - mutation: |
        root.processed = true
        root.timestamp = now()
```

## Configuration Fields

### `label` (string, optional)
Identifier for the processor.

### `mutation` (string, required)
Bloblang mapping expression.

## Key Characteristics

### Mutability Advantage

"A mutation is a mapping that transforms input documents directly, this has the advantage of reducing the need to copy the data fed into the mapping."

This makes mutations more memory-efficient than standard mappings when modifying documents in place.

### Execution Order Consideration

Because the referenced document changes throughout execution, the order of operations matters:

```yaml
# Be careful: filtering the same array twice yields different results
- mutation: |
    root.items = this.items.filter(i -> i.price > 100)
    root.expensive = this.items.filter(i -> i.price > 500)  # Uses already-filtered array!
```

Mitigate by capturing original values:

```yaml
- mutation: |
    let original_items = this.items
    root.items = $original_items.filter(i -> i.price > 100)
    root.expensive = $original_items.filter(i -> i.price > 500)
```

## When to Use

**Use mutation when:**
- Output documents maintain mostly the same structure as input
- You're modifying fields in place
- Memory efficiency is important

**Use mapping when:**
- Creating entirely new document shapes
- Complete restructuring is needed

## Error Handling

Bloblang mapping failures log errors and flag messages as failed, enabling standard error handling patterns. Use `.catch()` for fallback behavior:

```yaml
- mutation: |
    root.parsed_date = this.date_string.ts_parse("2006-01-02").catch(now())
```

## Examples

### Filter and Transform

```yaml
- mutation: |
    root.fans = this.fans.filter(f -> f.obsession_score > 80)
    root.fans = root.fans.map_each(f -> f.without("description"))
```

### Extract and Format

```yaml
- mutation: |
    root.washington_cities = this.cities
      .filter(c -> c.state == "WA")
      .map_each(c -> c.name)
      .join(", ")
```

### Add Computed Fields

```yaml
- mutation: |
    root.item_count = this.items.length()
    root.total_value = this.items.map_each(i -> i.price * i.quantity).sum()
    root.processed_at = now()
```

### Conditional Updates

```yaml
- mutation: |
    root.status = if this.score > 90 {
      "excellent"
    } else if this.score > 70 {
      "good"
    } else {
      "needs_improvement"
    }
```
