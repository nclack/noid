# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

This is Nathan's opinionated imaging data library (noid) - an experimental
project for developing standards and recommendations for organizing scientific
datasets involving multidimensional arrays. Metadata describing these datasets
is stored as JSON-LD.

The focus is on modeling bioimaging data sets with spatial annotations for
machine learning applications.

The approach is to identify composable vocabularies so that the schema is
flexible and extensible. Schema development is tightly coupled with developing
a library that helps with validation, dataset creation, and deserializtion.

A key way of testing this is to understand how geospatial data can be integrated
into the schema, though geospatial data is not the primary focus of this
project.

## Repository Structure

The noid repository is organized as a multi-package structure using uv workspaces:

```
noid/
├── packages/
│   ├── noid-registry/           # Generic JSON-LD registry system
│   └── noid-transforms/         # Transform-specific functionality  
├── pyproject.toml              # Workspace configuration
└── uv.lock                     # Workspace lockfile
```

### Package Details

**noid-registry** (generic reusable components):
- Registry system for mapping JSON-LD IRIs to factory functions
- Namespace abbreviation system for clean JSON-LD output
- JSON-LD processing utilities (expand, compact, from_jsonld, to_jsonld)
- PyLD data adapter for normalizing PyLD output
- Dependencies: rdflib, pyld, typing-extensions

**noid-transforms** (domain-specific):
- LinkML-based coordinate transformation models
- Factory functions for creating transforms
- Validation utilities
- Depends on noid-registry via workspace reference
- Dependencies: linkml, linkml-runtime, pydantic, noid-registry

### Development Setup

- Use `uv sync` in root to set up workspace environment
- All tests pass: noid-registry (33 tests), noid-transforms (99 tests)
- Workspace dependencies automatically resolve between packages
- Use `uv run pytest packages/{package-name}/tests/` to test individual packages

### Future Package Candidates

Based on project needs, potential future packages:
- **noid-spaces**: Coordinate spaces vocabulary (CoordinateSpace, Dimension classes)
- **noid-core**: Shared utilities and base classes
- Other domain-specific vocabularies as needed

## Core Architecture

The project is organized around several key components:

**Schema Development**: LinkML vocabularies and schemas
define the core data model for multidimensional arrays and relational
model.

**Transform Vocabularies**: Located in `packages/noid-transforms/`, these define
controlled vocabularies for geometric transformations.

**Coordinate Space Vocabularies**: The coordinate spaces vocabulary defines
CoordinateSpace and Dimension classes. Dimensions have name, unit, and type
properties where type can be "space", "time", or "other". Units for space/time
dimensions should use UDUNITS-2 terms, while "index" and "arbitrary" are valid
for all types. Transforms link to coordinate spaces via "input" and "output"
properties.

## References

- [ome-ngff v0.5 schemas](https://github.com/ome/ngff/tree/v0.5/schemas)
- [zarr v3 specification](https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html)
- [RFC-5 Coordinate systems and transformations](https://github.com/ome/ngff/blob/main/rfc/5/index.md)
- [JSON-LD 1.1 spec](https://www.w3.org/TR/json-ld11)
- [LinkML](https://linkml.io/linkml/)
