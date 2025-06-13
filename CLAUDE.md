# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Nathan's opinionated imaging data library (noid) - an experimental project for developing standards and recommendations for organizing scientific datasets involving multidimensional arrays. The project focuses on creating JSON-LD vocabularies and schemas for describing relationships between zarr-based arrays and croissant datasets.

## Core Architecture

The project is organized around several key components:

**Schema Development**: JSON-LD vocabularies and schemas in `/schemas/` define the core data model for multidimensional arrays with rich relational metadata. The main vocabulary is `mdarray.json` which defines coordinate spaces, transforms, and dimensional relationships.

**Transform Vocabularies**: Located in `/schemas/transforms/`, these define controlled vocabularies for coordinate transformations between named coordinate spaces. The TTL vocabulary defines transform types (affine, translation, scale, etc.) with their parameters.

**Documentation**: `/docs/` contains design documents, examples, and development notes. Key files include `design.md` for the overall approach and `coordinate-spaces-transforms-examples.md` for practical usage patterns.

**Python Library**: A minimal Python package structure exists with basic setup in `pyproject.toml` and source in `/src/`.

## Development Commands

**Python Environment**:
```bash
# Run Python code using uv
uv run python -c "import noid; print('Hello from noid!')"

# Install in development mode
uv pip install -e .
```

**Schema Validation**: There are no automated validation tools currently set up. Schema validation should be done manually or by implementing custom validators for the JSON-LD vocabularies.

## Key Design Concepts

**Coordinate Spaces**: Every array has an implicit coordinate space where dimensions use "index" units. Named coordinate spaces can be defined with physical units (micrometers, seconds, etc.).

**Transform Triples**: Coordinate transformations are defined as (input space, output space, transform definition) triples using controlled vocabularies.

**Relational Extensions**: The project extends beyond traditional array formats by adding rich relational metadata linking arrays to external tables and category schemes.

**Croissant Integration**: The schemas are designed to work within the MLCommons Croissant framework for dataset description while adding multidimensional array capabilities.

## Schema Organization

The vocabulary follows a modular approach:
- Core multidimensional array concepts in `mdarray.json`
- Transform-specific vocabulary in `transforms/vocabulary.ttl`
- Example usage patterns demonstrate integration with croissant datasets
- Schemas support inheritance from formats like OME-NGFF while adding relational extensions