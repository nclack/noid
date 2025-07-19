# noid-registry

Generic JSON-LD registry system with namespace support.

This package provides a generic registry pattern for mapping JSON-LD IRIs to factory functions, with support for namespace abbreviations and JSON-LD processing utilities.

## Features

- Generic registry for mapping IRIs to factory functions
- Namespace abbreviation system for cleaner JSON-LD output
- JSON-LD processing utilities (expand, compact, frame)
- Thread-safe registry operations
- Extensible design for different schema types

## Installation

```bash
pip install noid-registry
```

## Usage

```python
from noid_registry import Registry, set_namespace, register

# Set namespace for registrations
set_namespace("https://example.com/schema/")

# Register factory functions
@register("MyType")
def create_my_type(**kwargs):
    return MyType(**kwargs)

# Use registry to create objects
registry = Registry()
obj = registry.create("https://example.com/schema/MyType", {...})
```