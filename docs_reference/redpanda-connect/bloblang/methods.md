# Bloblang Methods Reference

> Source: https://docs.redpanda.com/redpanda-connect/guides/bloblang/methods/

Bloblang methods augment values and chain together in expressions. They support both named and nameless argument styles.

## General Methods

### `apply(mapping: string)`
Executes a declared mapping on a target value, useful for reusable transformations.

### `catch(fallback: query)`
Returns fallback value if target query fails (type errors, parsing failures, etc.).
- **Use Case:** Error recovery, default values

### `exists(path: string)`
Checks if a dot-path field exists in an object, returning boolean.

### `from(index: integer)`
Executes functions from perspective of another message in batch.

### `from_all()`
Executes functions across all batch messages, returning results as array.

### `or(fallback: query)`
Returns fallback if target fails or resolves to null.

## String Manipulation Methods

### `capitalize()`
Maps Unicode letters beginning words to title case.

### `compare_argon2(hashed_secret: string)`
Verifies string against Argon2 hash.

### `compare_bcrypt(hashed_secret: string)`
Verifies string against bcrypt hash.

### `contains(value: unknown)`
Checks if string contains substring.

### `escape_html()`
Escapes `<`, `>`, `&`, `'`, `"` for safe HTML placement.

### `escape_url_query()`
Escapes string for URL query parameters.

### `filepath_join()`
Joins path elements into OS-appropriate file path.

### `filepath_split()`
Splits path into directory and filename components.

### `format(...args)`
Uses string as format specifier (Go fmt syntax).

### `has_prefix(value: string)`
Returns boolean indicating prefix match.

### `has_suffix(value: string)`
Returns boolean indicating suffix match.

### `index_of(value: string)`
Returns starting index of substring or -1.

### `length()`
Returns string length.

### `lowercase()`
Converts to lowercase.

### `quote()`
Quotes with escape sequences for control characters.

### `replace_all(old: string, new: string)`
Replaces all occurrences.

### `replace_all_many(values: array)`
Chains multiple replacements efficiently.

### `repeat(count: integer)`
Returns string repeated N times.

### `reverse()`
Returns string in reverse order.

### `slice(low: integer, high?: integer)`
Extracts substring slice (negative indices supported).

### `slug(lang?: string)`
Creates URL-friendly slug (beta, supports language parameter).

### `split(delimiter: string)`
Splits into array by delimiter.

### `strip_html(preserve?: array)`
Removes HTML tags with optional element preservation.

### `trim(cutset?: string)`
Removes leading/trailing characters (default: whitespace).

### `trim_prefix(prefix: string)`
Removes leading prefix substring.

### `trim_suffix(suffix: string)`
Removes trailing suffix substring.

### `unescape_html()`
Unescapes HTML entities to characters.

### `unescape_url_query()`
Expands URL query escape sequences.

### `unicode_segments(type: string)`
Splits into sentences/graphemes/words using Unicode rules (beta).

### `unquote()`
Unquotes and expands escape sequences.

### `uppercase()`
Converts to uppercase.

## Regular Expression Methods

### `re_find_all(pattern: string)`
Returns array of all successive matches.

### `re_find_all_object(pattern: string)`
Returns matches with named/indexed groups.

### `re_find_all_submatch(pattern: string)`
Returns nested arrays of matches and subexpressions.

### `re_find_object(pattern: string)`
Returns first match with groups.

### `re_match(pattern: string)`
Returns boolean for pattern match anywhere in string.

### `re_replace_all(pattern: string, value: string)`
Replaces with submatch expansion support ($1, etc.).

## Number Manipulation Methods

### `abs()`
Returns absolute value (int64 or float64).

### `bitwise_and(value: integer)`
Bitwise AND operation.

### `bitwise_or(value: integer)`
Bitwise OR operation.

### `bitwise_xor(value: integer)`
Bitwise XOR operation.

### `ceil()`
Returns least integer >= value.

### `cos()`
Calculates cosine (radians).

### `float32()` / `float64()`
Converts to 32-bit or 64-bit float.

### `floor()`
Returns greatest integer <= value.

### `int8()` / `int16()` / `int32()` / `int64()`
Converts to signed integer variants.

### `log()`
Returns natural logarithm.

### `log10()`
Returns base-10 logarithm.

### `max()`
Returns largest value in array.

### `min()`
Returns smallest value in array.

### `pow(exponent: float)`
Raises number to exponent power.

### `round()`
Rounds to nearest integer (half away from zero).

### `sin()`
Calculates sine (radians).

### `tan()`
Calculates tangent (radians).

### `uint8()` / `uint16()` / `uint32()` / `uint64()`
Converts to unsigned integer variants.

## Timestamp Manipulation Methods

### `parse_duration()`
Parses duration string ("300ms", "1.5h") to nanoseconds.

### `parse_duration_iso8601()`
Parses ISO-8601 duration ("P3Y6M4DT12H30M5S") to nanoseconds (beta).

### `ts_add_iso8601(duration: string)`
Adds ISO 8601 period to timestamp (beta).

### `ts_format(format?: string, tz?: string)`
Formats timestamp using Go time layout (default RFC 3339) (beta).

### `ts_parse(format: string)`
Parses string as timestamp using Go time layout (beta).

### `ts_round(duration: integer)`
Rounds timestamp to nearest duration multiple (nanoseconds) (beta).

### `ts_strftime(format: string, tz?: string)`
Formats using strftime syntax (beta).

