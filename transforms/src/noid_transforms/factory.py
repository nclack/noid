"""
Factory functions for creating transform objects.

This module provides convenient factory functions for creating transform objects
from various input formats, including dictionaries, JSON, and direct parameters.
The factory functions are registered with the registry system for extensibility.
"""

from collections.abc import Sequence
import json
from typing import Any, Union

from .models import (
    CoordinateLookupTable,
    DisplacementLookupTable,
    Homogeneous,
    Identity,
    MapAxis,
    SamplerConfig,
    Scale,
    Transform,
    Translation,
)

# Type aliases
HomogeneousMatrix = Union[Sequence[Sequence[float | int]], Sequence[float | int]]

# Import registry system
from .registry import UnknownTransformError, register, registry, set_namespace

# Set namespace for transforms
set_namespace("https://github.com/nclack/noid/schemas/transforms/")


# Registry-based factory functions
@register
def identity() -> Identity:
    """Create an identity transform.

    Returns:
        Identity transform object that represents no transformation

    Invariants:
        - Always represents the identity operation
        - No parameters required
    """
    return Identity()


@register
def translation(translation: Sequence[float | int]) -> Translation:
    """Create a translation transform.

    Args:
        translation: Translation vector as sequence of numbers (supports lists, tuples, numpy arrays)

    Returns:
        Translation transform object

    Invariants:
        - Translation vector must not be empty
        - All elements must be numeric

    Note:
        Generalized parameter type to Sequence allows numpy arrays and other sequence-like objects.
    """
    return Translation(translation=translation)


@register
def scale(scale: Sequence[float | int]) -> Scale:
    """Create a scale transform.

    Args:
        scale: Scale factors as sequence of numbers (supports lists, tuples, numpy arrays)

    Returns:
        Scale transform object

    Invariants:
        - Scale vector must not be empty
        - All elements must be numeric and non-zero
        - Zero scale factors are not allowed as they are non-invertible

    Note:
        Generalized parameter type to Sequence allows numpy arrays and other sequence-like objects.
    """
    return Scale(scale=scale)


@register("mapAxis")  # Schema uses camelCase, Python uses snake_case
def mapaxis(map_axis: Sequence[int]) -> MapAxis:
    """Create an axis mapping transform.

    Args:
        map_axis: Permutation vector of 0-based input dimension indices (supports lists, tuples, numpy arrays)

    Returns:
        MapAxis transform object

    Invariants:
        - MapAxis vector must not be empty
        - All elements must be non-negative integers
        - Should represent a valid permutation (no duplicate indices)

    Note:
        Generalized parameter type to Sequence allows numpy arrays and other sequence-like objects.
    """
    return MapAxis(mapAxis=map_axis)


@register
def homogeneous(homogeneous: HomogeneousMatrix) -> Homogeneous:
    """Create a homogeneous transformation matrix.

    Args:
        homogeneous: 2D transformation matrix or flat list (supports lists, tuples, numpy arrays)

    Returns:
        Homogeneous transform object

    Invariants:
        - Matrix must not be empty
        - If 2D format: must be rectangular (all rows same length)
        - If flat format: must be a perfect square length
        - All elements must be numeric

    Note:
        Generalized parameter type to Sequence allows numpy arrays and other sequence-like objects.
        Supports both 2D matrix format and flat list format.
    """
    return Homogeneous(homogeneous=homogeneous)


@register
def displacements(
    path: str, interpolation: str = "nearest", extrapolation: str = "nearest"
) -> DisplacementLookupTable:
    """Create a displacement lookup table transform.

    Args:
        path: Path to displacement field data file
        interpolation: Interpolation method
        extrapolation: Extrapolation method

    Returns:
        DisplacementLookupTable transform object

    Invariants:
        - Path must be a valid string
        - Sampling configuration must be valid if provided

    Example:
        >>> # Direct usage
        >>> disp = displacements("path/to/field.zarr", "linear", "zero")
        >>>
        >>> # Registry usage with dict expansion
        >>> from_dict({"displacements": {"path": "path/to/field.zarr", "interpolation": "linear"}})
    """
    config = SamplerConfig(interpolation=interpolation, extrapolation=extrapolation)
    return DisplacementLookupTable(path=path, displacements=config)


@register("lookup_table")  # Schema name for coordinate lookup tables
def coordinate_lookup(
    path: str, interpolation: str = "nearest", extrapolation: str = "nearest"
) -> "CoordinateLookupTable":
    """Create a coordinate lookup table transform.

    Args:
        path: Path to coordinate lookup table data file
        interpolation: Interpolation method
        extrapolation: Extrapolation method

    Returns:
        CoordinateLookupTable transform object

    Invariants:
        - Path must be a valid string
        - Sampling configuration must be valid if provided

    Example:
        >>> # Direct usage
        >>> lookup = coordinate_lookup("path/to/lut.zarr", "cubic", "reflect")
        >>>
        >>> # Registry usage with dict expansion
        >>> from_dict({"lookup_table": {"path": "path/to/lut.zarr", "interpolation": "cubic"}})
    """
    config = SamplerConfig(interpolation=interpolation, extrapolation=extrapolation)
    return CoordinateLookupTable(path=path, lookup_table=config)


# Main orchestration functions
def from_dict(data: dict[str, Any] | str) -> Transform:
    """
    Create a transform from a dictionary or string representation.

    This function uses the registry system for extensible transform creation.

    Args:
        data: Dictionary with transform parameters or "identity" string

    Returns:
        Transform object of appropriate type

    Raises:
        ValueError: If data format is invalid or unsupported

    Example:
        >>> # Identity transform
        >>> identity = from_dict("identity")
        >>>
        >>> # Translation transform
        >>> trans = from_dict({"translation": [10, 20, 5]})
        >>>
        >>> # Scale transform
        >>> scale = from_dict({"scale": [2.0, 1.5, 0.5]})
        >>>
        >>> # Homogeneous transform
        >>> matrix = from_dict({
        ...     "homogeneous": [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
        ... })
    """
    # Handle identity as string
    if data == "identity":
        return identity()

    if not isinstance(data, dict):
        raise ValueError(
            f"Transform data must be a dictionary or 'identity' string, got {type(data)}"
        )

    # Check for exactly one key (self-describing parameter)
    if len(data) != 1:
        raise ValueError(
            f"Transform dictionary must have exactly one key, got {len(data)}"
        )

    key, value = next(iter(data.items()))

    # Use registry-based dispatch
    namespace = "https://github.com/nclack/noid/schemas/transforms/"
    full_iri = f"{namespace}{key}"

    try:
        return registry.create(full_iri, value)
    except UnknownTransformError:
        raise ValueError(f"Unknown transform type: '{key}'")


def from_json(json_str: str) -> Transform:
    """
    Create a transform from a JSON string.

    Args:
        json_str: JSON string representation of transform

    Returns:
        Transform object of appropriate type

    Raises:
        ValueError: If JSON is invalid or transform format is unsupported

    Example:
        >>> trans = from_json('{"translation": [10, 20, 5]}')
        >>> trans.to_dict()
        {'translation': [10.0, 20.0, 5.0]}
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    return from_dict(data)
