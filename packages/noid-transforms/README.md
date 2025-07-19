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

The build process also includes:
- Code linting and type checking (via ruff)
- Test execution
- Example validation
- Code formatting verification

## Quality Checks

The project uses pre-commit hooks to ensure code quality. All checks run automatically on commit, but you can also run them manually:

```bash
# Install pre-commit (one-time setup)
pip install pre-commit
pre-commit install

# Run all quality checks manually (same as what runs on commit)
python check.py

# Or run pre-commit directly
pre-commit run --all-files

# Individual checks (if you need them):
ruff check src/              # Linting and type checking
ruff format src/             # Auto-format code
pytest tests/ -v            # Tests only
```

The quality checks include:
- **Linting & Type Checking**: via ruff (includes ANN rules for type annotations)
- **Code Formatting**: via ruff format
- **Tests**: via pytest
- **File Checks**: trailing whitespace, YAML/TOML syntax, etc.

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
homogeneous = transforms.from_data({
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
