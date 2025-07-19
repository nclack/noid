"""
Tests for the models module.

Tests the enhanced transform model classes including validation,
properties, and methods.
"""

from pathlib import Path
import sys

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from noid_transforms.models import (
    CoordinateLookupTable,
    DisplacementLookupTable,
    Homogeneous,
    Identity,
    MapAxis,
    SamplerConfig,
    Scale,
    Translation,
)


class TestIdentity:
    """Test Identity transform."""

    def test_creation(self):
        """Test identity transform creation."""
        identity = Identity()
        assert isinstance(identity, Identity)

    def test_to_data(self):
        """Test identity transform serialization."""
        identity = Identity()
        assert identity.to_data() == "identity"

    def test_str_repr(self):
        """Test string representations."""
        identity = Identity()
        assert str(identity) == "identity"
        assert "Identity" in repr(identity)


class TestTranslation:
    """Test Translation transform."""

    def test_creation(self):
        """Test translation transform creation."""
        trans = Translation([10, 20, 5])
        assert trans.translation == [10.0, 20.0, 5.0]

    def test_dimensions(self):
        """Test dimensions property."""
        trans = Translation([10, 20, 5])
        assert trans.dimensions == 3

    def test_to_data(self):
        """Test translation transform serialization."""
        trans = Translation([10, 20, 5])
        expected = {"translation": [10.0, 20.0, 5.0]}
        assert trans.to_data() == expected

    def test_empty_translation_error(self):
        """Test error on empty translation vector."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Translation([])

    def test_int_conversion(self):
        """Test integer input conversion."""
        trans = Translation([10, 20, 5])
        assert all(isinstance(x, float) for x in trans.translation)


class TestScale:
    """Test Scale transform."""

    def test_creation(self):
        """Test scale transform creation."""
        scale = Scale([2.0, 1.5, 0.5])
        assert scale.scale == [2.0, 1.5, 0.5]

    def test_dimensions(self):
        """Test dimensions property."""
        scale = Scale([2.0, 1.5, 0.5])
        assert scale.dimensions == 3

    def test_to_data(self):
        """Test scale transform serialization."""
        scale = Scale([2.0, 1.5, 0.5])
        expected = {"scale": [2.0, 1.5, 0.5]}
        assert scale.to_data() == expected

    def test_empty_scale_error(self):
        """Test error on empty scale vector."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Scale([])

    def test_zero_scale_error(self):
        """Test error on zero scale factors."""
        with pytest.raises(ValueError, match="cannot be zero"):
            Scale([2.0, 0.0, 1.0])


class TestMapAxis:
    """Test MapAxis transform."""

    def test_creation(self):
        """Test mapaxis transform creation."""
        mapaxis = MapAxis([1, 0, 2])
        assert mapaxis.map_axis == [1, 0, 2]

    def test_dimensions(self):
        """Test dimension properties."""
        mapaxis = MapAxis([1, 0, 2])
        assert mapaxis.output_dimensions == 3
        assert mapaxis.input_dimensions == 3

    def test_to_data(self):
        """Test mapaxis transform serialization."""
        mapaxis = MapAxis([1, 0, 2])
        expected = {"map-axis": [1, 0, 2]}
        assert mapaxis.to_data() == expected

    def test_empty_mapaxis_error(self):
        """Test error on empty mapaxis vector."""
        with pytest.raises(ValueError, match="cannot be empty"):
            MapAxis([])

    def test_negative_index_error(self):
        """Test error on negative indices."""
        with pytest.raises(ValueError, match="non-negative"):
            MapAxis([1, -1, 2])


class TestHomogeneous:
    """Test Homogeneous transform."""

    def test_creation(self):
        """Test homogeneous transform creation."""
        matrix = [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
        homogeneous = Homogeneous(matrix)
        assert homogeneous.matrix_shape == (4, 4)

    def test_get_matrix(self):
        """Test matrix retrieval."""
        matrix = [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
        homogeneous = Homogeneous(matrix)
        retrieved = homogeneous.get_matrix()
        assert retrieved == matrix

    def test_to_data(self):
        """Test homogeneous transform serialization."""
        matrix = [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
        homogeneous = Homogeneous(matrix)
        result = homogeneous.to_data()
        assert "homogeneous" in result
        assert len(result["homogeneous"]) == 16  # 4x4 matrix flattened

    def test_empty_matrix_error(self):
        """Test error on empty matrix."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Homogeneous([])

    def test_non_rectangular_matrix_error(self):
        """Test error on non-rectangular matrix."""
        with pytest.raises(ValueError, match="rectangular"):
            Homogeneous([[1, 2], [3, 4, 5]])


class TestDisplacementLookupTable:
    """Test DisplacementLookupTable transform."""

    def test_creation(self):
        """Test displacement lookup table creation."""
        disp = DisplacementLookupTable("path/to/field.zarr")
        assert disp.path == "path/to/field.zarr"

    def test_with_config(self):
        """Test creation with sampler config."""
        config = SamplerConfig(interpolation="linear", extrapolation="zero")
        disp = DisplacementLookupTable("path/to/field.zarr", displacements=config)
        assert disp.displacements.interpolation == "linear"
        assert disp.displacements.extrapolation == "zero"

    def test_to_data(self):
        """Test displacement lookup table serialization."""
        config = SamplerConfig(interpolation="linear", extrapolation="zero")
        disp = DisplacementLookupTable("path/to/field.zarr", displacements=config)
        result = disp.to_data()
        assert "displacements" in result
        assert result["displacements"]["path"] == "path/to/field.zarr"
        assert result["displacements"]["interpolation"] == "linear"


class TestCoordinateLookupTable:
    """Test CoordinateLookupTable transform."""

    def test_creation(self):
        """Test coordinate lookup table creation."""
        lookup = CoordinateLookupTable("path/to/lut.zarr")
        assert lookup.path == "path/to/lut.zarr"

    def test_with_config(self):
        """Test creation with sampler config."""
        config = SamplerConfig(interpolation="cubic", extrapolation="reflect")
        lookup = CoordinateLookupTable("path/to/lut.zarr", lookup_table=config)
        assert lookup.lookup_table.interpolation == "cubic"
        assert lookup.lookup_table.extrapolation == "reflect"

    def test_to_data(self):
        """Test coordinate lookup table serialization."""
        config = SamplerConfig(interpolation="cubic", extrapolation="reflect")
        lookup = CoordinateLookupTable("path/to/lut.zarr", lookup_table=config)
        result = lookup.to_data()
        assert "lookup-table" in result
        assert result["lookup-table"]["path"] == "path/to/lut.zarr"
        assert result["lookup-table"]["interpolation"] == "cubic"


class TestSamplerConfig:
    """Test SamplerConfig."""

    def test_creation(self):
        """Test sampler config creation."""
        config = SamplerConfig()
        assert config.interpolation == "nearest"
        assert config.extrapolation == "nearest"

    def test_custom_values(self):
        """Test custom interpolation and extrapolation."""
        config = SamplerConfig(interpolation="linear", extrapolation="zero")
        assert config.interpolation == "linear"
        assert config.extrapolation == "zero"

    def test_to_data(self):
        """Test sampler config serialization."""
        config = SamplerConfig(interpolation="linear", extrapolation="zero")
        expected = {"interpolation": "linear", "extrapolation": "zero"}
        assert config.to_data() == expected
