"""
Validation utilities for space objects.

This module provides validation functions for space objects, ensuring they
conform to expected schemas and constraints, with support for dimensional
compatibility, transform parameter validation, and unit compatibility checks.
"""

from typing import TYPE_CHECKING, Any
import warnings

if TYPE_CHECKING:
    from .models import CoordinateSystem, CoordinateTransform, Dimension


class ValidationError(Exception):
    """Exception raised when validation fails."""

    pass


class ValidationWarning(UserWarning):
    """Warning raised for non-critical validation issues."""

    pass


def validate(obj: Any, strict: bool = True) -> None:
    """
    Validate a space object with comprehensive checks.

    Args:
        obj: Space object to validate
        strict: If True, all validation issues raise errors. If False,
               some issues (like unit compatibility) may only warn.

    Raises:
        ValidationError: If validation fails
        ValidationWarning: If non-critical issues found (when strict=False)

    Example:
        >>> unit = Unit("m")
        >>> validate(unit)  # No exception means valid
        >>>
        >>> # Validate coordinate transform
        >>> ct = CoordinateTransform(input=cs1, output=cs2, transform=translation)
        >>> validate(ct, strict=True)  # Comprehensive validation
    """
    # Import here to avoid circular imports
    from .models import CoordinateSystem, CoordinateTransform, Dimension

    # Basic serialization validation (existing functionality)
    if hasattr(obj, "to_data"):
        try:
            obj.to_data()
        except Exception as e:
            raise ValidationError(f"Object failed serialization test: {e}") from e

    # Type-specific validation
    if isinstance(obj, CoordinateTransform):
        validate_coordinate_transform(obj, strict=strict)
    elif isinstance(obj, CoordinateSystem):
        validate_coordinate_system(obj, strict=strict)
    elif isinstance(obj, Dimension):
        validate_dimension(obj, strict=strict)
    # Unit validation happens in constructor via Pint, so no additional validation needed


def validate_coordinate_transform(
    transform: "CoordinateTransform", strict: bool = True
) -> None:
    """
    Validate a coordinate transform with comprehensive checks.

    Args:
        transform: CoordinateTransform to validate
        strict: If True, all issues raise errors. If False, some may warn.

    Raises:
        ValidationError: For critical validation failures
        ValidationWarning: For non-critical issues (when strict=False)
    """
    # 1. Dimensional compatibility validation (ALWAYS CRITICAL)
    _validate_dimensional_compatibility(transform)

    # 2. Transform parameter validation (ALWAYS CRITICAL)
    _validate_transform_parameters(transform)

    # 3. Unit compatibility validation (can be warning in non-strict mode)
    _validate_unit_compatibility(transform, strict=strict)


def validate_coordinate_system(
    coord_system: "CoordinateSystem", strict: bool = True
) -> None:
    """
    Validate a coordinate system.

    Args:
        coord_system: CoordinateSystem to validate
        strict: If True, all issues raise errors. If False, some may warn.

    Raises:
        ValidationError: For critical validation failures
    """
    # Validate each dimension
    for dim in coord_system.dimensions:
        validate_dimension(dim, strict=strict)

    # Check for duplicate dimension IDs
    dim_ids = [dim.id for dim in coord_system.dimensions]
    if len(dim_ids) != len(set(dim_ids)):
        duplicates = [dim_id for dim_id in set(dim_ids) if dim_ids.count(dim_id) > 1]
        raise ValidationError(f"Duplicate dimension IDs found: {duplicates}")


def validate_dimension(dimension: "Dimension", strict: bool = True) -> None:
    """
    Validate a dimension.

    Args:
        dimension: Dimension to validate
        strict: If True, all issues raise errors. If False, some may warn.

    Raises:
        ValidationError: For critical validation failures
    """
    # Unit validation happens in constructor via Pint, so no additional validation needed

    # Validate type-unit consistency (from LinkML schema rules)
    if dimension.type.value == "index" and dimension.unit.value != "index":
        raise ValidationError(
            f"Dimension type 'index' requires unit 'index', got '{dimension.unit.value}'"
        )


def _validate_dimensional_compatibility(transform: "CoordinateTransform") -> None:
    """
    Validate dimensional compatibility between coordinate systems and transform.
    This is always critical and will raise errors.
    """
    input_dims = len(transform.input.dimensions)
    output_dims = len(transform.output.dimensions)
    transform_obj = transform.transform

    # Get transform type name for better error messages
    transform_type = type(transform_obj).__name__

    # Check dimensional compatibility based on transform type
    if hasattr(transform_obj, "dimensions"):
        # For transforms with explicit dimension requirements
        expected_dims = transform_obj.dimensions
        if input_dims != expected_dims:
            raise ValidationError(
                f"{transform_type} transform expects {expected_dims} dimensions, "
                f"but input coordinate system has {input_dims}"
            )
        if output_dims != expected_dims:
            raise ValidationError(
                f"{transform_type} transform expects {expected_dims} dimensions, "
                f"but output coordinate system has {output_dims}"
            )
    elif hasattr(transform_obj, "input_dimensions") and hasattr(
        transform_obj, "output_dimensions"
    ):
        # For transforms like MapAxis with different input/output dimensions
        expected_input = transform_obj.input_dimensions
        expected_output = transform_obj.output_dimensions
        if input_dims != expected_input:
            raise ValidationError(
                f"{transform_type} transform expects {expected_input} input dimensions, "
                f"but input coordinate system has {input_dims}"
            )
        if output_dims != expected_output:
            raise ValidationError(
                f"{transform_type} transform expects {expected_output} output dimensions, "
                f"but output coordinate system has {output_dims}"
            )
    else:
        # For generic transforms, assume input/output dimensions should match
        if input_dims != output_dims:
            raise ValidationError(
                f"{transform_type} transform requires matching input/output dimensions, "
                f"but got input={input_dims}, output={output_dims}"
            )


