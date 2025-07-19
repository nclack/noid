# Data Sources Data Model

## Schema Components Overview

| Component | Description | Key Properties |
|---|---|---|
| Data Source | A typed, addressable spatial or tabular data resource | `id`, `name`, `description`, `contentUrl`, `type`, `encodingFormat` |

## Example Value Formats

| Data Source Type | Example Value |
|---|---|
| Array | `{"id": "microscopy_image", "name": "Fluorescence Stack", "type": "array", "encodingFormat": "application/zarr+ome", "contentUrl": "data.zarr#multiscale/0"}` |
| Table | `{"id": "cell_measurements", "name": "Cell Analysis Data", "type": "table", "encodingFormat": "application/parquet", "contentUrl": "measurements.parquet"}` |
| Points | `{"id": "centroids", "name": "Cell Centers", "type": "points", "encodingFormat": "application/parquet", "contentUrl": "centroids.parquet"}` |
| Mesh | `{"id": "surfaces", "name": "Cell Boundaries", "type": "mesh", "encodingFormat": "application/neuroglancer-precomputed", "contentUrl": "meshes/cells"}` |

## Component Specifications

### Data Source

**Example:** `{"id": "fluorescence_stack", "name": "3D Fluorescence Microscopy", "description": "DAPI and GFP channels acquired at 63x magnification", "contentUrl": "https://example.com/data.zarr#images/stack", "type": "array", "encodingFormat": "application/zarr+ome"}`

Defines a typed, addressable resource containing spatial or tabular data with format-specific constraints.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `id` | String | Yes | Non-empty, unique across dataset | Unique identifier for the data source |
| `name` | String | Yes | Non-empty | Human-readable display name |
| `description` | String | Yes | Non-empty | Detailed description of the data source |
| `contentUrl` | String | Yes | Valid URI format | URI pointing to the data location |
| `type` | String | Yes | `"array"`, `"table"`, `"points"`, `"mesh"` | Spatial data type classification |
| `encodingFormat` | String | Yes | Must match type constraints | Format specification for the data |
| `sha256` | String | No | 64-character hexadecimal | Optional SHA256 hash for integrity |

## Data Source Types

### Array Data Sources

**Type:** `"array"`
**Required Encoding Format:** `"application/zarr+ome"`

Array data sources represent multidimensional arrays for images, volumes, and other gridded data.

**Recommended Uses:**
- Microscopy images
- Medical volumes
- Satellite imagery
- Time series grids

**Properties:**
- MUST support multidimensional coordinate systems
- SHOULD follow OME-Zarr metadata conventions
- MAY use fragment identifiers for sub-array addressing

### Table Data Sources

**Type:** `"table"`
**Required Encoding Format:** `"application/parquet"`

Table data sources represent structured tabular data with rows and columns.

**Recommended Uses:**
- Metadata tables
- Measurement data
- Annotation data
- Categorical data

**Properties:**
- SHOULD support foreign key relationships with other data sources
- MUST use columnar Parquet format for efficient querying
- MAY reference columns using `<datasource_id>/<column_name>` pattern

### Point Data Sources

**Type:** `"points"`
**Required Encoding Format:** `"application/parquet"`

Point data sources represent point cloud data with coordinates and optional features.

**Recommended Uses:**
- Cell centroids
- Landmark points
- Sparse annotations
- GPS coordinates

**Properties:**
- MUST include coordinate columns
- MAY include additional feature columns
- SHOULD use structured coordinate representation

### Mesh Data Sources

**Type:** `"mesh"`
**Required Encoding Format:** `"application/neuroglancer-precomputed"`

Mesh data sources represent 3D surface meshes with vertices and faces.

**Recommended Uses:**
- Cell surfaces
- Organ boundaries
- 3D reconstructions
- Surface-based visualizations

**Properties:**
- MUST represent 3D surface data
- SHOULD support hierarchical level-of-detail
- MAY integrate with Neuroglancer visualization tools

## Format Constraints

Data source objects MUST enforce strict type-format mappings:

| Type | Required Encoding Format | Validation Rule |
|---|---|---|
| `"array"` | `"application/zarr+ome"` | Must validate as OME-Zarr format |
| `"table"` | `"application/parquet"` | Must validate as Apache Parquet format |
| `"points"` | `"application/parquet"` | Must validate as Apache Parquet format |
| `"mesh"` | `"application/neuroglancer-precomputed"` | Must validate as Neuroglancer format |

## URI Addressing

### Fragment Identifiers

Data sources MAY use URI fragment identifiers to address sub-components within container formats.

**Pattern:** `<base_uri>#<fragment_path>`

**Examples:**
- `https://example.com/data.zarr#labels/cells` - Sub-array within container
- `https://example.com/data.zarr#multiscale/0` - Specific resolution level
- `https://example.com/data.h5#/measurements/cell_stats` - HDF5 internal dataset

### Container Format Support

| Format | Fragment Support | Example Paths |
|---|---|---|
| OME-Zarr | Arrays, labels, multiscale | `#labels/cells`, `#multiscale/0` |
| HDF5 | Datasets, groups | `#/data/measurements`, `#/metadata` |
| Multi-resolution | Level specification | `#level/0`, `#resolution/high` |

