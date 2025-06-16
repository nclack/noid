# ID Naming Convention

## Overview

This document specifies the naming convention for identifiers used within NOID datasets. The convention establishes a hierarchical namespace that enables consistent referencing of data sources, their components, and relationships between them.

This naming convention aims to provide:

1. **Consistency**: Standardized patterns across all dataset types
2. **Clarity**: Clear distinction between data sources, dimensions, and values
3. **Scalability**: Hierarchical structure supports complex datasets
4. **Interoperability**: Predictable naming enables automated processing
5. **Relationship Modeling**: Clear syntax for foreign key references

## Dataset Structure

A dataset is composed of a collection of **data sources**. Each data source is either:
- **Spatial data**: multidimensional arrays, point sets, meshes, polygons
- **Tables**: tabular data with rows and columns

## Data Source Identifiers

Each data source has a unique identifier within the dataset scope:

```
<datasource_id>
```

**Requirements:**
- Must be unique across all data sources within a dataset
- Must be a non-empty string
- Should follow valid identifier patterns for interoperability

## Table References

Table columns are referenced using the pattern:

```
<datasource_id>/<column_name>
```

This pattern is used for defining foreign key relationships between data sources.

**Example:**
```
metadata_table/sample_id
annotations_table/image_id
```

## Spatial Data Coordinate Spaces

Each spatial data source has an implicit coordinate space that can be referenced as:

```
<datasource_id>
```

The coordinate space identifier is the same as the data source identifier, representing the default coordinate system associated with that spatial data.

## Array Dimension References

For multidimensional arrays, dimensions are referenced using structured paths:

### Coordinate Dimensions
```
<datasource_id>/dims/<dimension_id>
```

### Value Dimension
```
<datasource_id>/values
```

**Examples:**
```
microscopy_image/dims/x
microscopy_image/dims/y
microscopy_image/dims/z
microscopy_image/dims/time
microscopy_image/values
```

## File-Type Conventions

Each spatial data type will have established conventions for default dimension names based on the file format. These conventions ensure consistent dimension naming across datasets using the same data formats.

**Note:** Specific file-type conventions will be documented separately as they are established.

## Hierarchical Namespace

The naming convention creates a hierarchical namespace structure:

```
<datasource_id>                    # Data source / coordinate space
├── <column_name>                  # Table columns (for tabular data)
├── dims/
│   ├── <dimension_id>             # Coordinate dimensions (for arrays)
│   └── ...
└── values                         # Value dimension (for arrays)
```

## Examples

### Dataset with Mixed Data Types

```
# Data sources
image_stack                        # 3D microscopy array
point_annotations                  # Point set data
metadata_table                     # Tabular metadata

# Table column references
metadata_table/sample_id
metadata_table/acquisition_date

# Array dimension references
image_stack/dims/x
image_stack/dims/y  
image_stack/dims/z
image_stack/dims/channel
image_stack/values

# Coordinate space references
image_stack                        # Implicit coordinate space for the array
point_annotations                  # Implicit coordinate space for points
```

### Foreign Key Relationships

```
# Foreign key linking points to image metadata
point_annotations/sample_id → metadata_table/sample_id
```
