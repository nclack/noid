# Dataset Specification

## 1. Introduction

This document specifies the dataset schema for NOID (Nathan's Opinionated Imaging Data library). A dataset represents a complete collection of related spatial and tabular data sources with their coordinate transforms and relational mappings.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 2. Dataset Structure

A NOID dataset is a container that organizes heterogeneous data sources into a coherent, queryable collection. It consists of:

- **Data Sources** (required): Typed, addressable data resources that form the dataset content
- **Coordinate Transforms** (optional): Mathematical mappings between coordinate spaces for spatial alignment  
- **Equivalence Relations** (optional): Mappings identifying columns and dimensions representing the same logical entity

## 3. Required Properties

### 3.1 Identifier (`id`)
The `id` property MUST be a non-empty string that uniquely identifies the dataset and SHOULD be descriptive of the dataset content.

### 3.2 Name (`name`) 
The `name` property MUST be a non-empty string providing a human-readable name suitable for display in user interfaces.

### 3.3 Description (`description`)
The `description` property MUST be a non-empty string providing detailed information about the dataset, including data collection methodology, processing history, and intended use cases.

### 3.4 Data Sources (`sources`)
The `sources` property MUST be an array containing at least one data source object. Each data source object MUST conform to the Data Sources specification.

## 4. Optional Properties

### 4.1 Coordinate Transforms (`transforms`)
The `transforms` property MAY be included as an array of coordinate transform objects. When present, each transform MUST conform to the Coordinate Transforms specification and SHOULD reference coordinate spaces defined by data sources.

### 4.2 Equivalence Relations (`relations`)
The `relations` property MAY be included as an array of relation objects that define equivalence mappings between data source components.

## 5. Relation Objects

Relation objects define equivalence relationships between columns and dimensions across data sources.

### 5.1 Required: Equivalent Items (`equivalent`)
The `equivalent` property MUST be an array containing at least two unique string identifiers that reference specific entity types within the dataset.

Each identifier MUST correspond to one of the following entity types:
- **Data source coordinate spaces**: `<datasource_id>` (e.g., `fluorescence_image`)
- **Table columns**: `<datasource_id>/<column_name>` (e.g., `measurements/cell_id`)
- **Array coordinate dimensions**: `<datasource_id>/dims/<dimension_id>` (e.g., `image_stack/dims/z`)
- **Array value dimensions**: `<datasource_id>/values` (e.g., `segmentation/values`)

The `<datasource_id>` component MUST correspond to the `id` property of a data source in the dataset's `sources` array. Identifiers SHOULD follow this hierarchical naming convention and MUST match the pattern `^[^/]+(/[^/]+)*$`.

### 5.2 Optional: Relation Identifier (`id`) and Description (`description`)
The `id` and `description` properties MAY be included as non-empty strings to identify and explain the relation.

## 6. Validation Requirements

Implementations MUST validate dataset objects against the JSON Schema specification, including required field presence, data source conformance, and reference pattern validation.

Implementations SHOULD validate cross-references exist within the dataset and MAY perform semantic validation of coordinate space compatibility and relation consistency.

## 7. Examples

### 7.1 Minimal Dataset
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

### 7.2 Complete Dataset with Relations
```json
{
  "id": "cell_analysis_dataset",
  "name": "Cell Analysis Dataset",
  "description": "Microscopy images with cell segmentation and quantitative measurements",
  "sources": [
    {
      "id": "fluorescence",
      "name": "Fluorescence Microscopy Image Stack",
      "description": "3D fluorescence microscopy data with DAPI and GFP channels",
      "contentUrl": "https://example.com/data/image.zarr",
      "type": "array",
      "encodingFormat": "application/zarr+ome"
    },
    {
      "id": "segmentation",
      "name": "Segmented Cell Labels",
      "description": "Segmented 3D microscopy data with cell identity labels",
      "contentUrl": "https://example.com/data/image.zarr#labels",
      "type": "array",
      "encodingFormat": "application/zarr+ome"
    },
    {
      "id": "cell_measurements",
      "name": "Cell Quantitative Measurements",
      "description": "Area, intensity, and morphology measurements per cell",
      "contentUrl": "https://example.com/data/measurements.parquet",
      "type": "table",
      "encodingFormat": "application/parquet"
    }
  ],
  "transforms": [
    {
      "id": "fluorescence_to_segmentation",
      "input": "fluorescence",
      "output": "segmentation",
      "transform": {"identity": []},
      "description": "Fluorescence and segmentation share the same coordinate space"
    }
  ],
  "relations": [
    {
      "id": "cell_identifiers",
      "equivalent": ["segmentation/values", "cell_measurements/cell_id"],
      "description": "Cell identifier linking segmentation labels to measurement rows"
    }
  ]
}
```

### 7.3 Multi-Modal Dataset
```json
{
  "id": "multi_modal_dataset",
  "name": "Multi-Modal Cell Analysis",
  "description": "Comprehensive cell analysis with images, measurements, centroids, and surface meshes",
  "sources": [
    {
      "id": "microscopy",
      "name": "Fluorescence Microscopy",
      "description": "3D fluorescence imaging data",
      "contentUrl": "https://example.com/microscopy.zarr",
      "type": "array",
      "encodingFormat": "application/zarr+ome"
    },
    {
      "id": "measurements",
      "name": "Quantitative Analysis",
      "description": "Cell measurements and statistics",
      "contentUrl": "https://example.com/measurements.parquet",
      "type": "table",
      "encodingFormat": "application/parquet"
    },
    {
      "id": "centroids",
      "name": "Cell Center Points",
      "description": "XYZ coordinates of cell centers",
      "contentUrl": "https://example.com/centroids.parquet",
      "type": "points",
      "encodingFormat": "application/parquet"
    },
    {
      "id": "surfaces",
      "name": "Cell Surface Meshes",
      "description": "3D surface meshes of cell boundaries",
      "contentUrl": "https://example.com/meshes/cells",
      "type": "mesh",
      "encodingFormat": "application/neuroglancer-precomputed"
    }
  ],
  "transforms": [
    {
      "id": "image_to_physical",
      "input": "microscopy",
      "output": "physical_space",
      "transform": {"scale": [0.1, 0.1, 0.2]},
      "description": "Convert image coordinates to physical micrometers"
    }
  ],
  "relations": [
    {
      "id": "cell_identifiers",
      "equivalent": [
        "measurements/cell_id",
        "centroids/cell_id",
        "surfaces/cell_id"
      ],
      "description": "Cell identifiers linking all data modalities"
    }
  ]
}
```

## 8. Security Considerations

Implementations SHOULD validate that:
- Data source content URLs use approved schemes
- Cross-references do not create circular dependencies
- Relation patterns cannot be exploited for path traversal attacks

When processing datasets from untrusted sources, implementations MUST validate
all references and URIs before attempting to access referenced content.

## 9. References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- Data Sources Specification
- Coordinate Transforms Specification
- JSON Schema Specification
