# Expanso Pipeline Examples Index

> Source: https://examples.expanso.io/

Production-ready pipeline configurations with downloadable YAML files, step-by-step explanations, and component references.

## Getting Started

| Example | Description |
|---------|-------------|
| Local Development | Setting up local development environment |
| Services (Kafka) | Connecting to Kafka services |

## Data Routing

| Example | Description |
|---------|-------------|
| **Content Routing** | Send the right data to the right place using conditional logic |
| **Circuit Breakers** | Handle downstream failures gracefully |
| **Priority Queues** | Premium users get expedited processing |
| **Fan-Out Pattern** | Broadcast to multiple destinations simultaneously |
| **Content Splitting** | Break large payloads into smaller messages |
| **Smart Buffering** | Buffer messages for batch processing |

### Content Routing Techniques
- **Severity Routing** - Critical alerts to PagerDuty, warnings to Slack, info to logs
- **Geographic Routing** - EU data stays in EU (GDPR compliance)
- **Event Type Routing** - Payments to fraud detection, auth to security systems
- **Priority Queues** - Premium users get expedited processing

## Data Security

| Example | Description |
|---------|-------------|
| **Field-Level Encryption** | Encrypt sensitive fields in transit |
| **Encrypt Sensitive Data** | Protect PII with encryption |
| **Remove PII** | Delete, hash, pseudonymize, or generalize personal data |
| **Enforce Schema Validation** | Validate data structure before processing |

### PII Removal Techniques
- **Deletion** - Remove credit cards, precise coordinates (no analytics value)
- **Hashing** - One-way transform IPs and emails (preserve uniqueness for counting)
- **Pseudonymization** - Replace names with IDs (preserve relationships)
- **Generalization** - Coordinates → city names (preserve regional trends)

## Data Transformation

| Example | Description |
|---------|-------------|
| **Aggregate Time Windows** | Combine events over time periods |
| **Deduplicate Events** | Remove duplicate messages |
| **Normalize Timestamps** | Standardize timestamp formats |
| **Parse Structured Logs** | Extract fields from log messages |
| **Transform Formats** | Convert between JSON, XML, CSV, etc. |

### Deduplication Strategies
- **Hash-Based** - SHA-256 content hashing with in-memory caching for exact matches
- **Fingerprint-Based** - Hash business-critical fields to detect semantic duplicates
- **ID-Based** - Cache event identifiers directly for systems with guaranteed unique IDs
- **Production Configuration** - Redis-backed caching with consistent hashing for multi-node setups

## Log Processing

| Example | Description |
|---------|-------------|
| **Filter by Severity** | Route logs based on severity level |
| **Log Enrichment & S3 Export** | Add context and archive to S3 |
| **Production Pipeline** | Complete production-ready logging pipeline |

## Each Example Includes

- **Interactive Explorer** - Live examples with before/after comparisons
- **Step-by-Step Tutorial** - Incremental pipeline building
- **Complete Pipeline** - Production-ready code available for download
- **Component References** - Links to relevant documentation
