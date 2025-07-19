"""
Validation utilities for transform objects.

This module provides validation functions that leverage LinkML's validation capabilities
and add additional business logic validation for transform objects.
"""

from .models import Transform


class ValidationError(Exception):
    """Exception raised when transform validation fails."""

    pass


def validate(transform: Transform, strict: bool = True) -> bool:
    """
    Validate a transform object.

    Args:
        transform: Transform object to validate
        strict: If True, raise exception on validation failure

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails and strict=True

    Example:
        >>> from .factory import translation
        >>> trans = translation([10, 20, 5])
        >>> validate(trans)
        True
    """
    try:
        _validate_transform_structure(transform)
        _validate_transform_semantics(transform)
        return True
    except ValidationError:
        if strict:
            raise
        return False


def _validate_transform_structure(transform: Transform) -> None:
    """Validate the structural properties of a transform."""
    from .models import (
        CoordinateLookupTable,
        DisplacementLookupTable,
        Homogeneous,
        Identity,
        MapAxis,
        Scale,
        Translation,
    )

    # Check that transform is a known type
    if not isinstance(
        transform,
        Identity
        | Translation
        | Scale
        | MapAxis
        | Homogeneous
        | DisplacementLookupTable
        | CoordinateLookupTable,
    ):
        raise ValidationError(f"Unknown transform type: {type(transform)}")

    # Type-specific structural validation
    if isinstance(transform, Translation):
        if not hasattr(transform, "translation") or not transform.translation:
            raise ValidationError(
                "Translation transform must have non-empty translation vector"
            )
        if not all(isinstance(x, int | float) for x in transform.translation):
            raise ValidationError("Translation vector must contain only numbers")

    elif isinstance(transform, Scale):
        if not hasattr(transform, "scale") or not transform.scale:
            raise ValidationError("Scale transform must have non-empty scale vector")
        if not all(isinstance(x, int | float) for x in transform.scale):
            raise ValidationError("Scale vector must contain only numbers")
        if any(x == 0 for x in transform.scale):
            raise ValidationError("Scale factors cannot be zero")

    elif isinstance(transform, MapAxis):
        if not hasattr(transform, "map_axis") or not transform.map_axis:
            raise ValidationError(
                "MapAxis transform must have non-empty map_axis vector"
            )
        if not all(isinstance(x, int) for x in transform.map_axis):
            raise ValidationError("MapAxis vector must contain only integers")
        if any(x < 0 for x in transform.map_axis):
            raise ValidationError("MapAxis indices must be non-negative")

    elif isinstance(transform, Homogeneous):
        if not hasattr(transform, "homogeneous") or not transform.homogeneous:
            raise ValidationError("Homogeneous transform must have non-empty matrix")
        if not all(isinstance(x, int | float) for x in transform.homogeneous):
            raise ValidationError("Homogeneous matrix must contain only numbers")

        # Check that matrix dimensions are consistent
        if hasattr(transform, "_rows") and hasattr(transform, "_cols"):
            expected_size = transform._rows * transform._cols
            if len(transform.homogeneous) != expected_size:
                raise ValidationError(
                    f"Homogeneous matrix size mismatch: expected {expected_size}, got {len(transform.homogeneous)}"
                )

    elif isinstance(transform, DisplacementLookupTable | CoordinateLookupTable):
        if not hasattr(transform, "path") or not transform.path:
            raise ValidationError("Lookup table transform must have non-empty path")
        if not isinstance(transform.path, str):
            raise ValidationError("Lookup table path must be a string")


def _validate_transform_semantics(transform: Transform) -> None:
    """Validate the semantic properties of a transform."""
    from .models import (
        CoordinateLookupTable,
        DisplacementLookupTable,
        Homogeneous,
        MapAxis,
    )

    # Semantic validation for specific transform types
    if isinstance(transform, MapAxis):
        # Check for duplicate indices (not allowed in permutation)
        if len(set(transform.map_axis)) != len(transform.map_axis):
            raise ValidationError("MapAxis vector cannot contain duplicate indices")

        # Check for reasonable index range (warn if indices are very large)
        max_index = max(transform.map_axis)
        if max_index > 10:  # Arbitrary threshold
            import warnings

            warnings.warn(
                f"MapAxis contains very large index {max_index}, which may indicate an error",
                stacklevel=2,
            )

    elif isinstance(transform, Homogeneous):
        # Check for square matrix (common case)
        if hasattr(transform, "_rows") and hasattr(transform, "_cols"):
            if transform._rows != transform._cols:
                import warnings

                warnings.warn(
                    f"Homogeneous matrix is not square ({transform._rows}x{transform._cols})",
                    stacklevel=2,
                )

    elif isinstance(transform, DisplacementLookupTable | CoordinateLookupTable):
        # Validate sampler configuration if present
        config = getattr(transform, "displacements", None) or getattr(
            transform, "lookup_table", None
        )
        if config:
            _validate_sampler_config(config)


