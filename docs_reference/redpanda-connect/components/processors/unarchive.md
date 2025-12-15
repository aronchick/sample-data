# Unarchive Processor Documentation

> Source: https://docs.redpanda.com/redpanda-connect/components/processors/unarchive/

## Overview

The unarchive processor expands archived messages into multiple individual messages within a batch. It supports a variety of archive formats and is available in both Cloud and Self-Managed Redpanda environments.

## Basic Configuration

```yaml
label: ""
unarchive:
  format: "" # No default (required)
```

## Core Functionality

When processing occurs, "the new messages replace the original message in the batch." Messages that cannot be properly unarchived due to invalid formatting remain in the batch but are marked as failed, enabling downstream error handling capabilities.

## Metadata Handling

Metadata from the original message carries forward to all resulting messages. For archive types that include file information (tar, zip formats), an additional `archive_filename` field is automatically populated with the extracted filename.

## Supported Formats

| Format | Purpose |
|--------|---------|
| **binary** | Extracts messages from binary blob data |
| **csv** | Parses CSV files with headers; converts each row to JSON objects |
| **csv:x** | CSV parsing with custom single-character delimiters (e.g., `csv:\t` for tab-separated) |
| **json_array** | Extracts each element from a JSON array |
| **json_documents** | Parses concatenated JSON documents into separate messages |
| **json_map** | Expands JSON map elements into individual messages; adds `archive_key` metadata |
| **lines** | Splits message content by line breaks |
| **tar** | Extracts Unix tape archive contents |
| **zip** | Extracts ZIP file contents |

## Configuration Requirements

The `format` field is mandatory and has no default value—you must explicitly specify which unarchiving method to apply.

## Usage Examples

### Explode JSON Array

```yaml
pipeline:
  processors:
    - unarchive:
        format: json_array
```

Input: `[{"id": 1}, {"id": 2}, {"id": 3}]`
Output: Three separate messages: `{"id": 1}`, `{"id": 2}`, `{"id": 3}`

### Parse CSV to JSON

```yaml
pipeline:
  processors:
    - unarchive:
        format: csv
```

Input:
```
name,age,city
Alice,30,NYC
Bob,25,LA
```

Output: Two messages:
- `{"name": "Alice", "age": "30", "city": "NYC"}`
- `{"name": "Bob", "age": "25", "city": "LA"}`

### Split by Lines

```yaml
pipeline:
  processors:
    - unarchive:
        format: lines
```
