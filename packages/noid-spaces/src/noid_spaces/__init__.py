"""
NOID Spaces - A LinkML-based Python library for coordinate spaces and dimensions.

This library provides a user-friendly API for working with coordinate spaces,
dimensions, and coordinate transforms defined by the LinkML space schema.
It offers enhanced functionality including UDUNITS-2 validation, factory methods,
and JSON-LD serialization.

## Quick Start

```python
import noid_spaces

# Create dimensions
x_dim = noid_spaces.dimension("x", "micrometer", "space")
y_dim = noid_spaces.dimension("y", "micrometer", "space")
time_dim = noid_spaces.dimension("t", "second", "time")

# Create coordinate system
physical_space = noid_spaces.coordinate_system(
    "physical",
    [x_dim, y_dim, time_dim],
    "Physical coordinate system"
)

# Create from dictionaries
array_space = noid_spaces.from_dict({
    "coordinate-system": {
        "id": "array",
        "dimensions": [
            {"id": "i", "unit": "index", "type": "index"},
            {"id": "j", "unit": "index", "type": "index"},
            {"id": "k", "unit": "index", "type": "index"}
        ]
    }
})

# Create coordinate transform
transform = noid_spaces.coordinate_transform(
    "physical_to_array",
    "physical",
    "array",
    {"scale": [0.5, 0.5, 1.0]}
)

# Serialize to JSON-LD
json_ld = noid_spaces.to_jsonld(physical_space)

# Validate units with UDUNITS-2
noid_spaces.validate_dimension_unit("meter", "space")
```

## Core Classes

The library provides enhanced versions of the LinkML-generated classes:

- **Dimension**: Individual axis with unit and type classification
- **CoordinateSystem**: Collection of dimensions defining a coordinate space
- **CoordinateTransform**: Mapping between coordinate spaces with transform definition

## Validation

Built-in UDUNITS-2 validation for unit strings:

- Validates spatial and temporal units against UDUNITS-2 standard
- Supports special units: "index", "arbitrary"
- Enforces type-specific constraints (e.g., index dimensions must use "index" unit)

## API Reference

See individual modules for detailed documentation:

- `models`: Enhanced space model classes
- `factory`: Factory functions for creating space objects
- `validation`: UDUNITS-2 validation utilities
"""

from .factory import (
    coordinate_system,
    coordinate_transform,
    dimension,
    from_dict,
    from_json,
)
from .models import (
    CoordinateSystem,
    CoordinateTransform,
    Dimension,
    DimensionType,
    SpecialUnits,
    UnitTerm,
)
from .validation import (
    UdunitsValidationError,
    get_udunits_info,
    is_valid_dimension_unit,
    is_valid_udunits_string,
    validate_dimension_unit,
    validate_udunits_string,
)

__version__ = "0.1.0"

__all__ = [
    # Models
    "Dimension",
    "CoordinateSystem",
    "CoordinateTransform",
    "DimensionType",
    "SpecialUnits",
    "UnitTerm",
    # Factory functions
    "dimension",
    "coordinate_system",
    "coordinate_transform",
    "from_dict",
    "from_json",
    # Validation
    "validate_udunits_string",
    "is_valid_udunits_string",
    "validate_dimension_unit",
    "is_valid_dimension_unit",
    "get_udunits_info",
    "UdunitsValidationError",
    # JSON-LD functions (imported from noid-registry)
    "to_jsonld",
    "from_jsonld",
]

# Import enhanced JSON-LD processing as main API (requires noid-registry)
from noid_registry import from_jsonld, to_jsonld

# Import factory functions to ensure they get registered
try:
    from . import factory
except ImportError:
    # Registry not available - skip registration
    pass
