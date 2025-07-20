"""
Serialization utilities for space objects.

This module provides functions for converting space objects to various formats,
including dictionaries and JSON strings for use in data interchange.
"""

import json
from typing import Any


def to_data(obj: Any) -> dict[str, Any] | str | Any:
    """
    Convert a space object to its data representation.

    Args:
        obj: Space object to convert

    Returns:
        Data representation suitable for serialization

    Example:
        >>> unit = UnitTerm("m")
        >>> to_data(unit)
        'm'
    """
    if hasattr(obj, "to_data"):
        return obj.to_data()
    else:
        return obj


def to_json(obj: Any, **kwargs) -> str:
    """
    Convert a space object to JSON string.

    Args:
        obj: Space object to convert
        **kwargs: Additional arguments passed to json.dumps

    Returns:
        JSON string representation

    Example:
        >>> unit = UnitTerm("m")
        >>> to_json(unit)
        '"m"'
    """
    data = to_data(obj)
    return json.dumps(data, **kwargs)
