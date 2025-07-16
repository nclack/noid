# NOID Schema Organization

This directory contains the schema definitions for NOID (N-dimensional Objects with Identifiers and Data).

## Directory Structure

Each schema is organized in its own directory:

```
schemas/
├── transforms/
│   ├── transforms.linkml         # Source schema (hand-written)
│   ├── _out/                     # Generated files (JSON schema, JSON-LD context, Python)
│   └── docs/                     # Hand-written documentation
├── spaces/
│   ├── spaces.linkml
│   ├── _out/
│   └── docs/
└── dataset/
    ├── dataset.linkml
    ├── _out/
    └── docs/
```

## File Types

- **`*.linkml`** - Source schema files (edit these)
- **`_out/`** - Generated artifacts (don't edit these)
- **`docs/`** - Hand-written documentation