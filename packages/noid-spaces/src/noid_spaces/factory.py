"""
Factory functions for creating space objects.

This module provides convenient factory functions for creating space objects
from various input formats, including dictionaries, JSON, and direct parameters.
The factory functions are registered with the registry system for extensibility.
"""

import json
from typing import Any

from noid_registry import (
    UnknownIRIError,
    get_schema_namespace,
    register,
    registry,
    set_namespace,
)
import noid_transforms

from .models import CoordinateSystem, CoordinateTransform, Dimension, Unit

# Set namespace for spaces from LinkML schema
set_namespace(get_schema_namespace("space"))


# Registry-based factory functions
@register("unit")
def unit(unit: str | Any) -> Unit:
    """Create a unit term.

    Args:
        unit: Either a special unit ("index", "arbitrary") or physical unit string

    Returns:
        UnitTerm object

    Raises:
        ValueError: If unit is invalid or empty
        pint.UndefinedUnitError: If physical unit is not recognized by Pint

    Invariants:
        - Must be either a valid SpecialUnits value or valid physical unit
        - Physical units are validated using Pint's unit registry

    Example:
        >>> # Special units
        >>> index_unit = unit_term("index")
        >>> arbitrary_unit = unit_term("arbitrary")
        >>>
        >>> # Physical units
        >>> meter_unit = unit_term("m")
        >>> second_unit = unit_term("s")
        >>> density_unit = unit_term("kg/m^3")
    """
    return Unit(unit)


@register("dimension")
def dimension(id: str, unit: str, type: str | None = None) -> Dimension:
    """Create a dimension.

    Args:
        id: Dimension identifier
        unit: Unit specification
        type: Dimension type (optional, inferred from unit if not provided)

    Returns:
        Dimension object

    Example:
        >>> # Direct call with explicit type
        >>> dim = dimension(id="x", unit="m", type="space")
        >>>
        >>> # Direct call with inferred type
        >>> dim = dimension(id="y", unit="mm")  # Infers SPACE
        >>>
        >>> # From registry (expands dict as kwargs)
        >>> dim = from_data({"dimension": {"id": "x", "unit": "m"}})
    """
    data = {"id": id, "unit": unit}
    if type is not None:
        data["type"] = type

    return Dimension.from_data(data)


@register("coordinate-system")
def coordinate_system(
    dimensions: list[dict[str, Any]],
    id: str | None = None,
    description: str | None = None,
) -> CoordinateSystem:
    """Create a coordinate system with automatic dimension creation and labeling.

    This function creates coordinate systems using schema-compliant dimension
    specifications. Dimensions use "id" and "type" fields matching the JSON-LD
    schema. Auto-labeling is supported when "id" is not provided.

    Args:
        dimensions: List of dimension specifications. Each dict can contain:
            - "id": Dimension identifier (optional, auto-generated if not provided)
            - "unit": Unit specification (required)
            - "type": Dimension type (optional, inferred from unit if not provided)
        id: Optional identifier for the coordinate system
        description: Optional description of the coordinate system

    Returns:
        CoordinateSystem object with properly namespaced dimensions

    Example:
        >>> # With explicit IDs
        >>> cs = coordinate_system([
        ...     {"id": "x", "unit": "pixel", "type": "space"},
        ...     {"id": "y", "unit": "pixel", "type": "space"}
        ... ], id="raw_data")
        >>> print(cs.dimensions[0].id)  # "raw_data#x"
        >>>
        >>> # With auto-generated IDs
        >>> cs = coordinate_system([
        ...     {"unit": "pixel", "type": "space"},  # Auto-labeled as dim_0
        ...     {"unit": "pixel", "type": "space"}   # Auto-labeled as dim_1
        ... ], id="image")
        >>> print(cs.dimensions[0].id)  # "image#dim_0"
        >>>
        >>> # Mixed explicit/auto IDs with type inference
        >>> cs = coordinate_system([
        ...     {"id": "x", "unit": "pixel"},        # Explicit ID, inferred type
        ...     {"unit": "pixel"},                   # Auto-ID and inferred type
        ...     {"id": "time", "unit": "ms"}         # Explicit ID, inferred type
        ... ])
        >>>
        >>> # From registry (expands dict as kwargs)
        >>> cs = from_data({
        ...     "coordinate-system": {
        ...         "dimensions": [
        ...             {"id": "x", "unit": "m", "type": "space"},
        ...             {"id": "y", "unit": "m", "type": "space"}
        ...         ]
        ...     }
        ... })
    """
    # Build data dict for CoordinateSystem - let from_data handle dimension conversion
    data: dict[str, Any] = {"dimensions": dimensions}
    if id is not None:
        data["id"] = id
    if description is not None:
        data["description"] = description

    return CoordinateSystem.from_data(data)


