# N-Dimensional Array Relational Model - Key Findings Summary

## Problem Statement
Need a relational model for n-dimensional arrays/images that supports:
- **Spatial dimensions**: Coordinate reference systems and transforms between vector spaces
- **Categorical dimensions**: Metadata lookup via relationships  
- **Temporal dimensions**: Event indexing with multiple clocks/timestamps
- **Value transforms**: Scalar pixel value mappings (contrast, lookup tables)
- **Storage**: Zarr-based with JSON-LD metadata

## Key Design Decisions

### 1. Coordinate Spaces as Namespaces
- **Coordinate space** = mathematical container + namespace for dimension tuples
- **Arrays have implicit coordinate spaces** (dimensions with units="index")  
- **Named coordinate spaces** for explicit reference systems
- **Transforms** map between coordinate spaces (may be non-bijective)

### 2. Unified Transform Pattern
- **Same structure** for spatial, temporal, and value transforms
- **Domain/Range** specify source/target coordinate spaces
- **mapsDimension** specifies dimension mappings
- **Context switching** for vocabulary-specific parameters

### 3. External References
- **Categorical lookups**: `@row_index` or named column joins
- **Temporal events**: External tables with multi-clock timestamps  
- **Value transforms**: Can reference other arrays (e.g., histograms)

## Core Relations Developed

### Array ↔ Space Relations
- `hasDimension` - Array has ordered dimensions (implicit coordinate space)
- `hasName`, `hasUnit`, `hasDimensionType` - Dimension properties

### Transform Relations  
- `hasTransform` - Links to transformation definition
- `hasDomain`, `hasRange` - Source/target coordinate spaces
- `mapsDimension` - Dimension index/name mappings

### Categorical Relations
- `hasCategoryScheme` - Links to category definitions
- `referencesTable` - External lookup table
- `hasLookupKey` - Join field (`@row_index` for positional)

### Temporal Relations
- `hasEventScheme` - Links to event definitions  
- `hasClock` - Multi-clock timestamp support
- Linear transforms for evenly-spaced time series

### Value Transform Relations
- `hasValueTransform` - Scalar value mappings
- `hasStatistics` - Data statistics (min/max/histogram arrays)
- Reuses coordinate space pattern for value spaces

## Technical Architecture

### JSON-LD with Context Switching
```json
{
  "@context": [
    {"@vocab": "https://your-domain.org/mdarray#"},
    {"proj": "https://proj.org/vocab#"},
    {"cv": "https://opencv.org/vocab#"}
  ],
  "transforms": {
    "geo_transform": {
      "@context": {"@vocab": "https://proj.org/vocab#"},
      "proj:parameters": {...}
    }
  }
}
```

### Vocabulary Registry System
- **Extensible vocabularies**: PROJ for geospatial, OpenCV for image processing
- **Handler registration**: Domain-specific parameter interpretation
- **Validation**: Ensures all vocabularies have registered handlers
- **Context switching**: Automatic dispatch to appropriate handlers

## Implementation Pattern
```python
# Registry-based validation and execution
metadata = MDArrayMetadata(json_ld)
validator = MDArrayValidator(VOCABULARY_REGISTRY)
assert validator.validate_schema(metadata).valid

# Automatic handler dispatch based on context
coords = metadata.apply_transform("geo_transform", pixel_coords)
enhanced = metadata.apply_transform("enhance_image", image_data)
```

## Key Standards Referenced
- **CF Conventions**: Mature metadata model for n-dimensional scientific data
- **PROJJSON**: Geospatial coordinate transformation parameters  
- **JSON-LD**: Linked data with vocabulary extension mechanisms
- **Zarr**: Core storage format (with xarray `_ARRAY_DIMENSIONS`)

## Status & Next Steps
- ✅ **Core relations defined** for all dimension types
- ✅ **Transform architecture** with vocabulary extensibility  
- ✅ **Complete integration example** (Landsat multispectral scene)
- 🔄 **Need to develop**: Transform parameter schemas for each vocabulary
- 🔄 **Future**: CF conventions comparison, slice-dependent transforms

## Architecture Benefits
- **Vocabulary agnostic**: Core schema + pluggable domain vocabularies
- **Zarr compatible**: Works with existing scientific data ecosystem
- **Extensible**: New transform types via vocabulary registration
- **Validatable**: Registry ensures implementation completeness
- **Standards-based**: Leverages JSON-LD, PROJ, CF conventions
