# Coordinate Spaces Specification

## Abstract

This document specifies the JSON Schema for coordinate spaces, dimensions,
and coordinate transformations. The specification defines structured formats
for representing coordinate systems and their transformations used in
multidimensional array processing.

## Status

This document describes the v0 schema for coordinate spaces and coordinate
transformations. The specification is influenced by the [RFC-5 Coordinate 
systems and transformations][RFC-5] specification.

## Table of Contents

1. [Introduction](#introduction)
2. [Terminology](#terminology)
3. [Schema Components](#schema-components)
4. [Schema Requirements](#schema-requirements)
5. [Examples](#examples)
6. [Security Considerations](#security-considerations)

## 1. Introduction

Coordinate spaces provide a structured way to describe the dimensions
and coordinate systems associated with multidimensional arrays. This
specification defines three core components: Dimensions, Coordinate Systems,
and Coordinate Transforms that link input and output coordinate spaces.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

## 2. Terminology

**Dimension**: A single axis within a coordinate space, characterized by an
identifier, unit of measurement, and type classification.

**Coordinate System**: A collection of dimensions that together define a
coordinate space for positioning data elements.

**Coordinate Transform**: A mathematical mapping between input and output
coordinate spaces, incorporating a transform definition.

**Dimension Type**: Classification of dimensions as spatial ("space"), temporal
("time"), array indices ("index"), or other ("other").

## 3. Schema Components

### 3.1 Dimension

A Dimension object MUST contain the following properties:

- `id`: A string that uniquely identifies the dimension across all dimensions
  in a dataset
- `unit`: A string specifying the unit of measurement
- `type`: A string specifying the dimension type

#### 3.1.1 Dimension ID

The `id` property MUST be a non-empty string.

The `id` MUST be unique across all dimensions within a dataset.

#### 3.1.2 Dimension Unit

The `unit` property MUST be a non-empty string.

For dimensions with `type` "space" or "time", the unit SHOULD use UDUNITS-2
terms (e.g., "micrometers", "seconds", "radians").

For all dimension types, "index" and "arbitrary" are valid unit values. 
Dimensions with unit "index" MAY have any type ("space", "time", "other", or "index").

#### 3.1.3 Dimension Type

The `type` property MUST be one of the following enumerated values:
- "space": Spatial dimensions
- "time": Temporal dimensions  
- "other": Channels, indices, or other non-spatial/temporal dimensions
- "index": Array index dimensions

If the `type` is "index", then the `unit` MUST be "index".

Additional properties MUST NOT be present in a Dimension object.

### 3.2 Coordinate System

A Coordinate System object MUST contain the following properties:

- `id`: A string that uniquely identifies the coordinate system
- `dimensions`: An array of dimension specifications

A Coordinate System object MAY contain the following optional property:

- `description`: A string describing the coordinate system

#### 3.2.1 Coordinate System ID

The `id` property MUST be a non-empty string.

The `id` MUST be unique across all coordinate systems within a dataset.

#### 3.2.2 Dimensions Array

The `dimensions` property MUST be an array containing at least one element.

Each element in the `dimensions` array MUST be either:
- A string referencing a dimension by its ID, OR
- A complete Dimension object as defined in Section 3.1

#### 3.2.3 Description

The optional `description` property, if present, MUST be a string.

Additional properties MUST NOT be present in a Coordinate System object.

### 3.3 Coordinate Transform

A Coordinate Transform object MUST contain the following properties:

- `id`: A string that uniquely identifies the coordinate transform
- `input`: The input coordinate space specification
- `output`: The output coordinate space specification
- `transform`: A transform definition

A Coordinate Transform object MAY contain the following optional property:

- `description`: A string describing the coordinate transform

#### 3.3.1 Coordinate Transform ID

The `id` property MUST be a non-empty string.

The `id` MUST be unique across all coordinate transforms within a dataset.

#### 3.3.2 Input and Output Specifications

The `input` and `output` properties MUST each be one of the following:
- An array of dimension specifications (strings or Dimension objects)
- A complete Coordinate System object as defined in Section 3.2
- A string referencing a coordinate system by its ID

The dimensionality of the input and output specifications MUST match the
dimensionality requirements of the associated transform.

#### 3.3.3 Transform Definition

The `transform` property MUST reference a valid transform definition from the
transforms vocabulary, as specified in the transforms JSON Schema at
`../transforms/transforms.v0.schema.json#/definitions/Transform`.

#### 3.3.4 Description

The optional `description` property, if present, MUST be a string.

Additional properties MUST NOT be present in a Coordinate Transform object.

## 4. Schema Requirements

### 4.1 General Requirements

All string properties MUST be non-empty strings.

All ID properties MUST be unique within their respective scope (dimension IDs
across all dimensions, coordinate system IDs across all coordinate systems,
coordinate transform IDs across all coordinate transforms).

Objects MUST NOT contain additional properties beyond those specified in this
document.

### 4.2 Validation

Implementations SHOULD validate coordinate space objects against the JSON
Schema defined in `spaces.v0.schema.json`.

Implementations MUST reject objects that do not conform to this specification.

Implementations SHOULD validate that referenced dimension and coordinate system
IDs exist within the dataset scope.

## 5. Examples

### 5.1 Valid Dimension Examples

```json
{
  "id": "x",
  "unit": "micrometers", 
  "type": "space"
}
```

```json
{
  "id": "time",
  "unit": "seconds",
  "type": "time"
}
```

```json
{
  "id": "channel",
  "unit": "arbitrary",
  "type": "other"
}
```

```json
{
  "id": "array_index_0",
  "unit": "index",
  "type": "index"
}
```

### 5.2 Valid Coordinate System Examples

```json
{
  "id": "physical_space",
  "dimensions": ["x", "y", "z"],
  "description": "3D physical coordinate system in micrometers"
}
```

```json
{
  "id": "image_coordinates",
  "dimensions": [
    {"id": "row", "unit": "index", "type": "index"},
    {"id": "col", "unit": "index", "type": "index"}
  ]
}
```

### 5.3 Valid Coordinate Transform Example

```json
{
  "id": "physical_to_pixel",
  "input": "physical_space",
  "output": "image_coordinates", 
  "transform": {
    "scale": [0.1, 0.1, 0.2]
  },
  "description": "Convert from physical units to pixel coordinates"
}
```

### 5.4 Invalid Examples

```json
{
  "id": "invalid_index",
  "unit": "micrometers",
  "type": "index"
}
```
*Invalid: index type dimensions must have unit "index"*

```json
{
  "id": "missing_required",
  "type": "space"
}
```
*Invalid: missing required "unit" property*

```json
{
  "id": "coord_system",
  "dimensions": []
}
```
*Invalid: dimensions array must contain at least one element*

## 6. Security Considerations

ID uniqueness validation SHOULD be performed to prevent namespace collisions
that could lead to incorrect coordinate mappings.

Implementations SHOULD validate dimension and coordinate system references to
prevent dangling references that could cause runtime errors.

Transform definitions reference external schemas and SHOULD be validated
according to the security considerations outlined in the transforms
specification.

Implementations SHOULD impose reasonable limits on the number of dimensions
and coordinate systems to prevent resource exhaustion.
