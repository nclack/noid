"""Tests for noid_spaces.models module."""

import pytest

from noid_spaces.models import CoordinateSystem, CoordinateTransform, Dimension


class TestDimension:
    """Test cases for the Dimension class."""

    def test_dimension_creation_valid(self):
        """Test creating valid dimensions."""
        # Spatial dimension
        dim = Dimension(id="x", unit="micrometer", type="space")
        assert dim.id == "x"
        assert dim.unit == "micrometer"
        assert dim.type == "space"
        assert dim.is_spatial
        assert not dim.is_temporal
        assert not dim.is_index
        assert not dim.is_other

        # Temporal dimension
        time_dim = Dimension(id="t", unit="second", type="time")
        assert time_dim.is_temporal
        assert not time_dim.is_spatial

        # Index dimension
        index_dim = Dimension(id="i", unit="index", type="index")
        assert index_dim.is_index
        assert not index_dim.is_spatial

        # Other dimension
        other_dim = Dimension(id="channel", unit="arbitrary", type="other")
        assert other_dim.is_other
        assert not other_dim.is_spatial

    def test_dimension_creation_invalid_id(self):
        """Test dimension creation with invalid ID."""
        with pytest.raises(ValueError, match="Dimension ID must be a non-empty string"):
            Dimension(id="", unit="meter", type="space")

        with pytest.raises(ValueError, match="Dimension ID must be a non-empty string"):
            Dimension(id=None, unit="meter", type="space")

    def test_dimension_creation_invalid_unit(self):
        """Test dimension creation with invalid unit."""
        with pytest.raises(ValueError, match="Unit must be a non-empty string"):
            Dimension(id="x", unit="", type="space")

        with pytest.raises(ValueError, match="Unit must be a non-empty string"):
            Dimension(id="x", unit=None, type="space")

    def test_dimension_creation_invalid_type(self):
        """Test dimension creation with invalid type."""
        with pytest.raises(ValueError, match="Type must be one of: space, time, other, index"):
            Dimension(id="x", unit="meter", type="invalid")

        with pytest.raises(ValueError, match="Type must be one of: space, time, other, index"):
            Dimension(id="x", unit="meter", type="")

    def test_index_dimension_constraint(self):
        """Test that index dimensions must have 'index' unit."""
        # Valid index dimension
        Dimension(id="i", unit="index", type="index")

        # Invalid index dimension
        with pytest.raises(ValueError, match="Index type dimensions must have 'index' unit"):
            Dimension(id="i", unit="meter", type="index")

    def test_dimension_to_dict(self):
        """Test dimension serialization to dict."""
        dim = Dimension(id="x", unit="micrometer", type="space")
        expected = {
            "id": "x",
            "unit": "micrometer",
            "type": "space",
        }
        assert dim.to_dict() == expected

    def test_dimension_string_representations(self):
        """Test string representations of dimension."""
        dim = Dimension(id="x", unit="micrometer", type="space")
        assert str(dim) == "x (micrometer, space)"
        assert repr(dim) == "Dimension(id='x', unit='micrometer', type='space')"

    def test_dimension_properties(self):
        """Test dimension property methods."""
        spatial_dim = Dimension(id="x", unit="meter", type="space")
        temporal_dim = Dimension(id="t", unit="second", type="time")
        index_dim = Dimension(id="i", unit="index", type="index")
        other_dim = Dimension(id="c", unit="arbitrary", type="other")

        # Test spatial
        assert spatial_dim.is_spatial
        assert not spatial_dim.is_temporal
        assert not spatial_dim.is_index
        assert not spatial_dim.is_other

        # Test temporal
        assert temporal_dim.is_temporal
        assert not temporal_dim.is_spatial
        assert not temporal_dim.is_index
        assert not temporal_dim.is_other

        # Test index
        assert index_dim.is_index
        assert not index_dim.is_spatial
        assert not index_dim.is_temporal
        assert not index_dim.is_other

        # Test other
        assert other_dim.is_other
        assert not other_dim.is_spatial
        assert not other_dim.is_temporal
        assert not other_dim.is_index