@register("coordinate-transform")
def coordinate_transform(
    input: dict[str, Any],
    output: dict[str, Any],
    transform: dict[str, Any],
    id: str | None = None,
    description: str | None = None,
) -> CoordinateTransform:
    """Create a coordinate transform.

    Args:
        input: Input coordinate system specification as dictionary
        output: Output coordinate system specification as dictionary
        transform: Transform definition as dictionary
        id: Optional identifier for the coordinate transform
        description: Optional description of the coordinate transform

    Returns:
        CoordinateTransform object

    Example:
        >>> # Direct call
        >>> ct = coordinate_transform(
        ...     input={"dimensions": [{"id": "x", "unit": "pixel"}]},
        ...     output={"dimensions": [{"id": "x", "unit": "mm"}]},
        ...     transform={"translation": [0.1]}
        ... )
        >>>
        >>> # From registry (expands dict as kwargs)
        >>> ct = from_data({
        ...     "coordinate-transform": {
        ...         "input": {"dimensions": [{"id": "x", "unit": "pixel"}]},
        ...         "output": {"dimensions": [{"id": "x", "unit": "mm"}]},
        ...         "transform": {"translation": [0.1]}
        ...     }
        ... })
    """
    # Convert coordinate system data to CoordinateSystem objects
    input_cs = CoordinateSystem.from_data(input)
    output_cs = CoordinateSystem.from_data(output)

    try:
        transform_obj = noid_transforms.from_data(transform)
    except Exception as e:
        raise ValueError(f"Failed to create transform from data: {e}") from e

    return CoordinateTransform(
        input=input_cs,
        output=output_cs,
        transform=transform_obj,
        id=id,
        description=description,
    )


# Main orchestration functions
def from_data(data: dict[str, Any] | str) -> Any:
    """
    Create a space object from a data representation.

    This function uses the registry system for extensible space object creation.

    Args:
        data: Dictionary with object parameters or string for simple types

    Returns:
        Space object of appropriate type

    Raises:
        ValueError: If data format is invalid or unsupported

    Example:
        >>> # Unit term
        >>> unit = from_data({"unit-term": "m"})
        >>>
        >>> # Dimension
        >>> dim = from_data({"dimension": {"id": "x", "unit": "m", "type": "space"}})
    """
    # Handle simple string cases
    if isinstance(data, str):
        # For now, assume string inputs are unit terms
        return unit(data)

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


def from_json(json_str: str) -> Any:
    """
    Create a space object from a JSON string.

    Args:
        json_str: JSON string representation of space object

    Returns:
        Space object of appropriate type

    Raises:
        ValueError: If JSON is invalid or space format is unsupported

    Example:
        >>> unit = from_json('{"unit-term": "m"}')
        >>> unit.to_data()
        'm'
        >>>
        >>> dim = from_json('{"dimension": {"id": "x", "unit": "m", "type": "space"}}')
        >>> dim.id
        'x'
    """
    data = json.loads(json_str)
    return from_data(data)