def _validate_transform_parameters(transform: "CoordinateTransform") -> None:
    """
    Validate transform parameters against coordinate system dimensions.
    This is always critical and will raise errors.
    """
    input_dims = len(transform.input.dimensions)
    output_dims = len(transform.output.dimensions)
    transform_obj = transform.transform
    transform_type = type(transform_obj).__name__

    # Validate specific transform types
    if transform_type == "Translation":
        translation_dims = len(transform_obj.translation)
        if translation_dims != input_dims:
            raise ValidationError(
                f"Translation vector has {translation_dims} elements but "
                f"coordinate system has {input_dims} dimensions"
            )

    elif transform_type == "Scale":
        scale_dims = len(transform_obj.scale)
        if scale_dims != input_dims:
            raise ValidationError(
                f"Scale vector has {scale_dims} elements but "
                f"coordinate system has {input_dims} dimensions"
            )
        # Check for zero scale factors
        if any(s == 0 for s in transform_obj.scale):
            raise ValidationError("Scale factors cannot be zero")

    elif transform_type == "MapAxis":
        # Validate axis indices are in bounds
        max_index = max(transform_obj.map_axis)
        if max_index >= input_dims:
            raise ValidationError(
                f"MapAxis contains index {max_index} but input has only {input_dims} dimensions"
            )
        # Check for duplicate indices
        if len(set(transform_obj.map_axis)) != len(transform_obj.map_axis):
            raise ValidationError("MapAxis contains duplicate axis indices")

    elif transform_type == "Homogeneous":
        # Validate matrix dimensions
        matrix = transform_obj.get_matrix()
        expected_rows = output_dims + 1  # +1 for homogeneous coordinates
        expected_cols = input_dims + 1
        if matrix.shape != (expected_rows, expected_cols):
            raise ValidationError(
                f"Homogeneous matrix has shape {matrix.shape} but expected "
                f"({expected_rows}, {expected_cols}) for {input_dims}D→{output_dims}D transform"
            )


def _validate_unit_compatibility(
    transform: "CoordinateTransform", strict: bool = True
) -> None:
    """
    Validate unit compatibility between input and output coordinate systems.
    In strict mode, raises errors. In non-strict mode, may only warn.
    """
    input_dims = transform.input.dimensions
    output_dims = transform.output.dimensions

    # Only check if dimensions match (already validated in dimensional compatibility)
    if len(input_dims) != len(output_dims):
        return

    for i, (input_dim, output_dim) in enumerate(
        zip(input_dims, output_dims, strict=False)
    ):
        input_type = input_dim.type
        output_type = output_dim.type
        input_unit = input_dim.unit.value
        output_unit = output_dim.unit.value

        # Check for problematic unit domain changes
        problematic_combinations = [
            # Spatial to temporal
            (["space"], ["time"]),
            (["time"], ["space"]),
            # Index to physical without clear intent
            (["index"], ["space", "time"]),
        ]

        for input_types, output_types in problematic_combinations:
            if input_type.value in input_types and output_type.value in output_types:
                message = (
                    f"Dimension {i} transforms from {input_type.value} ({input_unit}) "
                    f"to {output_type.value} ({output_unit}), which may not be intended"
                )
                if strict:
                    raise ValidationError(message)
                else:
                    warnings.warn(message, ValidationWarning, stacklevel=3)


# Additional validation functions for specific use cases
def validate_transform_chain(
    transforms: list["CoordinateTransform"], strict: bool = True
) -> None:
    """
    Validate a chain of coordinate transforms for consistency.

    Args:
        transforms: List of CoordinateTransform objects forming a chain
        strict: If True, all issues raise errors. If False, some may warn.

    Raises:
        ValidationError: If chain is invalid
    """
    if len(transforms) < 2:
        return  # Single transform or empty chain is trivially valid

    # Validate each individual transform
    for transform in transforms:
        validate_coordinate_transform(transform, strict=strict)

    # Validate chain continuity
    for i in range(len(transforms) - 1):
        current_output = transforms[i].output
        next_input = transforms[i + 1].input

        # Check if output matches next input (by dimensions and units)
        if len(current_output.dimensions) != len(next_input.dimensions):
            raise ValidationError(
                f"Transform chain break at step {i}→{i + 1}: "
                f"output has {len(current_output.dimensions)} dimensions "
                f"but next input has {len(next_input.dimensions)}"
            )

        for j, (out_dim, in_dim) in enumerate(
            zip(current_output.dimensions, next_input.dimensions, strict=False)
        ):
            if out_dim.unit.value != in_dim.unit.value:
                message = (
                    f"Transform chain break at step {i}→{i + 1}, dimension {j}: "
                    f"output unit '{out_dim.unit.value}' != input unit '{in_dim.unit.value}'"
                )
                if strict:
                    raise ValidationError(message)
                else:
                    warnings.warn(
                        f"Chain unit mismatch: {message}",
                        ValidationWarning,
                        stacklevel=2,
                    )
