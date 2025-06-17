# Dataset Data Model

## Overview

The Dataset is the top-level object in the data model. It serves as a container that organizes heterogeneous data sources into a  queryable collection with coordinate transforms and equivalence relations.

## Schema Components Overview

| Component | Description | Key Properties |
|---|---|---|
| Dataset | A complete collection of related spatial and tabular data sources | `id`, `name`, `description`, `sources` |
| Relation | Equivalence mapping between columns and dimensions across data sources | `equivalent` |

## Example Value Formats

| Component | Example Value |
|---|---|
| Dataset | `{"id": "cell_analysis", "name": "Cell Analysis Dataset", "description": "Microscopy with measurements", "sources": [...]}` |
| Relation | `{"equivalent": ["segmentation/values", "measurements/cell_id"], "description": "Cell identifiers"}` |

## Component Specifications

### Dataset

**Example:** `{"id": "multi_modal_dataset", "name": "Multi-Modal Cell Analysis", "description": "Comprehensive cell analysis with images and measurements", "sources": [...], "transforms": [...], "relations": [...]}`

Defines a complete collection of related data sources with optional coordinate transforms and equivalence relations.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `id` | String | Yes | Non-empty, unique | Unique identifier for the dataset |
| `name` | String | Yes | Non-empty | Human-readable display name |
| `description` | String | Yes | Non-empty | Detailed dataset description |
| `sources` | Array | Yes | ≥1 data source object | Collection of data sources |
| `transforms` | Array | No | Coordinate transform objects | Optional coordinate transforms |
| `relations` | Array | No | Relation objects | Optional equivalence relations |

### Relation

**Example:** `{"id": "cell_identifiers", "equivalent": ["segmentation/values", "cell_measurements/cell_id"], "description": "Links segmentation labels to measurement rows"}`

Defines equivalence relationships between columns and dimensions across data sources.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `equivalent` | Array | Yes | ≥2 unique string identifiers | List of equivalent entity references |
| `id` | String | No | Non-empty if present | Optional relation identifier |
| `description` | String | No | Non-empty if present | Optional relation description |

## Entity Reference Types

Relations reference specific entity types within the dataset using hierarchical naming patterns:

### Data Source Coordinate Spaces
**Pattern:** `<datasource_id>`  
**Example:** `fluorescence_image`  
**Description:** References the implicit coordinate space defined by a spatial data source

### Table Columns
**Pattern:** `<datasource_id>/<column_name>`  
**Example:** `measurements/cell_id`  
**Description:** References a specific column within a table data source

### Array Coordinate Dimensions
**Pattern:** `<datasource_id>/dims/<dimension_id>`  
**Example:** `image_stack/dims/z`  
**Description:** References a coordinate dimension within an array data source

### Array Value Dimensions
**Pattern:** `<datasource_id>/values`  
**Example:** `segmentation/values`  
**Description:** References the value dimension of an array data source

## Dataset Structure

### Required Components

#### Data Sources
Every dataset MUST contain at least one data source. Data sources provide the fundamental data content and define the coordinate spaces available for transforms and relations.

**Supported Types:**
- Arrays (multidimensional gridded data)
- Tables (structured tabular data)
- Points (point cloud data)
- Meshes (3D surface data)

### Optional Components

#### Coordinate Transforms
Mathematical mappings between coordinate spaces that enable spatial alignment of data sources. Transforms create a network of coordinate space relationships within the dataset.

**Common Use Cases:**
- Pixel-to-physical coordinate conversion
- Multi-resolution alignment
- Cross-modality registration

#### Equivalence Relations
Explicit mappings that identify semantically equivalent entities across data sources, enabling relational queries and foreign key relationships.

**Common Use Cases:**
- Linking array values to table rows
- Connecting measurements across modalities
- Establishing dimension correspondences

## Validation Rules

### General Constraints

| Rule | Description |
|---|---|
| Unique IDs | Dataset, data source, transform, and relation IDs must be unique within their scope |
| Non-empty Required Fields | All required string properties must be non-empty |
| Reference Consistency | Entity references in relations must correspond to actual dataset components |
| Pattern Matching | Entity identifiers must match pattern `^[^/]+(/[^/]+)*$` |

### Cross-Reference Validation

| Validation | Rule | Example |
|---|---|---|
| Data Source References | `<datasource_id>` must exist in sources array | `fluorescence` → sources contains `{"id": "fluorescence", ...}` |
| Transform References | Transform input/output should reference dataset coordinate spaces | Transform input `"microscopy"` → data source exists |
| Relation Entity Types | Equivalent identifiers must follow valid entity patterns | `"measurements/area"` follows table column pattern |

### Semantic Constraints