def _validate_sampler_config(config) -> None:
    """Validate sampler configuration."""
    from .models import SamplerConfig

    if not isinstance(config, SamplerConfig):
        raise ValidationError(
            f"Sampler configuration must be SamplerConfig, got {type(config)}"
        )

    # Validate interpolation method
    valid_interpolation = ["linear", "nearest", "cubic", "area", "bspline", "lanczos"]
    if config.interpolation not in valid_interpolation:
        raise ValidationError(f"Invalid interpolation method: {config.interpolation}")

    # Validate extrapolation method
    valid_extrapolation = ["nearest", "zero", "constant", "reflect", "wrap"]
    if config.extrapolation not in valid_extrapolation:
        raise ValidationError(f"Invalid extrapolation method: {config.extrapolation}")


def validate_sequence(transforms: list[Transform], strict: bool = True) -> bool:
    """
    Validate a sequence of transforms.

    Args:
        transforms: List of transform objects to validate
        strict: If True, raise exception on validation failure

    Returns:
        True if all transforms validate successfully

    Raises:
        ValidationError: If any transform fails validation and strict=True

    Example:
        >>> from .factory import identity, translation
        >>> transforms = [identity(), translation([10, 20, 5])]
        >>> validate_sequence(transforms)
        True
    """
    if not isinstance(transforms, list):
        if strict:
            raise ValidationError("Transform sequence must be a list")
        return False

    for i, transform in enumerate(transforms):
        try:
            validate(transform, strict=True)
        except ValidationError as e:
            if strict:
                raise ValidationError(f"Transform {i} failed validation: {e}") from e
            return False

    return True


def validate_dimension_consistency(
    transforms: list[Transform], strict: bool = True
) -> bool:
    """
    Validate that transforms in a sequence have consistent dimensions.

    Args:
        transforms: List of transform objects to validate
        strict: If True, raise exception on validation failure

    Returns:
        True if dimension consistency is maintained

    Raises:
        ValidationError: If dimension consistency fails and strict=True

    Note:
        This is a best-effort check as some transforms don't specify dimensions explicitly.

    Example:
        >>> from .factory import translation, scale
        >>> transforms = [translation([10, 20, 5]), scale([2, 1, 3])]
        >>> validate_dimension_consistency(transforms)
        True
    """
    from .models import MapAxis, Scale, Translation

    if not transforms:
        return True

    # Extract dimension information where available
    dimensions = []
    for i, transform in enumerate(transforms):
        if isinstance(transform, Translation | Scale):
            dim = len(
                transform.translation
                if isinstance(transform, Translation)
                else transform.scale
            )
            dimensions.append((i, dim))
        elif isinstance(transform, MapAxis):
            input_dim = max(transform.map_axis) + 1 if transform.map_axis else 0
            output_dim = len(transform.map_axis)
            dimensions.append((i, f"{input_dim}→{output_dim}"))

    # Check for consistency among transforms that specify dimensions
    if len(dimensions) > 1:
        # For Translation and Scale, check that dimensions match
        numeric_dims = [(i, dim) for i, dim in dimensions if isinstance(dim, int)]
        if len(numeric_dims) > 1:
            first_dim = numeric_dims[0][1]
            for _, dim in numeric_dims[1:]:
                if dim != first_dim:
                    msg = f"Dimension mismatch between transforms: {first_dim} vs {dim}"
                    if strict:
                        raise ValidationError(msg)
                    return False

    return True


def check_transform_compatibility(transform1: Transform, transform2: Transform) -> bool:
    """
    Check if two transforms are compatible for composition.

    Args:
        transform1: First transform
        transform2: Second transform

    Returns:
        True if transforms are compatible

    Note:
        This is a basic compatibility check. Full compatibility requires
        knowledge of the coordinate spaces involved.

    Example:
        >>> from .factory import translation, scale
        >>> trans = translation([10, 20, 5])
        >>> sc = scale([2, 1, 3])
        >>> check_transform_compatibility(trans, sc)
        True
    """
    from .models import Identity, MapAxis, Scale, Translation

    # Identity transforms are always compatible
    if isinstance(transform1, Identity) or isinstance(transform2, Identity):
        return True

    # Simple dimension check for basic transforms
    if isinstance(transform1, Translation | Scale) and isinstance(
        transform2, Translation | Scale
    ):
        dim1 = len(
            transform1.translation
            if isinstance(transform1, Translation)
            else transform1.scale
        )
        dim2 = len(
            transform2.translation
            if isinstance(transform2, Translation)
            else transform2.scale
        )
        return dim1 == dim2

    # MapAxis compatibility requires output dimensions of first to match input capabilities of second
    if isinstance(transform1, MapAxis) and isinstance(transform2, Translation | Scale):
        output_dim1 = len(transform1.map_axis)
        dim2 = len(
            transform2.translation
            if isinstance(transform2, Translation)
            else transform2.scale
        )
        return output_dim1 == dim2

    # For other cases, assume compatibility (conservative approach)
    return True
