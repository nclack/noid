"""
NOID Transforms - A LinkML-based Python library for coordinate transformations.

This library provides a user-friendly API for working with coordinate transformations
defined by the LinkML transforms schema. It offers enhanced functionality on top of
the generated LinkML classes including validation, serialization, and factory methods.

## Quick Start

```python
import noid_transforms

# Create transforms using factory functions
translation = noid_transforms.translation([10, 20, 5])
scale = noid_transforms.scale([2.0, 1.5, 0.5])
identity = noid_transforms.identity()

# Create from dictionaries
homogeneous = noid_transforms.from_dict({
    "homogeneous": [
        [2.0, 0, 0, 10],
        [0, 1.5, 0, 20],
        [0, 0, 0.5, 5],
        [0, 0, 0, 1]
    ]
})

# Serialize to JSON-LD
json_ld = noid_transforms.to_jsonld(translation)

# Validate transforms
noid_transforms.validate(translation)
```

## Transform Types

The library supports all transform types defined in the LinkML schema:

- **Identity**: No transformation
- **Translation**: Translation vector
- **Scale**: Scale factors  
- **MapAxis**: Axis permutation
- **Homogeneous**: Matrix transformation
- **DisplacementLookupTable**: Displacement field lookup
- **CoordinateLookupTable**: Coordinate lookup table

## API Reference

See individual modules for detailed documentation:

- `models`: Enhanced transform model classes
- `factory`: Factory functions for creating transforms
- `serialization`: JSON-LD serialization support
- `validation`: Validation utilities
"""

from typing import Optional

from .models import (
    Transform,
    Identity,
    Translation,
    Scale,
    MapAxis,
    Homogeneous,
    DisplacementLookupTable,
    CoordinateLookupTable,
    SamplerConfig,
    InterpolationMethod,
    ExtrapolationMethod,
)

from .factory import (
    identity,
    translation,
    scale,
    mapaxis,
    homogeneous,
    displacements,
    coordinate_lookup,
    from_dict,
    from_json,
)

from .serialization import (
    to_dict,
    to_json,
)

# Import factory functions to ensure they get registered
try:
    from . import factory
except ImportError:
    # Registry not available - skip registration
    pass

from .validation import (
    validate,
    validate_dimension_consistency,
    check_transform_compatibility,
    ValidationError,
)

__version__ = "0.1.0"

__all__ = [
    # Models
    "Transform",
    "Identity", 
    "Translation",
    "Scale",
    "MapAxis",
    "Homogeneous",
    "DisplacementLookupTable",
    "CoordinateLookupTable",
    "SamplerConfig",
    "InterpolationMethod",
    "ExtrapolationMethod",
    
    # Factory functions
    "identity",
    "translation", 
    "scale",
    "mapaxis",
    "homogeneous",
    "displacements",
    "coordinate_lookup",
    "from_dict",
    "from_json",
    
    # Serialization
    "to_dict",
    "to_json",
    "to_jsonld",
    "from_jsonld",
    
    # Validation
    "validate",
    "validate_dimension_consistency",
    "check_transform_compatibility",
    "ValidationError",
]

# Import enhanced JSON-LD processing as main API (requires PyLD)
from .jsonld_processing import from_jsonld as _enhanced_from_jsonld, to_jsonld as _enhanced_to_jsonld

# Override the legacy versions with enhanced ones (with backward compatibility wrappers)
from_jsonld = _enhanced_from_jsonld

def to_jsonld(transform, include_context: bool = True, indent: Optional[int] = None) -> str:
    """Backward compatible wrapper for enhanced to_jsonld that always returns a string."""
    result = _enhanced_to_jsonld(transform, include_context, indent)
    if isinstance(result, str):
        return result
    else:
        # Enhanced version returned a dict, convert to string for backward compatibility
        import json
        return json.dumps(result, indent=indent)

# Internal registry components are imported but not exported
# Users should use the high-level from_jsonld/to_jsonld API