| Component | Constraint | Description |
|---|---|---|
| Relations | Minimum 2 equivalent items | Must establish equivalence between at least two entities |
| Relations | Unique equivalent items | No duplicate identifiers within single relation |
| Transforms | Coordinate space compatibility | Input/output spaces should be dimensionally compatible |

## Integration Patterns

### Spatial Data Alignment

Coordinate transforms enable spatial alignment between data sources:

```json
"transforms": [{
  "id": "image_to_physical",
  "input": "microscopy_image",
  "output": "physical_space",
  "transform": {"scale": [0.1, 0.1, 0.2]}
}]
```

### Cross-Modal Foreign Keys

Relations establish foreign key relationships between different data modalities:

```json
"relations": [{
  "equivalent": ["segmentation/values", "measurements/cell_id"],
  "description": "Cell identifier linking labels to measurements"
}]
```

### Multi-Source Integration

Complete datasets integrate multiple data sources through transforms and relations:

- **Arrays** provide spatial context and coordinate systems
- **Tables** provide quantitative measurements and metadata
- **Points** provide sparse spatial annotations
- **Meshes** provide detailed surface representations
- **Transforms** align coordinate systems across sources
- **Relations** establish semantic equivalences

## Complete Examples

### Minimal Dataset
```json
{
  "id": "simple_dataset",
  "name": "Simple Microscopy Dataset",
  "description": "Basic fluorescence microscopy data",
  "sources": [{
    "id": "image",
    "name": "Fluorescence Image",
    "description": "2D fluorescence microscopy image",
    "contentUrl": "https://example.com/image.zarr",
    "type": "array",
    "encodingFormat": "application/zarr+ome"
  }]
}
```

### Multi-Modal Dataset with Relations
```json
{
  "id": "cell_analysis_dataset",
  "name": "Cell Analysis Dataset",
  "description": "Microscopy images with cell segmentation and measurements",
  "sources": [
    {
      "id": "fluorescence",
      "name": "Fluorescence Stack",
      "description": "3D fluorescence microscopy data",
      "contentUrl": "https://example.com/image.zarr",
      "type": "array",
      "encodingFormat": "application/zarr+ome"
    },
    {
      "id": "segmentation",
      "name": "Cell Labels",
      "description": "Segmented cell labels",
      "contentUrl": "https://example.com/image.zarr#labels",
      "type": "array", 
      "encodingFormat": "application/zarr+ome"
    },
    {
      "id": "measurements",
      "name": "Cell Measurements",
      "description": "Quantitative cell analysis",
      "contentUrl": "https://example.com/measurements.parquet",
      "type": "table",
      "encodingFormat": "application/parquet"
    }
  ],
  "transforms": [{
    "id": "fluorescence_to_segmentation",
    "input": "fluorescence",
    "output": "segmentation", 
    "transform": {"identity": []},
    "description": "Shared coordinate space"
  }],
  "relations": [{
    "id": "cell_identifiers",
    "equivalent": ["segmentation/values", "measurements/cell_id"],
    "description": "Cell identifier linking segmentation to measurements"
  }]
}
```

### Complex Multi-Modal Dataset
```json
{
  "id": "comprehensive_analysis",
  "name": "Comprehensive Cell Analysis",
  "description": "Multi-modal dataset with arrays, tables, points, and meshes",
  "sources": [
    {
      "id": "microscopy",
      "name": "3D Microscopy",
      "type": "array",
      "encodingFormat": "application/zarr+ome",
      "contentUrl": "microscopy.zarr"
    },
    {
      "id": "measurements", 
      "name": "Cell Measurements",
      "type": "table",
      "encodingFormat": "application/parquet",
      "contentUrl": "measurements.parquet"
    },
    {
      "id": "centroids",
      "name": "Cell Centers",
      "type": "points", 
      "encodingFormat": "application/parquet",
      "contentUrl": "centroids.parquet"
    },
    {
      "id": "surfaces",
      "name": "Cell Surfaces", 
      "type": "mesh",
      "encodingFormat": "application/neuroglancer-precomputed",
      "contentUrl": "meshes/cells"
    }
  ],
  "transforms": [{
    "id": "image_to_physical",
    "input": "microscopy",
    "output": "physical_space",
    "transform": {"scale": [0.1, 0.1, 0.2]}
  }],
  "relations": [
    {
      "equivalent": ["measurements/cell_id", "centroids/cell_id", "surfaces/cell_id"],
      "description": "Cell identifiers across all modalities"
    },
    {
      "equivalent": ["microscopy/dims/x", "centroids/x", "surfaces/x_coord"],
      "description": "X coordinate correspondence"
    }
  ]
}
```