"""
Tests for dimension reuse prevention validation.

This module tests the validation system that prevents dimension objects from being
reused inappropriately, which could lead to data integrity issues.
"""

import warnings

import noid_transforms
import pytest

from noid_spaces.models import CoordinateSystem, CoordinateTransform, Dimension
from noid_spaces.validation import (
    ValidationError,
    ValidationWarning,
    validate_coordinate_system,
    validate_coordinate_transform,
    validate_dimension_reuse_across_coordinate_systems,
)


class TestDimensionReuseWithinCoordinateSystem:
    """Test dimension reuse validation within a single coordinate system."""

    def test_normal_coordinate_system_no_reuse(self):
        """Test that normal coordinate systems with unique dimensions pass validation."""
        # Create coordinate system with unique dimensions
        dim1 = Dimension(dimension_id="x", unit="mm", kind="space")
        dim2 = Dimension(dimension_id="y", unit="mm", kind="space")
        dim3 = Dimension(dimension_id="t", unit="ms", kind="time")

        cs = CoordinateSystem(dimensions=[dim1, dim2, dim3])

        # Should not raise any errors
        validate_coordinate_system(cs, strict=True)

    def test_dimension_object_reuse_within_coordinate_system_strict(self):
        """Test that reusing the same dimension object within a coordinate system fails in strict mode."""
        # Create dimensions with different IDs but reuse one object
        dim1 = Dimension(dimension_id="x", unit="mm", kind="space")
        dim2 = Dimension(dimension_id="y", unit="mm", kind="space")

        # Create coordinate system normally first
        cs = CoordinateSystem(dimensions=[dim1, dim2])

        # Now manually modify the dimensions list to create object reuse (this is the problematic scenario)
        cs._dimensions = [dim1, dim1, dim2]  # dim1 object reused
        cs._inner.dimensions = [dim._inner for dim in cs._dimensions]

        # This should fail during validation
        with pytest.raises(
            ValidationError,
            match="Dimension objects are reused within coordinate system",
        ):
            validate_coordinate_system(cs, strict=True)

    def test_dimension_object_reuse_within_coordinate_system_non_strict(self):
        """Test that reusing dimension objects within coordinate system warns in non-strict mode."""
        # This test checks the validation function directly to avoid duplicate ID issues
        from noid_spaces.validation import (
            _validate_dimension_reuse_within_coordinate_system,
        )

        # Create dimensions
        dim1 = Dimension(dimension_id="x", unit="mm", kind="space")
        dim2 = Dimension(dimension_id="y", unit="mm", kind="space")

        # Create coordinate system normally first
        cs = CoordinateSystem(dimensions=[dim1, dim2])

        # Manually modify to create object reuse (different IDs to avoid duplicate ID validation)
        # We'll create a new dimension object but modify the internal structure to simulate reuse
        cs._dimensions = [dim1, dim2, dim1]  # Reuse dim1 at the end

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Test the reuse validation function directly
            _validate_dimension_reuse_within_coordinate_system(cs, strict=False)

            # Should have generated a warning
            assert len(w) > 0
            assert any(issubclass(warning.category, ValidationWarning) for warning in w)
            assert any(
                "reused within coordinate system" in str(warning.message)
                for warning in w
            )


