"""Tests for validation utilities."""

import warnings

import pytest

from noid_spaces.factory import coordinate_system, coordinate_transform, dimension, unit
from noid_spaces.models import CoordinateSystem, Dimension
from noid_spaces.validation import (
    ValidationError,
    ValidationWarning,
    validate,
    validate_coordinate_system,
    validate_coordinate_transform,
    validate_dimension,
    validate_transform_chain,
)


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from Exception."""
        assert issubclass(ValidationError, Exception)

        error = ValidationError("test message")
        assert str(error) == "test message"


class TestValidationWarning:
    """Tests for ValidationWarning."""

    def test_validation_warning_inheritance(self):
        """Test that ValidationWarning inherits from UserWarning."""
        assert issubclass(ValidationWarning, UserWarning)


# Unit validation happens in constructor via Pint, so no separate validate_unit function needed


class TestValidateDimension:
    """Tests for dimension validation."""

    def test_validate_dimension_valid(self):
        """Test validating valid dimensions."""
        # Spatial dimension
        x_dim = dimension("x", "m", "space")
        validate_dimension(x_dim, strict=True)

        # Temporal dimension
        t_dim = dimension("t", "s", "time")
        validate_dimension(t_dim, strict=True)

        # Index dimension
        idx_dim = dimension("idx", "index", "index")
        validate_dimension(idx_dim, strict=True)

    def test_validate_dimension_index_type_consistency(self):
        """Test validation of index type requiring index unit."""
        # This should fail - index type requires index unit
        with pytest.raises(
            ValueError, match="Dimension type 'index' requires unit 'index'"
        ):
            _ = Dimension(dimension_id="bad", unit="m", kind="index")


class TestValidateCoordinateSystem:
    """Tests for coordinate system validation."""

    def test_validate_coordinate_system_valid(self):
        """Test validating valid coordinate systems."""
        cs = coordinate_system(
            [
                {"id": "x", "unit": "m", "type": "space"},
                {"id": "y", "unit": "m", "type": "space"},
            ]
        )
        validate_coordinate_system(cs, strict=True)

    def test_validate_coordinate_system_duplicate_ids(self):
        """Test validation catches duplicate dimension IDs."""
        with pytest.raises(ValidationError, match="Duplicate dimension IDs found"):
            # This will be caught during validation, not construction
            _ = CoordinateSystem(
                dimensions=[
                    Dimension(dimension_id="x", unit="m", kind="space"),
                    Dimension(dimension_id="x", unit="mm", kind="space"),  # Same ID
                ]
            )


class TestValidateCoordinateTransform:
    """Tests for coordinate transform validation."""

    def test_validate_coordinate_transform_valid_translation(self):
        """Test validating valid translation transform."""
        ct = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "pixel"}]},
            output={"dimensions": [{"id": "x", "unit": "mm"}]},
            transform={"translation": [0.1]},
        )
        validate_coordinate_transform(ct, strict=True)

    def test_validate_coordinate_transform_valid_scale(self):
        """Test validating valid scale transform."""
        ct = coordinate_transform(
            input={
                "dimensions": [
                    {"id": "x", "unit": "pixel"},
                    {"id": "y", "unit": "pixel"},
                ]
            },
            output={
                "dimensions": [{"id": "x", "unit": "mm"}, {"id": "y", "unit": "mm"}]
            },
            transform={"scale": [0.5, 0.5]},
        )
        validate_coordinate_transform(ct, strict=True)

    def test_validate_coordinate_transform_dimensional_mismatch(self):
        """Test validation catches dimensional mismatches."""
        # Translation vector has wrong number of elements
        with pytest.raises(
            ValidationError, match="Translation transform expects .* dimensions"
        ):
            _ = coordinate_transform(
                input={
                    "dimensions": [
                        {"id": "x", "unit": "pixel"},
                        {"id": "y", "unit": "pixel"},
                    ]
                },
                output={
                    "dimensions": [
                        {"id": "x", "unit": "mm"},
                        {"id": "y", "unit": "mm"},
                    ]
                },
                transform={"translation": [0.1]},  # Should have 2 elements, not 1
            )

    def test_validate_coordinate_transform_zero_scale(self):
        """Test validation catches zero scale factors."""
        # The scale factory in noid_transforms already validates, so this will fail during creation
        with pytest.raises(ValueError, match="Failed to create transform from data"):
            _ = coordinate_transform(
                input={"dimensions": [{"id": "x", "unit": "pixel"}]},
                output={"dimensions": [{"id": "x", "unit": "mm"}]},
                transform={"scale": [0]},  # Zero scale factor
            )

    def test_validate_coordinate_transform_unit_compatibility_strict(self):
        """Test unit compatibility validation in strict mode."""
        # Space to time conversion should fail in strict mode when explicitly validated
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            # Constructor will generate a warning in non-strict mode, which we expect
            ct = coordinate_transform(
                input={"dimensions": [{"id": "x", "unit": "m", "type": "space"}]},
                output={"dimensions": [{"id": "t", "unit": "s", "type": "time"}]},
                transform={"translation": [1.0]},
            )

        # The constructor uses non-strict mode, but explicit validation should fail in strict mode
        with pytest.raises(ValidationError, match="transforms from space.*to time"):
            validate_coordinate_transform(ct, strict=True)

    def test_validate_coordinate_transform_unit_compatibility_non_strict(self):
        """Test unit compatibility validation in non-strict mode generates warnings."""
        # Space to time conversion should warn in non-strict mode
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            ct = coordinate_transform(
                input={"dimensions": [{"id": "x", "unit": "m", "type": "space"}]},
                output={"dimensions": [{"id": "t", "unit": "s", "type": "time"}]},
                transform={"translation": [1.0]},
            )
            validate_coordinate_transform(ct, strict=False)

            # Should have generated a warning
            assert len(w) > 0
            assert any(issubclass(warning.category, ValidationWarning) for warning in w)
            assert any("transforms from space" in str(warning.message) for warning in w)


class TestValidateFunction:
    """Tests for main validate function."""

    def test_validate_unit(self):
        """Test main validate function with unit (basic serialization test only)."""
        test_unit = unit("m")
        validate(test_unit, strict=True)  # Only runs serialization test

    def test_validate_dimension(self):
        """Test main validate function with dimension."""
        dim = dimension("x", "m", "space")
        validate(dim, strict=True)

    def test_validate_coordinate_system(self):
        """Test main validate function with coordinate system."""
        cs = coordinate_system(
            [
                {"id": "x", "unit": "m", "type": "space"},
                {"id": "y", "unit": "m", "type": "space"},
            ]
        )
        validate(cs, strict=True)

    def test_validate_coordinate_transform(self):
        """Test main validate function with coordinate transform."""
        ct = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "pixel"}]},
            output={"dimensions": [{"id": "x", "unit": "mm"}]},
            transform={"translation": [0.1]},
        )
        validate(ct, strict=True)

    def test_validate_serialization_test(self):
        """Test that validate runs serialization test on objects with to_data method."""
        # Create an object that will pass basic validation
        test_unit = unit("m")

        # Should not raise any exception
        validate(test_unit, strict=True)

    def test_validate_unknown_type(self):
        """Test validate with object type that doesn't have specific validation."""

        # Plain object with to_data method should just run serialization test
        class TestObject:
            def to_data(self):
                return {"test": "data"}

        obj = TestObject()
        validate(obj, strict=True)  # Should not raise

    def test_validate_broken_object(self):
        """Test validating an object that fails serialization."""

        class BrokenObject:
            def to_data(self):
                raise RuntimeError("Broken!")

        obj = BrokenObject()
        with pytest.raises(ValidationError, match="Object failed serialization test"):
            validate(obj)


