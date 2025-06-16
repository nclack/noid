# Transform Parameters Specification

## Abstract

This document specifies the JSON Schema for coordinate transform parameters in the NOID (Nathan's Opinionated Imaging Data) library. The specification defines a self-describing format for representing various types of coordinate transformations used in multidimensional array processing.

## Status

This document describes the v0 schema for transform parameters.

## Table of Contents

1. [Introduction](#introduction)
2. [Terminology](#terminology)
3. [Transform Types](#transform-types)
4. [Schema Requirements](#schema-requirements)
5. [Examples](#examples)
6. [Security Considerations](#security-considerations)

## 1. Introduction

Transform parameters in NOID use a self-describing JSON format where the transform type is identified by the property name. This specification defines eight distinct transform types and their parameter requirements.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 2. Terminology

**Transform**: A mathematical operation that maps coordinates from one coordinate space to another.

**Self-describing format**: A JSON representation where the transform type is inferred from the property name rather than an explicit type field.

**Parameter object**: A JSON object containing exactly one transform property and its associated parameters.

## 3. Transform Types

### 3.1 Identity Transform

An identity transform object MUST contain an `identity` property.

The `identity` property MUST be an empty array (`[]`).

Additional properties MUST NOT be present in an identity transform object.

### 3.2 Translation Transform

A translation transform object MUST contain a `translation` property.

The `translation` property MUST be an array of numbers representing the translation vector.

The array MUST contain at least one element.

Additional properties MUST NOT be present in a translation transform object.

### 3.3 Scale Transform

A scale transform object MUST contain a `scale` property.

The `scale` property MUST be an array of positive numbers representing scale factors.

Each scale factor MUST be greater than zero.

The array MUST contain at least one element.

Additional properties MUST NOT be present in a scale transform object.

### 3.4 Axis Mapping Transform

An axis mapping transform object MUST contain a `mapAxis` property.

The `mapAxis` property MUST be an object with string key-value pairs mapping input axis names to output axis names.

Both keys and values MUST match the pattern `^[a-zA-Z_][a-zA-Z0-9_]*$` (valid identifier format).

The object MUST contain at least one property.

Additional properties MUST NOT be present in an axis mapping transform object.

### 3.5 Homogeneous Transform

A homogeneous transform object MUST contain a `homogeneous` property.

The `homogeneous` property MUST be a 2D array of numbers representing a homogeneous transformation matrix. This transform type is useful for representing both affine and projective transformations.

The outer array MUST contain at least two sub-arrays.

Additional properties MUST NOT be present in a homogeneous transform object.

### 3.6 Displacements Transform

A displacements transform object MUST contain a `displacements` property.

The `displacements` property MUST be either:
- A string representing the path to a displacement field, OR
- An object with the following structure:
  - A REQUIRED `path` property containing a string
  - An OPTIONAL `interpolation` property with value "linear", "nearest", or "cubic"
  - An OPTIONAL `extrapolation` property with value "nearest", "zero", or "constant"

Additional properties MUST NOT be present in a displacements transform object or its configuration object.

### 3.7 Coordinates Transform

A coordinates transform object MUST contain a `coordinates` property.

The `coordinates` property MUST be an object with the following structure:
- A REQUIRED `lookup_table` property containing a string path
- An OPTIONAL `interpolation` property with value "linear", "nearest", or "cubic"  
- An OPTIONAL `extrapolation` property with value "nearest", "zero", or "constant"

Additional properties MUST NOT be present in a coordinates transform object or its configuration object.

## 4. Schema Requirements

### 4.1 General Requirements

Each transform parameter object MUST contain exactly one of the eight defined transform properties.

Transform parameter objects MUST NOT contain additional properties beyond the specified transform property.

All numeric values MUST be finite numbers (not NaN or infinity).

### 4.2 Validation

Implementations SHOULD validate transform parameters against the JSON Schema defined in `transforms.v0.schema.json`.

Implementations MUST reject transform objects that do not conform to this specification.

## 5. Examples

### 5.1 Valid Transform Examples

```json
{"identity": []}
```

```json
{"translation": [10, 20, 5]}
```

```json
{"scale": [2.0, 1.5, 0.5]}
```

```json
{"mapAxis": {"x": "y", "y": "x", "z": "z"}}
```

```json
{"homogeneous": [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]}
```

```json
{"sequence": [{"scale": [2.0, 2.0]}, {"translation": [10, 20]}]}
```

```json
{"displacements": "path/to/displacement_field.zarr"}
```

```json
{"coordinates": {"lookup_table": "path/to/coordinate_lut.zarr", "interpolation": "linear"}}
```

### 5.2 Invalid Transform Examples

```json
{"identity": [1, 2, 3]}
```
*Invalid: identity array must be empty*

```json
{"scale": [2.0, -1.5, 0.5]}
```
*Invalid: scale factors must be positive*

```json
{"translation": [10, 20], "scale": [2.0]}
```
*Invalid: multiple transform properties*

## 6. Security Considerations

Path references in `displacements` and `coordinates` transforms MAY reference external files. Implementations SHOULD validate file paths and implement appropriate access controls to prevent unauthorized file system access.

Implementations SHOULD impose reasonable limits on array sizes to prevent resource exhaustion attacks.

Matrix operations SHOULD be validated for numerical stability, particularly for homogeneous transforms.