class TestDimensionReuseAcrossCoordinateSystems:
    """Test dimension reuse validation across multiple coordinate systems."""

    def test_normal_coordinate_systems_no_reuse(self):
        """Test that coordinate systems with unique dimensions pass validation."""
        # Create separate dimensions for each coordinate system
        input_dims = [
            Dimension(dimension_id="x", unit="pixel", kind="space"),
            Dimension(dimension_id="y", unit="pixel", kind="space"),
        ]
        output_dims = [
            Dimension(dimension_id="x", unit="mm", kind="space"),
            Dimension(dimension_id="y", unit="mm", kind="space"),
        ]

        input_cs = CoordinateSystem(dimensions=input_dims)
        output_cs = CoordinateSystem(dimensions=output_dims)

        # Should not raise any errors
        validate_dimension_reuse_across_coordinate_systems(
            [input_cs, output_cs], strict=True
        )

    def test_dimension_reuse_across_coordinate_systems_strict(self):
        """Test that reusing dimension objects across coordinate systems fails in strict mode."""
        # Create dimensions
        shared_dim = Dimension(dimension_id="x", unit="mm", kind="space")
        other_dim1 = Dimension(dimension_id="y", unit="mm", kind="space")
        other_dim2 = Dimension(dimension_id="z", unit="mm", kind="space")

        # Create coordinate systems that share a dimension object
        cs1 = CoordinateSystem(dimensions=[shared_dim, other_dim1])
        cs2 = CoordinateSystem(dimensions=[shared_dim, other_dim2])  # shared_dim reused

        with pytest.raises(
            ValidationError,
            match="Dimension object.*is reused across coordinate systems",
        ):
            validate_dimension_reuse_across_coordinate_systems([cs1, cs2], strict=True)

    def test_dimension_reuse_across_coordinate_systems_non_strict(self):
        """Test that reusing dimension objects across coordinate systems warns in non-strict mode."""
        # Create dimensions
        shared_dim = Dimension(dimension_id="x", unit="mm", kind="space")
        other_dim1 = Dimension(dimension_id="y", unit="mm", kind="space")
        other_dim2 = Dimension(dimension_id="z", unit="mm", kind="space")

        # Create coordinate systems that share a dimension object
        cs1 = CoordinateSystem(dimensions=[shared_dim, other_dim1])
        cs2 = CoordinateSystem(dimensions=[shared_dim, other_dim2])

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            validate_dimension_reuse_across_coordinate_systems([cs1, cs2], strict=False)

            # Should have generated a warning
            assert len(w) > 0
            assert any(issubclass(warning.category, ValidationWarning) for warning in w)
            assert any(
                "reused across coordinate systems" in str(warning.message)
                for warning in w
            )

    def test_multiple_coordinate_systems_complex_reuse(self):
        """Test dimension reuse validation with multiple coordinate systems and complex reuse patterns."""
        # Create dimensions
        dim_a = Dimension(dimension_id="a", unit="mm", kind="space")
        dim_b = Dimension(dimension_id="b", unit="mm", kind="space")
        dim_c = Dimension(dimension_id="c", unit="ms", kind="time")
        dim_d = Dimension(dimension_id="d", unit="ms", kind="time")

        # Create coordinate systems with various reuse patterns
        cs1 = CoordinateSystem(dimensions=[dim_a, dim_b])
        cs2 = CoordinateSystem(dimensions=[dim_b, dim_c])  # dim_b reused from cs1
        cs3 = CoordinateSystem(dimensions=[dim_c, dim_d])  # dim_c reused from cs2

        with pytest.raises(ValidationError, match="reused across coordinate systems"):
            validate_dimension_reuse_across_coordinate_systems(
                [cs1, cs2, cs3], strict=True
            )

    def test_single_coordinate_system_validation_passes(self):
        """Test that validation passes when checking only one coordinate system."""
        dim1 = Dimension(dimension_id="x", unit="mm", kind="space")
        dim2 = Dimension(dimension_id="y", unit="mm", kind="space")
        cs = CoordinateSystem(dimensions=[dim1, dim2])

        # Should not raise any errors (nothing to compare against)
        validate_dimension_reuse_across_coordinate_systems([cs], strict=True)

    def test_empty_coordinate_systems_list(self):
        """Test that validation passes with empty coordinate systems list."""
        # Should not raise any errors
        validate_dimension_reuse_across_coordinate_systems([], strict=True)


class TestCoordinateTransformDimensionReuse:
    """Test dimension reuse validation in coordinate transforms."""

    def test_coordinate_transform_no_dimension_reuse(self):
        """Test that coordinate transforms with separate dimensions pass validation."""
        # Create separate dimensions for input and output
        input_dims = [
            Dimension(dimension_id="x", unit="pixel", kind="space"),
            Dimension(dimension_id="y", unit="pixel", kind="space"),
        ]
        output_dims = [
            Dimension(dimension_id="x", unit="mm", kind="space"),
            Dimension(dimension_id="y", unit="mm", kind="space"),
        ]

        input_cs = CoordinateSystem(dimensions=input_dims)
        output_cs = CoordinateSystem(dimensions=output_dims)

        transform = CoordinateTransform(
            input=input_cs,
            output=output_cs,
            transform=noid_transforms.translation([0.1, 0.1]),
        )

        # Should not raise any errors
        validate_coordinate_transform(
            transform, strict=False
        )  # Use non-strict to avoid unit compatibility warnings

    def test_coordinate_transform_with_dimension_reuse_fails(self):
        """Test that coordinate transforms with shared dimension objects fail validation."""
        # Create dimensions with one shared between input and output
        shared_dim = Dimension(dimension_id="x", unit="mm", kind="space")
        input_dim = Dimension(dimension_id="y", unit="pixel", kind="space")
        output_dim = Dimension(dimension_id="z", unit="mm", kind="space")

        # Create coordinate systems that share a dimension
        input_cs = CoordinateSystem(dimensions=[shared_dim, input_dim])
        output_cs = CoordinateSystem(
            dimensions=[shared_dim, output_dim]
        )  # shared_dim reused

        # This should fail during transform creation due to dimension reuse
        with pytest.raises(ValidationError, match="reused across coordinate systems"):
            CoordinateTransform(
                input=input_cs,
                output=output_cs,
                transform=noid_transforms.translation([0.1, 0.1]),
            )

    def test_coordinate_transform_created_with_shared_dimensions_constructor_validation(
        self,
    ):
        """Test that coordinate transform constructor catches dimension reuse during construction."""
        # Create dimensions - single dimension systems to avoid dimension mismatch issues
        shared_dim = Dimension(dimension_id="x", unit="mm", kind="space")

        # Create coordinate systems with shared dimension (both single dimension)
        input_cs = CoordinateSystem(dimensions=[shared_dim])
        output_cs = CoordinateSystem(dimensions=[shared_dim])  # Same object reused

        # Constructor should catch this during its validation
        with pytest.raises(ValidationError, match="reused across coordinate systems"):
            CoordinateTransform(
                input=input_cs,
                output=output_cs,
                transform=noid_transforms.translation([0.1]),
            )


