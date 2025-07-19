# Data Sources Specification

## 1. Introduction

This document specifies the data sources schema for NOID (Nathan's Opinionated
Imaging Data library) datasets. Data sources represent the fundamental data
units within NOID datasets - the spatial and tabular data that comprise a
scientific dataset.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

## 2. Overview

A data source is a typed, addressable resource with specific encoding format
constraints. This specification defines four data source types with their
corresponding format requirements and addressing mechanisms.

## 3. Data Source Types

### 3.1 Array Data Sources

Array data sources MUST have type `"array"` and encoding format
`"application/zarr+ome"`.

Array data sources represent multidimensional arrays for images, volumes, and other gridded data. RECOMMENDED uses include:
- Microscopy images
- Medical volumes
- Satellite imagery
- Time series grids

Array data sources MUST support multidimensional coordinate systems and SHOULD
follow OME-Zarr metadata conventions.

### 3.2 Table Data Sources

Table data sources MUST have type `"table"` and encoding format
`"application/parquet"`.

Table data sources represent structured tabular data with rows and columns. RECOMMENDED uses include:
- Metadata tables
- Measurement data
- Annotation data
- Categorical data

Table data sources SHOULD support foreign key relationships with other data
sources through the relational model.

### 3.3 Point Data Sources

Point data sources MUST have type `"points"` and encoding format
`"application/parquet"`.

Point data sources represent point cloud data with coordinates and optional features. RECOMMENDED uses include:
- Cell centroids
- Landmark points
- Sparse annotations
- GPS coordinates

Point data sources MUST include coordinate columns and MAY include additional
feature columns.

### 3.4 Mesh Data Sources

Mesh data sources MUST have type `"mesh"` and encoding format
`"application/neuroglancer-precomputed"`.

Mesh data sources represent 3D surface meshes with vertices and faces. RECOMMENDED uses include:
- Cell surfaces
- Organ boundaries
- 3D reconstructions
- Surface-based visualizations

## 4. Required Properties

All data source objects MUST include the following properties:

### 4.1 Identifier (`id`)

The `id` property MUST be a non-empty string that uniquely identifies the data
source within the dataset's data source collection.

The identifier SHOULD follow a hierarchical naming pattern that enables referencing of sub-components. For example, table columns are referenced as `<datasource_id>/<column_name>` and array dimensions as `<datasource_id>/dims/<dimension_id>`.

### 4.2 Name (`name`)

The `name` property MUST be a string providing a human-readable display name for
the data source.

The name SHOULD be descriptive and suitable for user interfaces.

### 4.3 Description (`description`)

The `description` property MUST be a string providing detailed information about
the data source content.

The description SHOULD include relevant context such as acquisition method,
processing history, or other explanatory information.

### 4.4 Content URL (`contentUrl`)

The `contentUrl` property MUST be a valid URI pointing to the data source
location.

The content URL MAY include fragment identifiers for addressing sub-components within container formats:
- `https://example.com/data.zarr#labels/cells` - Sub-array within container
- `https://example.com/data.zarr#multiscale/0` - Specific resolution level

### 4.5 Type (`type`)

The `type` property MUST be one of the following enumerated values:
- `"array"`
- `"table"`
- `"points"`
- `"mesh"`

### 4.6 Encoding Format (`encodingFormat`)

The `encodingFormat` property MUST be a string specifying the data format.

The encoding format MUST match the type-specific constraints defined in Section
3.

## 5. Optional Properties

### 5.1 SHA256 Hash (`sha256`)

The `sha256` property MAY be included to provide data integrity verification.

When present, the `sha256` property MUST be a 64-character hexadecimal string
representing the SHA256 hash of the referenced data.

## 6. Format Constraints

Data source objects MUST enforce the following type-format mappings:

| Type | Required Encoding Format |
|------|--------------------------|
| `array` | `application/zarr+ome` |
| `table` | `application/parquet` |
| `points` | `application/parquet` |
| `mesh` | `application/neuroglancer-precomputed` |

Implementations MUST validate that the `encodingFormat` property matches the
required format for the specified `type`.

## 7. URI Addressing

### 7.1 Fragment Identifiers

Data sources MAY use URI fragment identifiers to address components within
container formats.

Fragment identifiers MUST follow the pattern:
```
<base_uri>#<fragment_path>
```

Where `<fragment_path>` is a format-specific path to a sub-component.

### 7.2 Container Format Support

Implementations SHOULD support fragment addressing for container formats including:
- OME-Zarr arrays and labels
- HDF5 datasets and groups
- Multi-resolution hierarchies

## 8. ID-Based Referencing

Data sources support hierarchical referencing of their components through structured ID patterns:

### 8.1 Coordinate Space References

Each spatial data source defines an implicit coordinate space that MUST be referenced using the data source identifier:
```
<datasource_id>
```

### 8.2 Dimension References

Array dimensions MUST be referenced using the structured path format:
```
<datasource_id>/dims/<dimension_id>  # Coordinate dimensions
<datasource_id>/values               # Value dimension
```

### 8.3 Column References

Table columns MUST be referenced using the format:
```
<datasource_id>/<column_name>
```

## 9. Validation Requirements

### 9.1 Schema Validation

Implementations MUST validate data source objects against the JSON Schema
specification.

Schema validation MUST include:
- Required field presence
- Type-format constraint enforcement
- URI format validation
- SHA256 pattern validation (when present)

### 9.2 Integrity Verification

When the `sha256` property is present, implementations SHOULD verify data
integrity by computing the hash of the referenced content and comparing with the
declared value.

### 9.3 Container Addressing Validation

Implementations SHOULD validate that fragment identifiers resolve to valid paths
within their container formats.

## 10. Examples

### 10.1 Array Data Source
```json
{
  "id": "fluorescence_stack",
  "name": "3D Fluorescence Microscopy",
  "description": "DAPI and GFP channels acquired at 63x magnification",
  "contentUrl": "https://example.com/experiment1.zarr#images/stack",
  "type": "array",
  "encodingFormat": "application/zarr+ome",
  "sha256": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890"
}
```

### 10.2 Table Data Source
```json
{
  "id": "cell_measurements",
  "name": "Quantitative Cell Analysis",
  "description": "Area, intensity, and morphology measurements per cell",
  "contentUrl": "https://example.com/measurements.parquet",
  "type": "table",
  "encodingFormat": "application/parquet"
}
```

### 10.3 Point Data Source
```json
{
  "id": "nuclei_centroids",
  "name": "Nuclear Center Points",
  "description": "XYZ coordinates of detected cell nuclei",
  "contentUrl": "https://example.com/centroids.parquet",
  "type": "points",
  "encodingFormat": "application/parquet"
}
```

### 10.4 Mesh Data Source
```json
{
  "id": "cell_boundaries",
  "name": "3D Cell Surface Mesh",
  "description": "Triangulated surfaces of individual cell boundaries",
  "contentUrl": "https://example.com/meshes/cells",
  "type": "mesh",
  "encodingFormat": "application/neuroglancer-precomputed"
}
```

## 11. Security Considerations

Implementations SHOULD validate URI schemes and MAY restrict access to certain
URI schemes for security purposes.

When processing fragment identifiers, implementations MUST prevent path
traversal attacks and SHOULD validate that fragment paths are within expected
bounds.

## 12. References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- OME-Zarr specification
- Apache Parquet specification
- Neuroglancer Precomputed format specification
