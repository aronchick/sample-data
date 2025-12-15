# Bloblang Functions Reference

> Source: https://docs.redpanda.com/redpanda-connect/guides/bloblang/functions/

Bloblang functions enable extraction of environmental data, value generation, and access to message content during mapping operations.

## General Functions

### `bytes(length)`
Creates a zero-initialized byte array of specified size.
- **Parameter:** `length` (integer) - Buffer size in bytes
- **Use Case:** Binary data operations requiring fixed-size allocation

### `counter(min, max, set)`
Generates incrementing integers with optional reset logic.
- **Parameters:**
  - `min` (default: 1) - Starting value
  - `max` (default: 9223372036854775807) - Reset point
  - `set` (optional) - Conditional reset mapping
- **Note:** "Experimental; breaking changes possible outside major releases"

### `deleted()`
Marks content for removal/dropping with successful acknowledgment.
- **Use Case:** Conditional field removal or array element filtering
- **Example:** `root.field = deleted()` removes the field

### `pi()`
Returns the mathematical constant π
- **Use Case:** Trigonometric calculations

### `random_int(seed, min, max)`
Generates pseudo-random 64-bit integers.
- **Parameters:**
  - `seed` (optional) - Resolved once per mapping lifetime
  - `min` (default: 0)
  - `max` (default: 9223372036854775806)
- **Note:** Min/max are static only; use modulo for dynamic ranges

### `range(start, stop, step)`
Creates integer arrays within specified bounds.
- **Parameters:**
  - `start` - Beginning value
  - `stop` - Ending value (exclusive)
  - `step` (default: 1) - Increment
- **Example:** `range(0, 10)` produces `[0,1,2,3,4,5,6,7,8,9]`

### `throw(why)`
Abandons mapping with error message.
- **Parameter:** `why` (string) - Error explanation
- **Use Case:** Conditional validation failures

### `ulid(encoding, random_source)`
Generates random ULIDs (experimental).
- **Parameters:**
  - `encoding` (default: "crockford") - "crockford" or "hex"
  - `random_source` (default: "secure_random")

## Identifier Generation

### `uuid_v4()`
Generates RFC-4122 compliant UUIDs

### `uuid_v7(time)`
Creates time-ordered UUIDs.
- **Parameter:** `time` (optional timestamp) - Custom timestamp or current time
- **Use Case:** Data migration/replication timing

### `ksuid()`
Generates sortable unique identifiers

### `nanoid(length, alphabet)`
Produces compact string IDs.
- **Parameters:** Optional custom length and character set

### `snowflake_id(node_id)`
Twitter Snowflake-compatible IDs.
- **Parameter:** `node_id` (default: 1)

## Message Information

### `content()`
Retrieves complete raw message bytes.
- **Example:** `content().string()` converts to string representation

### `batch_index()`
Returns message position within batch (0-based)

### `batch_size()`
Returns total messages in current batch

### `metadata(key)` / `meta(key)`
Accesses input message metadata.
- **Parameter:** `key` (optional) - Specific field or all if omitted
- **Note:** "Reflects the read-only input message; doesn't capture in-map changes"

### `json(path)`
Extracts fields from JSON messages via dot notation.
- **Parameter:** `path` (optional) - Field location or full payload if empty

### Error Handling Functions
- `error()` - Returns error cause or null
- `errored()` - Boolean error status check
- `error_source_label()`, `error_source_name()`, `error_source_path()` - Error origin details

### Tracing Functions (Experimental)
- `tracing_id()` - Message trace identifier
- `tracing_span()` - OpenTelemetry span data

## Environment & File Access

### `env(name, no_cache)`
Retrieves environment variables.
- **Parameters:**
  - `name` (string) - Variable identifier
  - `no_cache` (default: false) - Disable per-invocation caching
- **Note:** Static names cache by default; use `no_cache: true` for runtime changes

### `file(path, no_cache)` / `file_rel(path, no_cache)`
Reads file contents.
- **Difference:** `file_rel` resolves relative to mapping directory
- **Caching:** Default caches; disable with `no_cache: true`

### `hostname()`
Returns machine hostname as string

## Timestamp Functions

### `now()`
Current timestamp in RFC 3339 format with local timezone.
- **Example:** `now().ts_format("Mon Jan 2 15:04:05 -0700 MST 2006", "UTC")`

### `timestamp_unix()`
Unix timestamp in seconds

### `timestamp_unix_milli()`
Unix timestamp in milliseconds

### `timestamp_unix_micro()`
Unix timestamp in microseconds

### `timestamp_unix_nano()`
Unix timestamp in nanoseconds

## Fake Data Generation

### `fake(function)`
Generates synthetic data via faker library.
- **Supported:** latitude, longitude, email, url, name, phone_number, jwt, uuid_hyphenated, ipv4, ipv6, password, and 30+ additional functions
- **Example:** `fake("email")` produces formatted email addresses

## Deprecated Functions

- `count(name)` - Replaced by `counter()`; increments from 1 per identifier
- `meta(key)` - Superseded by `metadata()`
- `root_meta(key)` - Use `@` operator for metadata mutations