## ID-Based Referencing

Data sources support hierarchical referencing through structured ID patterns:

### Coordinate Space References
Each spatial data source defines an implicit coordinate space:
```
<datasource_id>
```

### Dimension References
Array dimensions use structured paths:
```
<datasource_id>/dims/<dimension_id>  # Coordinate dimensions
<datasource_id>/values               # Value dimension
```

### Column References
Table columns use hierarchical naming:
```
<datasource_id>/<column_name>
```

## Schema Rules

### General Constraints

| Rule | Description |
|---|---|
| Unique IDs | All data source IDs must be unique within the dataset |
| Non-empty Strings | All required string properties must be non-empty |
| Type-Format Matching | Encoding format must match the specified type |
| URI Validation | Content URLs must be valid URI format |
| No Additional Properties | Objects cannot contain properties other than those specified |

### Type Validation Rules

| Validation | Rule | Example |
|---|---|---|
| Array Format Constraint | If `type` is "array", then `encodingFormat` MUST be "application/zarr+ome" | `{"type": "array", "encodingFormat": "application/zarr+ome"}` ✓ |
| Table Format Constraint | If `type` is "table", then `encodingFormat` MUST be "application/parquet" | `{"type": "table", "encodingFormat": "application/parquet"}` ✓ |
| Points Format Constraint | If `type` is "points", then `encodingFormat` MUST be "application/parquet" | `{"type": "points", "encodingFormat": "application/parquet"}` ✓ |
| Mesh Format Constraint | If `type` is "mesh", then `encodingFormat` MUST be "application/neuroglancer-precomputed" | `{"type": "mesh", "encodingFormat": "application/neuroglancer-precomputed"}` ✓ |

### SHA256 Validation

| Property | Pattern | Description |
|---|---|---|
| `sha256` | `^[a-f0-9]{64}$` | Exactly 64 hexadecimal characters |

### Invalid Examples

| Invalid Case | Example | Reason |
|---|---|---|
| Type-format mismatch | `{"type": "array", "encodingFormat": "application/parquet"}` | Array type requires zarr+ome format |
| Empty required field | `{"id": "", "type": "table"}` | ID cannot be empty |
| Invalid URI format | `{"contentUrl": "not-a-uri"}` | Must be valid URI format |
| Invalid SHA256 | `{"sha256": "invalid"}` | Must be 64-character hexadecimal |
| Missing required property | `{"id": "test", "type": "array"}` | Missing required properties |

## Complete Examples

### Array Data Source with Fragment Addressing
```json
{
  "id": "fluorescence_stack",
  "name": "3D Fluorescence Microscopy",
  "description": "DAPI and GFP channels acquired at 63x magnification with 0.1μm pixel size",
  "contentUrl": "https://example.com/experiment1.zarr#images/stack",
  "type": "array",
  "encodingFormat": "application/zarr+ome",
  "sha256": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890"
}
```

### Table Data Source with Measurements
```json
{
  "id": "cell_measurements",
  "name": "Quantitative Cell Analysis",
  "description": "Area, intensity, and morphology measurements per cell with statistical summaries",
  "contentUrl": "https://example.com/measurements.parquet",
  "type": "table",
  "encodingFormat": "application/parquet"
}
```

### Point Data Source for Centroids
```json
{
  "id": "nuclei_centroids",
  "name": "Nuclear Center Points",
  "description": "XYZ coordinates of detected cell nuclei with confidence scores",
  "contentUrl": "https://example.com/centroids.parquet",
  "type": "points",
  "encodingFormat": "application/parquet"
}
```

### Mesh Data Source for Surfaces
```json
{
  "id": "cell_boundaries",
  "name": "3D Cell Surface Mesh",
  "description": "Triangulated surfaces of individual cell boundaries from segmentation",
  "contentUrl": "https://example.com/meshes/cells",
  "type": "mesh",
  "encodingFormat": "application/neuroglancer-precomputed"
}
```

## Integration Patterns

### Foreign Key Relationships
Table data sources can establish foreign key relationships with other data sources:

```json
{
  "relations": [{
    "equivalent": ["fluorescence_stack/values", "cell_measurements/cell_id"],
    "description": "Links image pixel values to measurement rows"
  }]
}
```

### Coordinate Space Integration
Array data sources automatically define coordinate spaces for spatial transforms:

```json
{
  "transforms": [{
    "input": "fluorescence_stack",
    "output": "physical_space",
    "transform": {"scale": [0.1, 0.1, 0.2]}
  }]
}
```

### Multi-Source Datasets
Complete datasets combine multiple data source types:

```json
{
  "sources": [
    {"id": "images", "type": "array", "encodingFormat": "application/zarr+ome"},
    {"id": "annotations", "type": "table", "encodingFormat": "application/parquet"},
    {"id": "landmarks", "type": "points", "encodingFormat": "application/parquet"},
    {"id": "surfaces", "type": "mesh", "encodingFormat": "application/neuroglancer-precomputed"}
  ]
}
```