### `ts_strptime(format: string)`
Parses using strptime syntax (beta).

### `ts_sub(t2: timestamp)`
Returns nanosecond difference between timestamps (beta).

### `ts_sub_iso8601(duration: string)`
Subtracts ISO 8601 period (beta).

### `ts_tz(tz: string)`
Converts to specified timezone (beta).

### `ts_unix()` / `ts_unix_micro()` / `ts_unix_milli()` / `ts_unix_nano()`
Formats as unix timestamp in various precisions (beta).

## Type Coercion Methods

### `array()`
Wraps value in array (no-op if already array).

### `bool(default?: bool)`
Parses value to boolean with optional fallback.

### `bytes()`
Marshals value to byte array.

### `not_empty()`
Ensures string/array/object not empty, errors otherwise.

### `not_null()`
Ensures value not null, errors otherwise.

### `number(default?: float)`
Parses value to number with optional fallback.

### `string()`
Marshals value to string.

### `timestamp(default?: timestamp)`
Parses to timestamp (unix seconds or RFC 3339 format).

### `type()`
Returns type string: "string", "bytes", "number", "bool", "timestamp", "array", "object", "null".

## Object & Array Manipulation Methods

### `all(test: query)`
Returns true if all elements pass test query.

### `any(test: query)`
Returns true if any element passes test query.

### `append(...values)`
Appends elements to array.

### `assign(with: unknown)`
Merges object, overwriting destination on collision.

### `collapse(include_empty?: bool)`
Flattens to key/value pairs using dot notation (default: excludes empty).

### `concat(...arrays)`
Concatenates arrays.

### `contains(value: unknown)`
Checks if array/object contains value.

### `diff(other: unknown)`
Creates diff comparing current with given value (beta).

### `enumerated()`
Converts array to objects with "index" and "value" fields.

### `explode(path: string)`
Explodes array/object at field path into multiple documents.

### `filter(test: query)`
Removes elements where test returns non-true value.

### `find(value: unknown)` / `find_all(value: unknown)`
Returns index of first match or all matching indices (beta).

### `find_by(query: query)` / `find_all_by(query: query)`
Returns indices where query resolves true (beta).

### `flatten()`
Removes nested arrays, inserting elements directly.

### `fold(initial: unknown, query: query)`
Accumulates value across elements using query.

### `get(path: string)`
Extracts field value by dot path.

### `index(index: integer)`
Extracts array element (supports negative indices).

### `join(delimiter?: string)`
Joins string array with delimiter.

### `json_path(expression: string)`
Executes JSONPath expression (experimental).

### `json_schema(schema: string)`
Validates value against JSON schema (beta).

### `key_values()`
Returns key/value pairs as array of objects.

### `keys()`
Returns object keys as array.

### `length()`
Returns array length or object key count.

### `map_each(query: query)`
Maps query over each element/value.

### `map_each_key(query: query)`
Maps query over object keys.

### `merge(with: unknown)`
Merges object, combining values as arrays on collision.

### `patch(changelog: unknown)`
Applies changelog diff (beta).

### `slice(low: integer, high?: integer)`
Extracts array slice (negative indices supported).

### `sort(compare?: query)` / `sort_by(query: query)`
Sorts array with optional custom comparator or by query result.

### `squash()`
Squashes object array into single object (merges on key collision).

### `sum()`
Sums numerical array values.

### `unique(emit?: query)`
Removes duplicates with optional uniqueness query.

### `values()`
Returns object values as array.

### `with(...paths)`
Returns object with only specified dot-path fields retained.

### `without(...paths)`
Returns object with specified dot-path fields removed.

### `zip(...arrays)`
Zips arrays together into nested arrays.

## Parsing Methods

### `bloblang(mapping: string)`
Executes dynamic Bloblang mapping (beta, no environment access).

### `format_json(indent?: string, no_indent?: bool, escape_html?: bool)`
Pretty-prints as JSON (beta).

### `format_msgpack()`
Formats as MessagePack bytes.

### `format_xml(indent?: string, no_indent?: bool)`
Serializes as XML (beta).

### `format_yaml()`
Serializes as YAML (beta).

### `infer_schema()`
Infers schema structure.

### `parse_csv(parse_header_row?: bool, delimiter?: string, lazy_quotes?: bool)`
Parses CSV format.

### `parse_form_url_encoded()`
Parses x-www-form-urlencoded query string.

### `parse_json(use_number?: bool)`
Parses JSON string.

### `parse_msgpack()`
Parses MessagePack bytes.

### `parse_parquet(byte_array_as_string?: bool)`
Decodes Parquet file to row objects.

### `parse_url()`
Parses URL into structured components.

### `parse_xml(cast?: bool)`
Parses XML with optional type casting.

### `parse_yaml()`
Parses YAML document string.

## Encoding & Encryption Methods

### `compress(algorithm: string, level?: integer)`
Compresses using flate/gzip/pgzip/lz4/snappy/zlib/zstd.

### `decode(scheme: string)`
Decodes base64/hex/ascii85 to byte array.

### `decompress(algorithm: string)`
Decompresses gzip/zlib/bzip2/flate/snappy/lz4/zstd.

### `encode(scheme: string)`
Encodes byte array to base64/hex/ascii85.

### `hash(algorithm: string)`
Hashes using md5/sha1/sha256/sha512/sha3_256/sha3_512/blake2b/blake2s.