class TestCoordinateSystem:
    """Test cases for the CoordinateSystem class."""

    def test_coordinate_system_creation_valid(self, sample_dimensions):
        """Test creating valid coordinate systems."""
        coord_sys = CoordinateSystem(
            id="physical",
            dimensions=sample_dimensions,
            description="Physical coordinate system"
        )
        assert coord_sys.id == "physical"
        assert len(coord_sys.dimensions) == 3
        assert coord_sys.description == "Physical coordinate system"
        assert coord_sys.dimension_count == 3

    def test_coordinate_system_creation_minimal(self, sample_dimension):
        """Test creating coordinate system with minimal parameters."""
        coord_sys = CoordinateSystem(id="simple", dimensions=[sample_dimension])
        assert coord_sys.id == "simple"
        assert len(coord_sys.dimensions) == 1
        assert coord_sys.description is None

    def test_coordinate_system_creation_invalid_id(self, sample_dimensions):
        """Test coordinate system creation with invalid ID."""
        with pytest.raises(ValueError, match="CoordinateSystem ID must be a non-empty string"):
            CoordinateSystem(id="", dimensions=sample_dimensions)

        with pytest.raises(ValueError, match="CoordinateSystem ID must be a non-empty string"):
            CoordinateSystem(id=None, dimensions=sample_dimensions)

    def test_coordinate_system_creation_no_dimensions(self):
        """Test coordinate system creation with no dimensions."""
        with pytest.raises(ValueError, match="CoordinateSystem must have at least one dimension"):
            CoordinateSystem(id="empty", dimensions=[])

        with pytest.raises(ValueError, match="CoordinateSystem must have at least one dimension"):
            CoordinateSystem(id="none", dimensions=None)

    def test_coordinate_system_with_string_references(self):
        """Test coordinate system with string dimension references."""
        coord_sys = CoordinateSystem(id="array", dimensions=["i", "j", "k"])
        assert coord_sys.id == "array"
        assert len(coord_sys.dimensions) == 3
        assert coord_sys.dimensions[0] == "i"

    def test_coordinate_system_mixed_dimensions(self, sample_dimension):
        """Test coordinate system with mixed dimension types."""
        coord_sys = CoordinateSystem(
            id="mixed",
            dimensions=[sample_dimension, "ref_dim"]
        )
        assert len(coord_sys.dimensions) == 2
        assert isinstance(coord_sys.dimensions[0], Dimension)
        assert coord_sys.dimensions[1] == "ref_dim"

    def test_coordinate_system_invalid_dimension_type(self):
        """Test coordinate system with invalid dimension types."""
        with pytest.raises(ValueError, match="Dimensions must be Dimension objects or strings"):
            CoordinateSystem(id="invalid", dimensions=[123])

    def test_coordinate_system_to_dict(self, sample_dimensions):
        """Test coordinate system serialization to dict."""
        coord_sys = CoordinateSystem(
            id="physical",
            dimensions=sample_dimensions,
            description="Test system"
        )
        result = coord_sys.to_dict()

        assert result["id"] == "physical"
        assert result["description"] == "Test system"
        assert len(result["dimensions"]) == 3
        assert all("id" in dim for dim in result["dimensions"])

    def test_coordinate_system_string_representations(self, sample_dimensions):
        """Test string representations of coordinate system."""
        coord_sys = CoordinateSystem(id="physical", dimensions=sample_dimensions)
        str_repr = str(coord_sys)
        assert "physical:" in str_repr
        assert "x (micrometer, space)" in str_repr

        repr_str = repr(coord_sys)
        assert "CoordinateSystem(id='physical'" in repr_str

    def test_get_dimension_by_id(self, sample_dimensions):
        """Test getting dimensions by ID."""
        coord_sys = CoordinateSystem(id="test", dimensions=sample_dimensions)

        x_dim = coord_sys.get_dimension_by_id("x")
        assert x_dim is not None
        assert x_dim.id == "x"
        assert x_dim.unit == "micrometer"

        missing_dim = coord_sys.get_dimension_by_id("missing")
        assert missing_dim is None

    def test_dimension_filtering_properties(self, sample_dimensions, sample_index_dimensions):
        """Test dimension filtering properties."""
        # Mix of different dimension types
        all_dims = sample_dimensions + sample_index_dimensions
        coord_sys = CoordinateSystem(id="mixed", dimensions=all_dims)

        spatial_dims = coord_sys.spatial_dimensions
        assert len(spatial_dims) == 2
        assert all(dim.is_spatial for dim in spatial_dims)

        temporal_dims = coord_sys.temporal_dimensions
        assert len(temporal_dims) == 1
        assert all(dim.is_temporal for dim in temporal_dims)

        index_dims = coord_sys.index_dimensions
        assert len(index_dims) == 3
        assert all(dim.is_index for dim in index_dims)


