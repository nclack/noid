# Transforms

A LinkML-based Python library for defining coordinate transformations with self-describing parameters.

## Overview

This directory contains the complete transforms library, including LinkML schema definitions, enhanced Python API, comprehensive tests, and examples. The library uses LinkML as the source of truth for defining coordinate transformations including identity, translation, scale, axis mapping, homogeneous matrices, and lookup table transforms.

## Directory Structure

```
transforms/
├── README.md                    # This file
├── transforms.linkml.yaml       # Main transforms schema (SOURCE OF TRUTH)
├── samplers.linkml.yaml         # Sampler configuration schema
├── build.py                     # Build script for generating artifacts
├── _out/                        # Generated files from LinkML schemas
│   ├── transforms.py            # Generated Python classes
│   ├── transforms.schema.json   # Generated JSON Schema
│   ├── transforms.context.jsonld # Generated JSON-LD context
│   ├── samplers.py              # Generated sampler classes
│   └── docs/                    # Generated documentation
├── src/                         # Enhanced Python library
│   └── transforms/              # User-friendly API
├── tests/                       # Test suite
├── examples/                    # Example transform data
│   ├── examples.json            # JSON examples
│   ├── examples.yaml            # YAML examples
│   ├── examples.toml            # TOML examples
│   ├── jsonld_examples.json     # JSON-LD examples
│   ├── sequence_examples.jsonld # Transform sequence examples
│   └── usage_examples.py        # Python usage examples
├── docs/                        # Human-readable documentation
└── _old/                        # Legacy files (ignore)
```

## Key Files

- **LinkML Schemas** (`*.linkml.yaml`): The authoritative schema definitions
- **Generated Artifacts** (`_out/`): Auto-generated from LinkML schemas
- **Enhanced Library** (`src/transforms/`): User-friendly Python API
- **Examples** (`examples/`): Sample transform data in various formats
- **Build Script** (`build.py`): Generates all artifacts from LinkML schemas

## Transform Types

The schema defines several transform types with self-describing parameters:

- **Identity**: `"identity"` - No transformation
- **Translation**: `{"translation": [x, y, z]}` - Translation vector
- **Scale**: `{"scale": [sx, sy, sz]}` - Scale factors
- **MapAxis**: `{"mapAxis": [1, 0, 2]}` - Axis permutation
- **Homogeneous**: `{"homogeneous": [[...], [...], ...]}` - Matrix transformation
- **Lookup Tables**: Path-based displacement and coordinate transforms

## Usage

1. **Schema Development**: Edit `*.linkml.yaml` files as the source of truth
2. **Generate Artifacts**: Run `python build.py` to generate all derived files
3. **Use Library**: Import from `src/transforms/` for enhanced Python API
4. **Validate Data**: Use generated schemas and LinkML validation tools

## Build Process

The build process generates multiple artifacts from LinkML schemas:

```bash
python build.py
```

This creates:
- Python classes with LinkML runtime support
- JSON Schema for validation
- JSON-LD context for semantic web compatibility
- Documentation in multiple formats

## Installation

Install the library in development mode:

```bash
pip install -e .
```

## Quick Start

```python
import transforms

# Create transforms using factory functions
translation = transforms.create_translation([10, 20, 5])
scale = transforms.create_scale([2.0, 1.5, 0.5])
identity = transforms.create_identity()

# Create from dictionaries
homogeneous = transforms.from_dict({
    "homogeneous": [
        [2.0, 0, 0, 10],
        [0, 1.5, 0, 20],
        [0, 0, 0.5, 5],
        [0, 0, 0, 1]
    ]
})

# Serialize to JSON-LD
json_ld = transforms.to_jsonld(translation)

# Validate transforms
transforms.validate(translation)
```

## Dependencies

- LinkML for schema definition and generation
- LinkML runtime for Python class generation
- Pydantic for enhanced validation
- JSON-LD context support for semantic serialization