class TestValidateTransformChain:
    """Tests for transform chain validation."""

    def test_validate_transform_chain_empty(self):
        """Test validating empty transform chain."""
        validate_transform_chain([], strict=True)

    def test_validate_transform_chain_single(self):
        """Test validating single transform chain."""
        ct = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "pixel"}]},
            output={"dimensions": [{"id": "x", "unit": "mm"}]},
            transform={"translation": [0.1]},
        )
        validate_transform_chain([ct], strict=True)

    def test_validate_transform_chain_valid(self):
        """Test validating valid transform chain."""
        # First transform: pixel -> mm
        ct1 = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "pixel"}]},
            output={"dimensions": [{"id": "x", "unit": "mm"}]},
            transform={"scale": [0.1]},
        )

        # Second transform: mm -> m
        ct2 = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "mm"}]},
            output={"dimensions": [{"id": "x", "unit": "m"}]},
            transform={"scale": [0.001]},
        )

        validate_transform_chain([ct1, ct2], strict=True)

    def test_validate_transform_chain_dimensional_break(self):
        """Test validation catches dimensional breaks in chain."""
        # First transform: 1D -> 1D
        ct1 = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "pixel"}]},
            output={"dimensions": [{"id": "x", "unit": "mm"}]},
            transform={"translation": [0.1]},
        )

        # Second transform: expects 2D input but gets 1D output from first
        ct2 = coordinate_transform(
            input={
                "dimensions": [{"id": "x", "unit": "mm"}, {"id": "y", "unit": "mm"}]
            },
            output={"dimensions": [{"id": "x", "unit": "m"}, {"id": "y", "unit": "m"}]},
            transform={"scale": [0.001, 0.001]},
        )

        with pytest.raises(ValidationError, match="Transform chain break.*dimensions"):
            validate_transform_chain([ct1, ct2], strict=True)

    def test_validate_transform_chain_unit_mismatch_strict(self):
        """Test validation catches unit mismatches in chain (strict mode)."""
        # First transform: pixel -> mm
        ct1 = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "pixel"}]},
            output={"dimensions": [{"id": "x", "unit": "mm"}]},
            transform={"translation": [0.1]},
        )

        # Second transform: expects cm input but gets mm from first
        ct2 = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "cm"}]},  # Different unit!
            output={"dimensions": [{"id": "x", "unit": "m"}]},
            transform={"scale": [0.01]},
        )

        with pytest.raises(ValidationError, match="Transform chain break.*unit"):
            validate_transform_chain([ct1, ct2], strict=True)

    def test_validate_transform_chain_unit_mismatch_non_strict(self):
        """Test validation warns about unit mismatches in chain (non-strict mode)."""
        # First transform: pixel -> mm
        ct1 = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "pixel"}]},
            output={"dimensions": [{"id": "x", "unit": "mm"}]},
            transform={"translation": [0.1]},
        )

        # Second transform: expects cm input but gets mm from first
        ct2 = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "cm"}]},  # Different unit!
            output={"dimensions": [{"id": "x", "unit": "m"}]},
            transform={"scale": [0.01]},
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_transform_chain([ct1, ct2], strict=False)

            # Should generate warning about unit mismatch
            assert len(w) > 0
            assert any(issubclass(warning.category, ValidationWarning) for warning in w)
            assert any("Chain unit mismatch" in str(warning.message) for warning in w)


class TestValidationIntegration:
    """Tests for validation integration in model classes."""

    def test_coordinate_transform_constructor_validation(self):
        """Test that CoordinateTransform constructor calls validation."""
        # Valid transform should not raise
        ct = coordinate_transform(
            input={"dimensions": [{"id": "x", "unit": "pixel"}]},
            output={"dimensions": [{"id": "x", "unit": "mm"}]},
            transform={"translation": [0.1]},
        )
        assert ct is not None

    def test_coordinate_system_constructor_validation(self):
        """Test that CoordinateSystem constructor calls validation."""
        # Valid coordinate system should not raise
        cs = coordinate_system(
            [
                {"id": "x", "unit": "m", "type": "space"},
                {"id": "y", "unit": "m", "type": "space"},
            ]
        )
        assert cs is not None

    def test_dimension_constructor_validation(self):
        """Test that Dimension constructor calls validation."""
        # Valid dimension should not raise
        dim = dimension("x", "m", "space")
        assert dim is not None

    def test_unit_constructor_validation(self):
        """Test that Unit constructor validates via Pint."""
        # Valid unit should not raise
        test_unit = unit("m")
        assert test_unit is not None