class TestCoordinateTransform:
    """Test cases for the CoordinateTransform class."""

    def test_coordinate_transform_creation_valid(self):
        """Test creating valid coordinate transforms."""
        transform = CoordinateTransform(
            id="physical_to_array",
            input="physical_space",
            output="array_space",
            transform={"scale": [0.5, 0.5, 1.0]},
            description="Scale transform"
        )
        assert transform.id == "physical_to_array"
        assert transform.input == "physical_space"
        assert transform.output == "array_space"
        assert transform.transform == {"scale": [0.5, 0.5, 1.0]}
        assert transform.description == "Scale transform"

    def test_coordinate_transform_creation_minimal(self):
        """Test creating coordinate transform with minimal parameters."""
        transform = CoordinateTransform(
            id="simple",
            input="input_space",
            output="output_space",
            transform={"identity": True}
        )
        assert transform.id == "simple"
        assert transform.description is None

    def test_coordinate_transform_invalid_id(self):
        """Test coordinate transform creation with invalid ID."""
        with pytest.raises(ValueError, match="CoordinateTransform ID must be a non-empty string"):
            CoordinateTransform(
                id="",
                input="input",
                output="output",
                transform={"identity": True}
            )

    def test_coordinate_transform_with_coordinate_system(self, sample_coordinate_system):
        """Test coordinate transform with CoordinateSystem objects."""
        transform = CoordinateTransform(
            id="cs_transform",
            input=sample_coordinate_system,
            output=sample_coordinate_system,
            transform={"identity": True}
        )
        assert transform.id == "cs_transform"
        assert transform.input == sample_coordinate_system

    def test_coordinate_transform_with_dimension_lists(self, sample_dimensions):
        """Test coordinate transform with dimension lists."""
        transform = CoordinateTransform(
            id="list_transform",
            input=sample_dimensions,
            output=["i", "j", "k"],
            transform={"scale": [1.0, 1.0, 1.0]}
        )
        assert transform.id == "list_transform"
        # Dimension lists should be converted to proper format
        assert isinstance(transform.input, dict)
        assert "dimensions" in transform.input

    def test_coordinate_transform_to_dict(self):
        """Test coordinate transform serialization to dict."""
        transform = CoordinateTransform(
            id="test_transform",
            input="input_space",
            output="output_space",
            transform={"translation": [10, 20, 5]},
            description="Test transform"
        )
        result = transform.to_dict()

        assert result["id"] == "test_transform"
        assert result["input"] == "input_space"
        assert result["output"] == "output_space"
        assert result["transform"] == {"translation": [10, 20, 5]}
        assert result["description"] == "Test transform"

    def test_coordinate_transform_string_representations(self):
        """Test string representations of coordinate transform."""
        transform = CoordinateTransform(
            id="test",
            input="input",
            output="output",
            transform={"identity": True}
        )

        str_repr = str(transform)
        assert "test: input -> output" in str_repr

        repr_str = repr(transform)
        assert "CoordinateTransform(id='test'" in repr_str
