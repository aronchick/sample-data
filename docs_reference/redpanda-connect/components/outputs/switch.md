# Switch Output Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/outputs/switch/

## Overview

The switch output enables message routing to different destinations based on content evaluation using Bloblang queries.

## Basic Configuration

```yaml
output:
  switch:
    cases:
      - check: this.type == "order"
        output:
          kafka:
            addresses: ["localhost:9092"]
            topic: orders
      - check: this.type == "user"
        output:
          kafka:
            addresses: ["localhost:9092"]
            topic: users
      - output:
          kafka:
            addresses: ["localhost:9092"]
            topic: other
```

## Configuration Fields

### `cases` (array, required)
Array of routing rules with checks and target outputs.

### `cases[].check` (string, optional)
Bloblang boolean query. Empty check = always passes.

### `cases[].output` (object, required)
Target output configuration.

### `cases[].continue` (boolean, default: false)
Routes message through subsequent cases if true.

### `retry_until_success` (boolean, default: false)
Indefinitely retries failed sends when enabled.

### `strict_mode` (boolean, default: false)
Reports errors when no case matches. Default drops unmatched messages.

## Use Cases

### Content-Based Routing

Route messages by type to different systems:

```yaml
output:
  switch:
    cases:
      - check: this.priority == "high"
        output:
          amqp_0_9:
            urls: ["amqp://localhost:5672/"]
            exchange: priority_events
      - check: this.region == "eu"
        output:
          gcp_pubsub:
            project: my-project
            topic: eu-events
      - check: this.region == "us"
        output:
          redis_streams:
            url: redis://localhost:6379
            stream: us-events
      - output:
          file:
            path: /var/log/unrouted.jsonl
```

### Multi-Destination with Continue

Allow overlapping conditions - "a message that passes both the first case as well as the second will be routed to both":

```yaml
output:
  switch:
    cases:
      - check: this.type == "transaction"
        continue: true
        output:
          kafka:
            addresses: ["localhost:9092"]
            topic: all-transactions
      - check: this.amount > 10000
        output:
          kafka:
            addresses: ["localhost:9092"]
            topic: large-transactions
```

### Severity-Based Routing

```yaml
output:
  switch:
    cases:
      - check: this.severity == "critical"
        output:
          http_client:
            url: https://pagerduty.example.com/webhook
            verb: POST
      - check: this.severity == "warning"
        output:
          slack:
            url: ${SLACK_WEBHOOK_URL}
      - output:
          file:
            path: /var/log/info.jsonl
```

## Error Handling

Messages failing all cases are dropped unless `strict_mode: true` is configured:

```yaml
output:
  switch:
    strict_mode: true
    cases:
      - check: this.valid == true
        output:
          kafka:
            addresses: ["localhost:9092"]
            topic: valid-events
```

When `strict_mode` is enabled, unmatched messages trigger nacking/reprocessing at the input level.

## With Processors Per Case

```yaml
output:
  switch:
    cases:
      - check: this.type == "order"
        output:
          kafka:
            addresses: ["localhost:9092"]
            topic: orders
        processors:
          - mapping: |
              root = this.without("internal_fields")
      - check: this.type == "audit"
        output:
          aws_s3:
            bucket: audit-logs
            path: ${! timestamp_unix() }.json
        processors:
          - mapping: |
              root = this
              root.archived_at = now()
```
