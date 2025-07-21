# noid-spaces

Coordinate spaces vocabulary for multidimensional arrays.

This package provides LinkML-based models for defining coordinate systems, dimensions, and coordinate transforms for scientific datasets involving multidimensional arrays.

## Features

- **Dimension Identity & Namespacing**: Automatic dimension labeling with global ID generation using IRI fragment syntax
- **Factory Functions**: Schema-compliant creation with auto-labeling and type inference
- **Unit Vocabularies**: UDUNITS-2 compatible units with automatic type inference (space, time, index, other)
- **Coordinate Systems**: Collections of dimensions with proper ownership validation
- **Transform Validation**: 4-tier dimension compatibility checking for transform chains
- **JSON-LD Integration**: Roundtrip serialization preserving dimension identity
- **Dimension Reuse Prevention**: Validation to prevent improper dimension sharing between coordinate systems

## Installation

```bash
pip install noid-spaces
```

## Quick Start

```python
from noid_spaces import coordinate_system, to_jsonld, from_jsonld

# Factory function with auto-labeling and type inference
cs = coordinate_system(
    dimensions=[
        {"id": "x", "unit": "μm", "type": "space"},      # Explicit ID
        {"unit": "μm", "type": "space"},                 # Auto-labeled as "dim_0"
        {"id": "time", "unit": "ms"}                     # Type inferred as TIME
    ],
    id="microscopy_data",
    description="3D microscopy coordinate system"
)

# Access namespaced dimension IDs
print(cs.dimensions[0].id)  # "microscopy_data#x"
print(cs.dimensions[1].id)  # "microscopy_data#dim_0"
print(cs.dimensions[2].id)  # "microscopy_data#time"

# JSON-LD serialization preserves dimension identity
jsonld_data = to_jsonld(cs)
reconstructed = from_jsonld(jsonld_data)

# Transform chain validation with dimension ID checking
from noid_spaces.models import CoordinateTransform
from noid_spaces.validation import validate_transform_chain
import noid_transforms

input_cs = coordinate_system([{"id": "x", "unit": "pixel"}], id="raw")
output_cs = coordinate_system([{"id": "x", "unit": "mm"}], id="physical")

transform = CoordinateTransform(
    input=input_cs,
    output=output_cs,
    transform=noid_transforms.scale([0.1])  # 0.1mm per pixel
)

validate_transform_chain([transform], strict=True)  # Passes validation
```

## Unit Vocabulary

The package includes a controlled vocabulary for measurement units including:

- **Spatial**: meter, millimeter, micrometer, nanometer, pixel
- **Temporal**: second, millisecond, minute, hour
- **Angular**: radian, degree
- **Universal**: index, arbitrary

All units follow UDUNITS-2 conventions where applicable.

## Examples and Documentation

### Comprehensive Examples
- **[dimension_identity_usage.py](examples/dimension_identity_usage.py)**: Complete Python example demonstrating all features
- **[dimension_sequence.jsonld](examples/dimension_sequence.jsonld)**: JSON-LD with namespaced dimensions
- **[transforms_and_spaces.jsonld](examples/transforms_and_spaces.jsonld)**: Complex transform scenarios
- **[Examples README](examples/README.md)**: Detailed guide to all example files

### Documentation
- **[Dimension Identity RFC](../../docs/dimension-identity-namespacing-rfc.md)**: Complete technical specification
- **[API Documentation](src/noid_spaces/)**: Source code with comprehensive docstrings
- **[Test Suite](tests/)**: Extensive test examples covering all functionality

### Key Features Demonstrated
- **Auto-labeling**: `dim_0`, `dim_1` generation when IDs not provided
- **Type inference**: Automatic detection of dimension types from units
- **Namespacing**: Global IDs using `coordinate_system#dimension` syntax
- **JSON-LD roundtrips**: Perfect serialization/deserialization
- **Transform validation**: 4-tier compatibility checking
- **Reuse prevention**: Validation against improper dimension sharing
