"""
NOID Spaces - A LinkML-based Python library for coordinate spaces and dimensions.

This library provides a user-friendly API for working with coordinate spaces and dimensions
defined by the LinkML space schema. It offers enhanced functionality on top of
the generated LinkML classes including validation, serialization, and factory methods.

## Quick Start

```python
import noid_spaces

# Create unit terms
arbitrary_unit = noid_spaces.unit_term("arbitrary")
meter_unit = noid_spaces.unit_term("m")

# Serialize to JSON-LD
json_ld = noid_spaces.to_jsonld(x_dim)

# Validate dimensions
noid_spaces.validate(x_dim)
```

## Types

The library supports unit term functionality from the LinkML schema:

- **UnitTerm**: Non-physical units (index, arbitrary) or physical units via Pint

## API Reference

See individual modules for detailed documentation:

- `models`: Enhanced space model classes
- `factory`: Factory functions for creating space objects
- `serialization`: JSON-LD serialization support
- `validation`: Validation utilities
"""

from .factory import coordinate_system, coordinate_transform, from_data, from_json, unit
from .models import CoordinateTransform, DimensionType, Unit
from .serialization import to_data, to_json
from .validation import ValidationError, validate

__version__ = "0.1.0"

__all__ = [
    # Models
    "Unit",
    "DimensionType",
    "CoordinateTransform",
    # Factory functions
    "unit",
    "coordinate_system",
    "coordinate_transform",
    "from_data",
    "from_json",
    # Serialization
    "to_data",
    "to_json",
    "to_jsonld",
    "from_jsonld",
    # Validation
    "validate",
    "ValidationError",
]

# Import enhanced JSON-LD processing as main API (requires PyLD)
from noid_registry import from_jsonld, to_jsonld

# Internal registry components are imported but not exported
# Users should use the high-level from_jsonld/to_jsonld API
