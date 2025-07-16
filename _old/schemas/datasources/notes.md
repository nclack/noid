# Data Sources Schema Notes

## Overview

The data sources schema defines spatial data sources with URI-based addressing capabilities. It enforces type-specific encoding format constraints to ensure consistency across different spatial data types.

## Core Fields

### Required Fields
- **id**: Unique identifier within the data source collection
- **name**: Human-readable display name
- **description**: Textual description of the data source
- **contentUrl**: URI to the data source with optional fragment addressing
- **type**: Spatial data type (array, table, points, mesh)
- **encodingFormat**: Format specification constrained by type

### Optional Fields
- **sha256**: 64-character hexadecimal hash for integrity verification

## Spatial Data Types and Formats

The schema enforces strict type-format mappings:

| Type | Encoding Format | Use Case |
|------|----------------|----------|
| `array` | `application/zarr+ome` | Multidimensional arrays (images, volumes) |
| `table` | `application/parquet` | Tabular data with structured columns |
| `points` | `application/parquet` | Point cloud data (coordinates, features) |
| `mesh` | `application/neuroglancer-precomputed` | 3D surface meshes |

## URI Addressing

The `contentUrl` field supports fragment identifiers for addressing items within container formats:

- **Container root**: `https://example.com/data.zarr`
- **Sub-array**: `https://example.com/data.zarr#labels/cells`
- **Nested path**: `https://example.com/data.zarr#multiscale/0/labels/nuclei`

This approach enables:
- Single container hosting multiple related arrays
- Hierarchical organization within formats like OME-Zarr
- Future relative URI support for co-located metadata

## Design Considerations

### Format Selection Rationale
- **OME-Zarr**: Standard for bioimaging arrays with rich metadata
- **Parquet**: Efficient columnar format for structured data
- **Neuroglancer Precomputed**: Optimized for 3D mesh visualization

### Container Formats
Many formats are inherently containers (Zarr, HDF5). Fragment identifiers provide a standardized way to address sub-components without requiring format-specific parsers in the schema layer.

### Future Extensions
- Relative URI support for embedded metadata
- Additional spatial data types (volumes, annotations)
- Multi-format support per type (e.g., HDF5 arrays)
- Compression and encoding parameters

## Validation

Use standard JSON Schema validators. The schema includes conditional validation ensuring encoding formats match their declared types.

## Examples

See the schema file for complete examples covering all supported data types and addressing patterns.