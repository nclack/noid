"""
Public API for NOID schema classes with post-generation validation.

This module provides the public API for NOID's schema classes, combining
auto-generated Pydantic models with custom validation logic. Users should
import classes from this module rather than from the private _schema module.

## Approach

NOID uses a three-layer validation approach to provide robust schema validation
while maintaining clean separation between generated and custom code:

1. JSON Schema files in schemas/ are automatically converted to Pydantic models
   in _schema.py using datamodel-codegen.

2. Custom validation logic is implemented as mixins in _schema_validation.py,
   focusing on business rules that cannot be expressed in JSON Schema alone.

"""

from ._schema import (
    CoordinateSpacesSchema,
    DimensionType,
    Dimension as _Dimension,
    CoordinateSystem,
    Translation,
    Scale,
    MapAxis,
    Homogeneous,
    Interpolation,
    Extrapolation,
    Displacements,
    DisplacementLookupTable,
    CoordinateLookupTable,
    Transform,
    CoordinateTransform,
)

from ._schema_validation import DimensionValidationMixin


class Dimension(DimensionValidationMixin, _Dimension):
    """
    A dimension within a coordinate space with enhanced validation.

    Extends the generated Dimension class with business rule validation:
    - Index dimensions must have 'index' unit

    Args:
        id: Unique identifier for the dimension
        unit: Unit of measurement (UDUNITS-2 terms, 'index', or 'arbitrary')
        type: Dimension type ('space', 'time', 'other', or 'index')

    Example:
        >>> # Valid dimensions
        >>> spatial_dim = Dimension(id="x", unit="micrometers", type=DimensionType.space)
        >>> index_dim = Dimension(id="i", unit="index", type=DimensionType.index)
        >>>
        >>> # Invalid - will raise ValueError
        >>> bad_dim = Dimension(id="i", unit="micrometers", type=DimensionType.index)
    """

    pass


# Re-export everything we want to be public
__all__ = [
    "CoordinateSpacesSchema",
    "DimensionType",
    "Dimension",
    "CoordinateSystem",
    "Translation",
    "Scale",
    "MapAxis",
    "Homogeneous",
    "Interpolation",
    "Extrapolation",
    "Displacements",
    "DisplacementLookupTable",
    "CoordinateLookupTable",
    "Transform",
    "CoordinateTransform",
]
