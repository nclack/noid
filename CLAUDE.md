# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

This is Nathan's opinionated imaging data library (noid) - an experimental
project for developing standards and recommendations for organizing scientific
datasets involving multidimensional arrays. The project focuses on creating
JSON-LD vocabularies and schemas for describing relationships between zarr-based
arrays and croissant datasets.

The focus is on modeling bioimaging data sets with spatial annotations for
machine learning applications.

The approach is to identify composable vocabularies so that the schema is
flexible and extensible. A key way of testing this is to understand how
geospatial data can be integrated into the schema, though geospatial data is not
the primary focus of this project.

The aim is to build on croissant. In particular a croissant `distribution`
should be used to point to collections of arrays in `ome-zarr` files.
`RecordSets` should be used to define relationships between arrays, annotations,
and other data entities.

## Core Architecture

The project is organized around several key components:

**Schema Development**: JSON-LD vocabularies and schemas in `/schemas/`
define the core data model for multidimensional arrays with rich relational
metadata. Two core vocabularies have been implemented:
- `/schemas/transforms/vocabulary.ttl` - Transform types and parameters
- `/schemas/coordinate_spaces.ttl` - Coordinate spaces and dimensions

**Transform Vocabularies**: Located in `/schemas/transforms/`, these define
controlled vocabularies for coordinate transformations. The vocabulary includes
9 transform types: identity, translation, scale, mapAxis, homogeneous (for both
affine and projective), rotation, sequence, displacements, and coordinates.
Each transform uses self-describing parameters (e.g., "translation", "scale",
"matrix") with JSON-LD context enabling type inference from property presence.

**Coordinate Space Vocabularies**: The coordinate spaces vocabulary defines
CoordinateSpace and Dimension classes. Dimensions have name, unit, and type
properties where type can be "space", "time", or "other". Units for space/time
dimensions should use UDUNITS-2 terms, while "index" and "arbitrary" are valid
for all types. Transforms link to coordinate spaces via "input" and "output"
properties.

**Documentation**: `/docs/` contains design documents, examples, and development
notes. Key documents include:
- `/docs/coordinate_spaces_design.md` - Design decisions for coordinate spaces

**Examples**: `/examples/` contains croissant datasets and display scripts:
- `transforms.json` - Croissant dataset with transform examples
- `coordinate_spaces.json` - Croissant dataset with coordinate space examples  
- `coordinate_transforms.json` - Combined examples showing (input, output, transform) triples
- Python display scripts using Rich library for colorized output

**Python Library**: Minimal Python package structure with `pyproject.toml`.
Dependencies include `mlcroissant` for dataset handling and `rich` for display
formatting. Requires Python 3.10+.

## Development Commands

**Python Environment**: ```bash # Run Python code using uv uv run python -c
"import noid; print('Hello from noid!')"

# Install in development mode uv pip install -e . ```

**Schema Validation**: For croissant files, schema validation should be
done using `mlcroissant.validate`. Non-croissant JSON-LD examples  should be
validated using `jsonschema`.

## Key Design Concepts

**Coordinate Spaces**: Coordinate spaces are collections of dimensions with
JSON array representation. Each dimension has name, unit, and type properties.
Dimension types are "space" (spatial), "time" (temporal), or "other" 
(channels, indices, etc.). Units for space/time dimensions should use UDUNITS-2
terms (micrometers, seconds, radians, etc.), while "index" and "arbitrary" are
valid for all dimension types. Every array has two implicit coordinate spaces
("/coordinates" and "/values") that are handled at the application level, not
modeled explicitly in the vocabulary.

**Transforms**: Coordinate transformations are defined as (input space, output
space, transform definition) triples using controlled vocabularies. Transform
types use self-describing parameters - the property name matches the transform
type (e.g., "translation", "scale", "matrix"). JSON-LD context enables type
inference without explicit "type" fields.

**Relational Extensions**: The project extends beyond traditional array formats
by adding rich relational metadata linking arrays to external tables and
category schemes.

**Croissant Integration**: The schemas are designed to work within the MLCommons
Croissant framework for dataset description while adding multidimensional array
capabilities.

## References

- [croissant schema
- (ttl)](https://raw.githubusercontent.com/mlcommons/croissant/refs/heads/main/d
- ocs/croissant.ttl) [croissant
- specification](https://docs.mlcommons.org/croissant/docs/croissant-spec.html)
- [ome-ngff v0.5 schemas](https://github.com/ome/ngff/tree/v0.5/schemas) [zarr v3
- specification](https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html)
- [RFC-5 Coordinate systems and
- transformations](https://github.com/ome/ngff/blob/main/rfc/5/index.md)
