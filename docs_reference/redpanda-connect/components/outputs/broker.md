# Broker Output Component Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/outputs/broker/

## Overview

The broker output component enables message routing to multiple child outputs using various brokering patterns. It's available in both Cloud and Self-Managed Redpanda deployments.

## Configuration Structure

### Basic Configuration
```yaml
outputs:
  broker:
    pattern: fan_out
    outputs: []  # Required
    batching:
      count: 0
      byte_size: 0
      period: ""
```

### Advanced Configuration
```yaml
outputs:
  broker:
    copies: 1
    pattern: fan_out
    outputs: []
    batching:
      count: 0
      byte_size: 0
      period: ""
      check: ""
      processors: []
```

## Key Configuration Fields

**copies** (int, default: 1): Number of instances to spawn for each configured output.

**pattern** (string, default: fan_out): Determines message allocation strategy. Options include `fan_out`, `fan_out_fail_fast`, `fan_out_sequential`, `fan_out_sequential_fail_fast`, `round_robin`, and `greedy`.

**outputs[]** (array): List of child outputs for message routing.

**batching**: Configures batch flushing policies with count, byte size, period, and conditional triggers.

## Brokering Patterns

### fan_out
"All outputs will be sent every message that passes through Redpanda Connect in parallel." Back pressure from any output blocks subsequent messages. Failed messages retry continuously. Use `drop_on` wrapper to prevent blocking.

### fan_out_fail_fast
Parallel delivery like fan_out, but "output failures will not be automatically retried," reducing duplication risk but requiring careful monitoring.

### fan_out_sequential
Sequential parallel delivery where "an output is only written to once the preceding output has confirmed receipt." Maintains message order across outputs with automatic retries.

### fan_out_sequential_fail_fast
Sequential delivery variant without automatic retry on failures, offering faster throughput with duplication risks.

### round_robin
"Each message will be assigned a single output following their order." Failed messages attempt with the next output sequentially.

### greedy
"Each message is sent to a single output" determined by output readiness. "Faster outputs potentially processing more messages" at the cost of uneven distribution.

## Processor Integration

Processors can be applied at individual output or global levels:
```yaml
broker:
  outputs:
    - resource: foo
    - resource: bar
      processors:
        - resource: bar_processor
  processors:
    - resource: general_processor
```

## Usage Example: Fan-Out to Multiple Destinations

```yaml
output:
  broker:
    pattern: fan_out
    outputs:
      - kafka:
          addresses: ["localhost:9092"]
          topic: processed_events
      - s3:
          bucket: my-archive
          path: "events/${!timestamp_unix()}.json"
      - http_client:
          url: https://api.example.com/events
          verb: POST
```

This configuration sends every message to Kafka, S3, and an HTTP endpoint simultaneously.