class TestDimensionReuseEdgeCases:
    """Test edge cases for dimension reuse validation."""

    def test_dimensions_with_same_id_but_different_objects_allowed(self):
        """Test that dimensions with same ID but different objects are allowed."""
        # Create dimensions with same ID but different objects (this is actually valid for different coordinate systems)
        dim1 = Dimension(dimension_id="x", unit="pixel", kind="space")
        dim2 = Dimension(
            dimension_id="x", unit="mm", kind="space"
        )  # Same ID, different object

        # Should be different objects
        assert dim1 is not dim2
        assert id(dim1) != id(dim2)

        # Create coordinate systems
        input_cs = CoordinateSystem(dimensions=[dim1])
        output_cs = CoordinateSystem(dimensions=[dim2])

        # Should not raise any errors - different objects are fine
        validate_dimension_reuse_across_coordinate_systems(
            [input_cs, output_cs], strict=True
        )

    def test_coordinate_system_with_no_dimensions(self):
        """Test validation with coordinate systems that have no dimensions."""
        empty_cs = CoordinateSystem(dimensions=[])
        dim1 = Dimension(dimension_id="x", unit="mm", kind="space")
        normal_cs = CoordinateSystem(dimensions=[dim1])

        # Should not raise any errors
        validate_dimension_reuse_across_coordinate_systems(
            [empty_cs, normal_cs], strict=True
        )

    def test_coordinate_system_auto_generated_dimensions_no_reuse(self):
        """Test that auto-generated dimensions don't cause reuse issues."""
        cs1 = CoordinateSystem(id="system1", dimensions=[])
        dim1 = cs1.add_dimension(unit="mm", kind="space")  # Auto-generated

        cs2 = CoordinateSystem(id="system2", dimensions=[])
        dim2 = cs2.add_dimension(unit="mm", kind="space")  # Auto-generated

        # Should be different objects even though they have similar properties
        assert dim1 is not dim2
        assert id(dim1) != id(dim2)

        # Should not raise any errors
        validate_dimension_reuse_across_coordinate_systems([cs1, cs2], strict=True)


class TestDimensionReuseIntegration:
    """Test dimension reuse validation in realistic scenarios."""

    def test_realistic_processing_pipeline_no_reuse(self):
        """Test a realistic processing pipeline with proper dimension isolation."""
        # Create raw data coordinate system
        raw_cs = CoordinateSystem(id="raw_data", dimensions=[])
        raw_x = raw_cs.add_dimension(unit="pixel", kind="space", label="x")
        raw_y = raw_cs.add_dimension(unit="pixel", kind="space", label="y")

        # Create processed data coordinate system (separate dimensions)
        processed_cs = CoordinateSystem(id="processed_data", dimensions=[])
        proc_x = processed_cs.add_dimension(unit="μm", kind="space", label="x")
        proc_y = processed_cs.add_dimension(unit="μm", kind="space", label="y")

        # Create coordinate transform
        transform = CoordinateTransform(
            input=raw_cs,
            output=processed_cs,
            transform=noid_transforms.scale([0.1, 0.1]),  # 0.1 μm per pixel
        )

        # Should pass all validations
        validate_coordinate_transform(transform, strict=False)

        # Verify dimensions are indeed separate objects
        assert raw_x is not proc_x
        assert raw_y is not proc_y

    def test_incorrect_dimension_sharing_in_pipeline(self):
        """Test detection of incorrect dimension sharing in processing pipeline."""
        # Create dimensions
        shared_x = Dimension(dimension_id="x", unit="mm", kind="space")
        raw_y = Dimension(dimension_id="y", unit="pixel", kind="space")
        proc_y = Dimension(dimension_id="y", unit="μm", kind="space")

        # Incorrectly share the x dimension between coordinate systems
        raw_cs = CoordinateSystem(id="raw", dimensions=[shared_x, raw_y])
        processed_cs = CoordinateSystem(
            id="processed", dimensions=[shared_x, proc_y]
        )  # Reusing shared_x

        # This should be caught during transform creation
        with pytest.raises(ValidationError, match="reused across coordinate systems"):
            CoordinateTransform(
                input=raw_cs,
                output=processed_cs,
                transform=noid_transforms.translation([0.0, 0.0]),  # 2D transform
            )
