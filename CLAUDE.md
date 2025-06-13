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
metadata. The main vocabulary is `mdarray.json` which defines coordinate spaces,
transforms, and dimensional relationships. Other dependent vocabularies should
be put in subdirectories of `/schemas/`. For example, `/schemas/transforms/`
contains vocabularies for coordinate transformations.

**Transform Vocabularies**: Located in `/schemas/transforms/`, these define
controlled vocabularies for coordinate transformations between named coordinate
spaces. The TTL vocabulary defines transform types (affine, translation, scale,
etc.) with their parameters.

**Documentation**: `/docs/` contains design documents, examples, and development
notes.

**Python Library**: A minimal Python package structure exists with basic setup
in `pyproject.toml` and source in `/src/`.

## Development Commands

**Python Environment**: ```bash # Run Python code using uv uv run python -c
"import noid; print('Hello from noid!')"

# Install in development mode uv pip install -e . ```

**Schema Validation**: For croissant files, schema validation should be
done using `mlcroissant.validate`. Non-croissant JSON-LD examples  should be
validated using `jsonschema`.

## Key Design Concepts

**Coordinate Spaces**: Coordinate spaces are collections of dimensions. Named
coordinate spaces can be defined with physical units corresponding to defined
terms in the UDUNITS-2 ontology(micrometers, seconds, etc.). Each dimension has
a name and a unit. Every array has two implicit coordinate spaces: "coordinates"
and "values". These implicit spaces are referred to by appending `/coordinates`
or `/values` to the array id: e.g. `array0/coordinates` or `array1/values`.

**Transforms**: Coordinate transformations are defined as (input space, output
space, transform definition) triples using controlled vocabularies.

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
