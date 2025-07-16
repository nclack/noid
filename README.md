# noid - Nathan's opinionated imaging data library

This is an exploratory project to validate ideas and develop some design recommendations around imaging data.
This project explores ideas around standardizing how we describe and relate scientific imaging data.

## Features

- linkml vocabularies for coordinate spaces, transformations, and other data entities
- Support for common transform types (identity, translation, scale, etc.)
- Pydantic models for schema validation
- Support for json-ld

# Organization

A dataset is described using a combination of linkml-based schemas. They are:

* transforms - a vocabulary of transformations described by their parameters.
* coordinate spaces - a schema for describing coordinate spaces and coordinate transforms. This depends on the transforms vocabulary.
* data sources - a schema for specifying where data is stored for different spatial data (arrays, tables, points, meshes, etc.)
* data set - a schema for combining the different peices and describing the relationships between them.

Each of these component pieces is developed as a (a) linkml schema that acts as a source-of-truth specifying the data types and their representation in json-ld and (b) a python package that provides an api for working with data and validating it against the schema.

The python code is partially generated from the linkml schemas using `datamodel-codegen`.

## Examples

* channel metadata, time series, bounding boxes, etc.