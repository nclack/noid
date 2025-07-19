"""
Factory functions for creating coordinate space objects.

This module provides convenient factory functions for creating coordinate space
objects from various input formats, including dictionaries, JSON, and direct parameters.
The factory functions are registered with the registry system for extensibility.
"""

from collections.abc import Sequence
import json
from typing import Any

from noid_registry import (
    UnknownIRIError,
    get_schema_namespace,
    register,
    registry,
    set_namespace,
)

from .models import CoordinateSystem, CoordinateTransform, Dimension

# Set namespace for spaces from LinkML schema
set_namespace(get_schema_namespace("space"))


# Registry-based factory functions
@register()
def dimension(id: str, unit: str, type: str) -> Dimension:
    """Create a dimension.

    Args:
        id: Unique identifier for the dimension
        unit: Unit of measurement (special units or UDUNITS-2 compatible)
        type: Dimension type ('space', 'time', 'other', 'index')

    Returns:
        Dimension object

    Invariants:
        - ID must be a non-empty string
        - Unit must be valid (special units or UDUNITS-2 compatible)
        - Type must be one of: space, time, other, index
        - If type is "index", unit must be "index"

    Example:
        >>> dimension("x", "micrometer", "space")
        >>> dimension("t", "second", "time")
        >>> dimension("channel", "arbitrary", "other")
        >>> dimension("i", "index", "index")
    """
    return Dimension(id=id, unit=unit, type=type)


# CLAUDE: I'm getting type errors for register. How to fix?
@register("coordinate-system")  # Schema uses kebab-case, Python uses snake_case
def coordinate_system(
    id: str,
    dimensions: Sequence[dict | str],
    description: str | None = None,
) -> CoordinateSystem:
    """Create a coordinate system.

    Args:
        id: Unique identifier for the coordinate system
        dimensions: List of dimensions (dicts, Dimension objects or string references)
        description: Optional description

    Returns:
        CoordinateSystem object

    Invariants:
        - ID must be a non-empty string
        - Must have at least one dimension
        - All dimensions must be valid

    Example:
        >>> coordinate_system("physical", [
        ...     {"id": "x", "unit": "micrometer", "type": "space"},
        ...     {"id": "y", "unit": "micrometer", "type": "space"}
        ... ])
        >>> coordinate_system("array", ["i", "j", "k"])
    """
    # Convert dimension dicts to Dimension objects if needed
    processed_dims = []
    for dim in dimensions:
        if isinstance(dim, dict):
            processed_dims.append(Dimension(**dim))
        else:
            processed_dims.append(dim)

    return CoordinateSystem(id=id, dimensions=processed_dims, description=description)


@register("coordinate-transform")  # Schema uses kebab-case
def coordinate_transform(
    id: str,
    input: str | dict | list,
    output: str | dict | list,
    transform: dict,
    description: str | None = None,
) -> CoordinateTransform:
    """Create a coordinate transform.

    Args:
        id: Unique identifier for the transform
        input: Input coordinate space specification
        output: Output coordinate space specification
        transform: Transform definition
        description: Optional description

    Returns:
        CoordinateTransform object

    Invariants:
        - ID must be a non-empty string
        - Must have valid input and output coordinate space specifications
        - Must have a valid transform definition

    Example:
        >>> coordinate_transform(
        ...     "physical_to_array",
        ...     "physical_space",
        ...     "array_space",
        ...     {"scale": [0.5, 0.5, 1.0]}
        ... )
    """
    return CoordinateTransform(
        id=id,
        input=input,
        output=output,
        transform=transform,
        description=description,
    )


# Main orchestration functions
def from_dict(
    data: dict[str, Any],
) -> Dimension | CoordinateSystem | CoordinateTransform:
    """
    Create a space object from a dictionary representation.

    This function uses the registry system for extensible object creation.

    Args:
        data: Dictionary with object parameters

    Returns:
        Space object of appropriate type (Dimension, CoordinateSystem, or CoordinateTransform)

    Raises:
        ValueError: If data format is invalid or unsupported

    Example:
        >>> # Dimension
        >>> dim = from_dict({
        ...     "dimension": {
        ...         "id": "x",
        ...         "unit": "micrometer",
        ...         "type": "space"
        ...     }
        ... })
        >>>
        >>> # Coordinate system
        >>> coord_sys = from_dict({
        ...     "coordinate-system": {
        ...         "id": "physical",
        ...         "dimensions": [
        ...             {"id": "x", "unit": "micrometer", "type": "space"},
        ...             {"id": "y", "unit": "micrometer", "type": "space"}
        ...         ]
        ...     }
        ... })
        >>>
        >>> # Coordinate transform
        >>> coord_transform = from_dict({
        ...     "coordinate-transform": {
        ...         "id": "physical_to_array",
        ...         "input": "physical_space",
        ...         "output": "array_space",
        ...         "transform": {"scale": [0.5, 0.5, 1.0]}
        ...     }
        ... })
    """
    # Check for exactly one key (self-describing parameter)
    if len(data) != 1:
        raise ValueError(f"Space dictionary must have exactly one key, got {len(data)}")

    key, value = next(iter(data.items()))

    # Use registry-based dispatch - get namespace from LinkML schema
    namespace = get_schema_namespace("space")
    # Ensure namespace has trailing slash to match set_namespace behavior
    namespace = namespace.rstrip("/") + "/"
    full_iri = f"{namespace}{key}"

    try:
        return registry.create(full_iri, value)
    except UnknownIRIError as e:
        raise ValueError(f"Unknown space type: '{key}'") from e


def from_json(json_str: str) -> Dimension | CoordinateSystem | CoordinateTransform:
    """
    Create a space object from a JSON string.

    Args:
        json_str: JSON string representation of space object

    Returns:
        Space object of appropriate type

    Raises:
        ValueError: If JSON is invalid or space format is unsupported

    Example:
        >>> dim = from_json('{"dimension": {"id": "x", "unit": "micrometer", "type": "space"}}')
        >>> dim.to_dict()
        {'id': 'x', 'unit': 'micrometer', 'type': 'space'}
    """
    data = json.loads(json_str)
    return from_dict(data)
