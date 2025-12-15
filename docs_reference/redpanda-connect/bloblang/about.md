# Bloblang Language Guide

> Source: https://docs.redpanda.com/redpanda-connect/guides/bloblang/about/

## Overview

Bloblang (blobl) is a specialized language designed for transforming diverse data formats. As described in the documentation, it provides "a safe, fast, and powerful way to perform document mapping within Redpanda Connect." The language supports a Go API for custom plugin development and integrates with Redpanda Connect processors.

## Core Concepts

### Assignment Statements

Bloblang mappings create new documents by extracting and transforming data from input sources. The basic structure uses dot-separated path segments on the left side to specify target fields and right-side queries to define content.

Key keywords:
- `root` - refers to the root of the newly created document
- `this` - references the current query context (input document at mapping root)

**Example transformation:**
```coffeescript
root.id = this.thing.id
root.type = "yo"
content = thing.doc.message
```

Omitting `root` and `this` allows implicit inference. Assigning the input document to the root preserves all existing fields while allowing additions.

### Handling Special Characters

Field paths containing whitespace, dots, or special characters require quotation:

```coffeescript
root."foo.bar".baz = this."buz bev".fub
```

### Processing Unstructured Data

Raw binary or text data can be accessed through the `content()` function, which retrieves raw message bytes. Output can also be unstructured by assigning non-object values to `root`.

### Field Deletion

Remove specific fields using the `deleted()` function:

```coffeescript
root = this
root.bar = deleted()
```

### Variables

Temporary variables can be created with `let` statements and referenced using `$`:

```coffeescript
let foo = "yo"
root.new_doc.type = $foo
```

### Metadata Operations

Message metadata is separate from payload content. The `meta` keyword manages metadata, with `@` or `metadata()` providing access:

```coffeescript
root.new_doc.bar = @kafka_topic
meta bar = "hello world"
root.meta_obj = @
```

## Operators and Logic

### Coalesce Operator

Pipe operators within brackets select the first non-null, existing field:

```coffeescript
root.new_doc.type = this.thing.(article | comment | this).type
```

### Boolean and Arithmetic Operators

Supported operators include:
- Boolean: `!`, `>`, `>=`, `==`, `<`, `<=`, `&&`, `||`
- Mathematical: `+`, `-`, `*`, `/`, `%`

```coffeescript
root.is_big = this.number > 100
root.multiplied = this.number * 7
```

### Conditional Mapping

Use `if` statements or expressions with optional `else if` and `else` clauses:

```coffeescript
root.sorted_foo = if this.foo.type() == "array" { this.foo.sort() }

root.sound = if this.type == "cat" {
  this.cat.meow
} else if this.type == "dog" {
  this.dog.woof.uppercase()
} else {
  "sweet sweet silence"
}
```

### Pattern Matching

The `match` expression enables conditional mapping based on boolean expressions, literal comparisons, or catch-all cases using underscore (`_`):

```coffeescript
root.new_doc = match this.doc {
  this.type == "article" => this.article
  this.type == "comment" => this.comment
  _ => this
}
```

Match expressions can also use literal value comparisons and can omit the target value, leaving context unchanged.

## Data Types

Bloblang supports literal values for:
- Numbers
- Booleans
- Strings (including multi-line with triple quotes)
- Null
- Arrays
- Objects

Literal arrays and objects can contain dynamic query expressions, and object keys can be computed dynamically.

## Comments

Comments begin with `#` and extend to line end:

```coffeescript
root = this.some.value # This is a comment
```

## Functions and Methods

### Functions

Functions extract environmental information, generate values, or access message data. They support both named and positional arguments:

```coffeescript
root.doc.id = uuid_v4()
root.doc.received_at = now()
root.values = range(start: 0, stop: this.max, step: 2)
```

### Methods

Methods operate on target values, providing transformation capabilities. They chain together and support both argument styles:

```coffeescript
root.doc.id = this.thing.id.string().catch(uuid_v4())
root.doc.reduced_nums = this.thing.nums.map_each(num -> if num < 10 {
  deleted()
} else {
  num - 10
})
```

## Advanced Features

### Named Maps

Define reusable mappings with the `map` keyword and apply them using the `apply()` method:

```coffeescript
map things {
  root.first  = this.thing_one
  root.second = this.thing_two
}

root.foo = this.value_one.apply("things")
```

Within maps, `root` refers to the new document and `this` to the original target value.

### Importing Maps

Import maps from external files using `import` statements:

```coffeescript
import "./common_maps.blobl"

root.foo = this.value_one.apply("things")
```

Imports are relative to the running process for configuration files, or to the importing file for nested imports.

### Filtering

Delete entire messages by assigning `deleted()` to root:

```coffeescript
root = if this.doc.urls.length() < 10 { deleted() }
```

### Error Handling

The `catch()` method recovers from function or method failures, returning fallback values:

```coffeescript
root.foo = this.bar.split(",").catch([])
root.thing = (this.foo > this.bar && this.baz.contains("wut")).catch(false)
```

The `or()` method provides fallbacks specifically for null values:

```coffeescript
root.foo = this.bar.index(5).or("default")
```

## CLI Usage

Execute mappings from the command line using:

```shell
cat data.jsonl | rpk connect blobl 'foo.(bar | baz).buz'
```

Each input line must be valid JSON; line breaks determine document boundaries.

## Unit Testing

Bloblang mappings support standard Redpanda Connect unit testing capabilities for validation and regression prevention.
