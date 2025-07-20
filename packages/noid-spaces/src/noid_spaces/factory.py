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

from .models import Dimension, UnitTerm

# Set namespace for spaces from LinkML schema
set_namespace(get_schema_namespace("space"))


# Registry-based factory functions
@register("unit")
def unit_term(unit: str | Any) -> UnitTerm:
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
    return UnitTerm(unit)


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
        return unit_term(data)

    if not isinstance(data, dict):
        raise ValueError(f"Space data must be a dictionary or string, got {type(data)}")

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
