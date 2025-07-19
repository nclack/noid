"""
UDUNITS-2 validation utilities.

This module provides validation functions for unit strings using the py_udunits2 library,
which interfaces with the UDUNITS-2 library for validating physical unit expressions.
"""

from typing import Any

try:
    import udunits2 as py_udunits2
except ImportError:
    py_udunits2 = None


class UdunitsValidationError(ValueError):
    """Raised when a unit string fails UDUNITS-2 validation."""
    pass


def validate_udunits_string(unit_string: str) -> bool:
    """
    Validate a unit string using UDUNITS-2.

    Args:
        unit_string: The unit string to validate

    Returns:
        True if the unit string is valid according to UDUNITS-2

    Raises:
        UdunitsValidationError: If the unit string is invalid
        ImportError: If py_udunits2 is not available

    Example:
        >>> validate_udunits_string("meter")
        True
        >>> validate_udunits_string("m")
        True
        >>> validate_udunits_string("micrometer")
        True
        >>> validate_udunits_string("invalid_unit")
        Traceback (most recent call last):
        ...
        UdunitsValidationError: Invalid UDUNITS-2 unit string: 'invalid_unit'
    """
    if py_udunits2 is None:
        raise ImportError(
            "udunits2 is required for UDUNITS-2 validation. "
            "Install it with: pip install udunits2"
        )

    try:
        # Try to parse the unit string with UDUNITS-2
        unit = py_udunits2.Unit(unit_string)
        # If we can create a Unit object, the string is valid
        return True
    except Exception as e:
        raise UdunitsValidationError(
            f"Invalid UDUNITS-2 unit string: '{unit_string}'. Error: {e}"
        ) from e


def is_valid_udunits_string(unit_string: str) -> bool:
    """
    Check if a unit string is valid according to UDUNITS-2.

    This is a non-throwing version of validate_udunits_string.

    Args:
        unit_string: The unit string to check

    Returns:
        True if the unit string is valid, False otherwise

    Note:
        Returns False if py_udunits2 is not available instead of raising ImportError

    Example:
        >>> is_valid_udunits_string("meter")
        True
        >>> is_valid_udunits_string("invalid_unit")
        False
    """
    try:
        validate_udunits_string(unit_string)
        return True
    except (UdunitsValidationError, ImportError):
        return False


def validate_dimension_unit(unit: str, dimension_type: str) -> bool:
    """
    Validate a unit string for a specific dimension type.

    This function validates that:
    1. Special units ("index", "arbitrary") are valid for any dimension type
    2. For space/time dimensions, the unit must be a valid UDUNITS-2 string
    3. For other dimensions, any unit is allowed (including UDUNITS-2 strings)

    Args:
        unit: The unit string to validate
        dimension_type: The type of dimension ('space', 'time', 'other', 'index')

    Returns:
        True if the unit is valid for the given dimension type

    Raises:
        UdunitsValidationError: If validation fails
        ValueError: If dimension_type is invalid

    Example:
        >>> validate_dimension_unit("index", "index")
        True
        >>> validate_dimension_unit("arbitrary", "other")
        True
        >>> validate_dimension_unit("meter", "space")
        True
        >>> validate_dimension_unit("second", "time")
        True
        >>> validate_dimension_unit("invalid_unit", "space")
        Traceback (most recent call last):
        ...
        UdunitsValidationError: Invalid UDUNITS-2 unit string: 'invalid_unit'
    """
    if dimension_type not in ["space", "time", "other", "index"]:
        raise ValueError(f"Invalid dimension type: '{dimension_type}'. Must be one of: space, time, other, index")

    # Special units are valid for all dimension types
    if unit in ["index", "arbitrary"]:
        return True

    # Index dimensions must use "index" unit
    if dimension_type == "index":
        if unit != "index":
            raise UdunitsValidationError(
                f"Index dimensions must use 'index' unit, got '{unit}'"
            )
        return True

    # For space/time dimensions, validate with UDUNITS-2
    if dimension_type in ["space", "time"]:
        return validate_udunits_string(unit)

    # For "other" dimensions, any unit is allowed (but still validate UDUNITS-2 if it looks like one)
    # We don't enforce UDUNITS-2 validation for "other" dimensions to allow custom units
    return True


def is_valid_dimension_unit(unit: str, dimension_type: str) -> bool:
    """
    Check if a unit string is valid for a specific dimension type.

    This is a non-throwing version of validate_dimension_unit.

    Args:
        unit: The unit string to check
        dimension_type: The type of dimension

    Returns:
        True if the unit is valid for the given dimension type, False otherwise

    Example:
        >>> is_valid_dimension_unit("meter", "space")
        True
        >>> is_valid_dimension_unit("invalid_unit", "space")
        False
    """
    try:
        validate_dimension_unit(unit, dimension_type)
        return True
    except (UdunitsValidationError, ValueError):
        return False


def get_udunits_info(unit_string: str) -> dict[str, Any] | None:
    """
    Get information about a UDUNITS-2 unit string.

    Args:
        unit_string: The unit string to analyze

    Returns:
        Dictionary with unit information, or None if py_udunits2 is not available

    Example:
        >>> info = get_udunits_info("meter")
        >>> info is not None
        True
    """
    if py_udunits2 is None:
        return None

    try:
        unit = py_udunits2.Unit(unit_string)
        return {
            "unit_string": unit_string,
            "is_valid": True,
            "definition": str(unit),
        }
    except Exception:
        return {
            "unit_string": unit_string,
            "is_valid": False,
            "definition": None,
        }
