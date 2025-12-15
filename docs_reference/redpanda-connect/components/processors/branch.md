# Branch Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/branch/

## Overview

The `branch` processor enables you to "create a new request message via a Bloblang mapping, execute a list of processors on the request messages, and map the result back" into the original message. This functionality preserves original message content when using processors that would otherwise overwrite it completely.

## Configuration Structure

```yaml
label: ""
branch:
  request_map: ""
  processors: [] # Required
  result_map: ""
```

## Core Fields

### processors[]
A required list of processors applied to mapped requests. When handling message batches, the output batch must match the input batch's size and ordering—filtering and grouping operations are prohibited within these processors.

**Type**: `processor`

### request_map
A Bloblang mapping that constructs a request payload for child processors. When empty, the branch begins with an exact copy of the origin message including metadata.

**Type**: `string` | **Default**: `""`

**Sample configurations:**
```yaml
request_map: |-
  root = {
    "id": this.doc.id,
    "content": this.doc.body.text
  }
```

Supports conditional logic with `deleted()` to skip processing for specific messages:
```yaml
request_map: |-
  root = if this.type == "foo" {
    this.foo.request
  } else {
    deleted()
  }
```

### result_map
A Bloblang mapping describing how processed messages map back into the original payload. When empty, the origin message remains unchanged including metadata.

**Type**: `string` | **Default**: `""`

**Sample configurations:**
```yaml
result_map: |-
  meta foo_code = metadata("code")
  root.foo_result = this
```

Metadata handling examples:
```yaml
result_map: |-
  meta = metadata()
  root.bar.body = this.body
```

## Metadata Handling

Added metadata fields aren't automatically copied. Explicitly declare metadata preservation using `meta = metadata()` for complete copies or selective copies like `meta foo = metadata("bar")`. Reference origin message metadata via the `@` operator within `result_map`.

## Error Handling

- Failed `request_map`: child processors skip execution
- Failed child processors: `result_map` doesn't execute
- Failed `result_map`: message remains unchanged

Standard error handling methods apply across all scenarios.

## Conditional Branching

Setting `request_map` root to `deleted()` skips branch processors for specific messages, enabling conditional processing logic.

## Practical Examples

### HTTP Request Integration
Fetches external data and injects results into original message:
```yaml
pipeline:
  processors:
    - branch:
        request_map: 'root = ""'
        processors:
          - http:
              url: https://hub.docker.com/v2/repositories/jeffail/benthos
              verb: GET
        result_map: root.image.pull_count = this.pull_count
```
Input: `{"id":"foo","some":"pre-existing data"}`
Output: `{"id":"foo","some":"pre-existing data","image":{"pull_count":1234}}`

### Unstructured Results
Uses `content()` function for raw bytes conversion:
```yaml
pipeline:
  processors:
    - branch:
        request_map: 'root = this.document.id'
        processors:
          - cache:
              resource: descriptions_cache
              key: ${! content() }
              operator: get
        result_map: root.document.description = content().string()
```

### Lambda Function Invocation
Triggers external function without modifying original:
```yaml
pipeline:
  processors:
    - branch:
        request_map: '{"id":this.doc.id,"username":this.user.name}'
        processors:
          - aws_lambda:
              function: trigger_user_update
```

### Conditional Caching
Caches documents selectively based on type:
```yaml
pipeline:
  processors:
    - branch:
        request_map: |
          meta id = this.id
          root = if this.type == "foo" {
            this.document
          } else {
            deleted()
          }
        processors:
          - cache:
              resource: TODO
              operator: set
              key: ${! @id }
              value: ${! content() }
```
