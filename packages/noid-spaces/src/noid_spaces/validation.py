"""
Validation utilities for space objects.

This module provides validation functions for space objects, ensuring they
conform to expected schemas and constraints.
"""

from typing import Any


class ValidationError(Exception):
    """Exception raised when validation fails."""

    pass


def validate(obj: Any) -> None:
    """
    Validate a space object.

    Args:
        obj: Space object to validate

    Raises:
        ValidationError: If validation fails

    Example:
        >>> unit = UnitTerm("m")
        >>> validate(unit)  # No exception means valid
    """
    # For now, basic validation - objects that can be created are considered valid
    # This can be extended with more sophisticated validation as needed
    if hasattr(obj, "to_data"):
        try:
            obj.to_data()
        except Exception as e:
            raise ValidationError(f"Object failed serialization test: {e}") from e
    else:
        # Simple objects are considered valid if they exist
        pass
