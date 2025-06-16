"""Tests for coordinate spaces models."""

import pytest
from noid import Dimension, CoordinateSystem, CoordinateTransform, Transform
from noid.schema import DimensionType


class TestDimension:
    """Test Dimension model."""

    def test_valid_dimension(self):
        """Test creating a valid dimension."""
        dim = Dimension(id="x", unit="micrometers", type=DimensionType.space)
        assert dim.id == "x"
        assert dim.unit == "micrometers"
        assert dim.type == DimensionType.space

    def test_index_dimension_must_have_index_unit(self):
        """Test that index dimensions must have 'index' unit."""
        # Valid index dimension
        dim = Dimension(id="i", unit="index", type=DimensionType.index)
        assert dim.type == DimensionType.index
        assert dim.unit == "index"

        # Invalid index dimension should fail validation
        with pytest.raises(ValueError, match="Index dimensions must have 'index' unit"):
            Dimension(id="i", unit="micrometers", type=DimensionType.index)


class TestCoordinateSystem:
    """Test CoordinateSystem model."""

    def test_coordinate_system_with_dimension_objects(self):
        """Test coordinate system with full dimension objects."""
        dims = [
            Dimension(id="x", unit="micrometers", type=DimensionType.space),
            Dimension(id="y", unit="micrometers", type=DimensionType.space),
        ]

        cs = CoordinateSystem(
            id="image_2d", dimensions=dims, description="2D image space"
        )

        assert cs.id == "image_2d"
        assert len(cs.dimensions) == 2
        assert cs.description == "2D image space"

    def test_coordinate_system_with_dimension_references(self):
        """Test coordinate system with dimension ID references."""
        cs = CoordinateSystem(id="image_2d", dimensions=["x", "y"])

        assert cs.id == "image_2d"
        assert cs.dimensions == ["x", "y"]
        assert cs.description is None  # Optional field

    def test_coordinate_system_mixed_dimensions(self):
        """Test coordinate system with mixed dimension types."""
        cs = CoordinateSystem(
            id="mixed",
            dimensions=[
                "x",  # Reference
                Dimension(
                    id="y", unit="micrometers", type=DimensionType.space
                ),  # Object
            ],
        )

        assert len(cs.dimensions) == 2
        assert cs.dimensions[0] == "x"
        assert isinstance(cs.dimensions[1], Dimension)


class TestCoordinateTransform:
    """Test CoordinateTransform model."""

    def test_coordinate_transform_with_references(self):
        """Test coordinate transform with coordinate system references."""
        transform_data = {"identity": []}
        transform = Transform(transform_data)

        ct = CoordinateTransform(
            id="test_transform",
            input="input_space",
            output="output_space",
            transform=transform,
            description="Test transform",
        )

        assert ct.id == "test_transform"
        assert ct.input == "input_space"
        assert ct.output == "output_space"
        assert ct.description == "Test transform"

    def test_coordinate_transform_with_dimension_lists(self):
        """Test coordinate transform with dimension lists."""
        transform_data = {"translation": [10.0, 20.0]}
        transform = Transform(transform_data)

        input_dims = [
            Dimension(id="x", unit="micrometers", type=DimensionType.space),
            Dimension(id="y", unit="micrometers", type=DimensionType.space),
        ]

        ct = CoordinateTransform(
            id="translate_2d",
            input=input_dims,
            output=input_dims,  # Same output dims for translation
            transform=transform,
        )

        assert ct.id == "translate_2d"
        assert len(ct.input) == 2
        assert len(ct.output) == 2
