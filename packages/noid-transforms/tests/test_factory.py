"""
Tests for the factory module.

Tests the factory functions for creating transform objects from various inputs.
"""

import json
from pathlib import Path
import sys

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from noid_transforms.factory import (
    coordinate_lookup,
    displacements,
    from_dict,
    from_json,
    homogeneous,
    identity,
    mapaxis,
    scale,
    translation,
)
from noid_transforms.models import (
    CoordinateLookupTable,
    DisplacementLookupTable,
    Homogeneous,
    Identity,
    MapAxis,
    Scale,
    Translation,
)


class TestCreateFunctions:
    """Test individual create functions."""

    def test_identity(self):
        """Test identity creation."""
        ident = identity()
        assert isinstance(ident, Identity)
        assert ident.to_dict() == "identity"

    def test_translation(self):
        """Test translation creation."""
        trans = translation([10, 20, 5])
        assert isinstance(trans, Translation)
        assert trans.translation == [10.0, 20.0, 5.0]

    def test_scale(self):
        """Test scale creation."""
        sc = scale([2.0, 1.5, 0.5])
        assert isinstance(sc, Scale)
        assert sc.scale == [2.0, 1.5, 0.5]

    def test_mapaxis(self):
        """Test mapaxis creation."""
        ma = mapaxis([1, 0, 2])
        assert isinstance(ma, MapAxis)
        assert ma.map_axis == [1, 0, 2]

    def test_homogeneous(self):
        """Test homogeneous creation."""
        matrix = [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
        homo = homogeneous(matrix)
        assert isinstance(homo, Homogeneous)
        assert homo.matrix_shape == (4, 4)

    def test_displacements(self):
        """Test displacements creation."""
        disp = displacements("path/to/field.zarr", "linear", "zero")
        assert isinstance(disp, DisplacementLookupTable)
        assert disp.path == "path/to/field.zarr"
        assert disp.displacements.interpolation == "linear"
        assert disp.displacements.extrapolation == "zero"

    def test_coordinate_lookup(self):
        """Test coordinate lookup creation."""
        lookup = coordinate_lookup("path/to/lut.zarr", "cubic", "reflect")
        assert isinstance(lookup, CoordinateLookupTable)
        assert lookup.path == "path/to/lut.zarr"
        assert lookup.lookup_table.interpolation == "cubic"
        assert lookup.lookup_table.extrapolation == "reflect"


class TestFromDict:
    """Test from_dict function."""

    def test_identity_from_string(self):
        """Test identity creation from string."""
        identity = from_dict("identity")
        assert isinstance(identity, Identity)
        assert identity.to_dict() == "identity"

    def test_translation_from_dict(self):
        """Test translation creation from dict."""
        data = {"translation": [10, 20, 5]}
        trans = from_dict(data)
        assert isinstance(trans, Translation)
        assert trans.translation == [10.0, 20.0, 5.0]

    def test_scale_from_dict(self):
        """Test scale creation from dict."""
        data = {"scale": [2.0, 1.5, 0.5]}
        scale = from_dict(data)
        assert isinstance(scale, Scale)
        assert scale.scale == [2.0, 1.5, 0.5]

    def test_mapaxis_from_dict(self):
        """Test mapaxis creation from dict."""
        data = {"map-axis": [1, 0, 2]}
        mapaxis = from_dict(data)
        assert isinstance(mapaxis, MapAxis)
        assert mapaxis.map_axis == [1, 0, 2]

    def test_homogeneous_from_dict(self):
        """Test homogeneous creation from dict."""
        data = {
            "homogeneous": [
                [2.0, 0, 0, 10],
                [0, 1.5, 0, 20],
                [0, 0, 0.5, 5],
                [0, 0, 0, 1],
            ]
        }
        homogeneous = from_dict(data)
        assert isinstance(homogeneous, Homogeneous)
        assert homogeneous.matrix_shape == (4, 4)

    def test_displacements_from_dict_path_only(self):
        """Test displacements creation from dict with path only."""
        data = {"displacements": "path/to/field.zarr"}
        disp = from_dict(data)
        assert isinstance(disp, DisplacementLookupTable)
        assert disp.path == "path/to/field.zarr"

    def test_displacements_from_dict_full(self):
        """Test displacements creation from dict with full config."""
        data = {
            "displacements": {
                "path": "path/to/field.zarr",
                "interpolation": "linear",
                "extrapolation": "zero",
            }
        }
        disp = from_dict(data)
        assert isinstance(disp, DisplacementLookupTable)
        assert disp.path == "path/to/field.zarr"
        assert disp.displacements.interpolation == "linear"
        assert disp.displacements.extrapolation == "zero"

    def test_coordinate_lookup_from_dict(self):
        """Test coordinate lookup creation from dict."""
        data = {
            "lookup-table": {
                "path": "path/to/lut.zarr",
                "interpolation": "cubic",
                "extrapolation": "reflect",
            }
        }
        lookup = from_dict(data)
        assert isinstance(lookup, CoordinateLookupTable)
        assert lookup.path == "path/to/lut.zarr"
        assert lookup.lookup_table.interpolation == "cubic"
        assert lookup.lookup_table.extrapolation == "reflect"

    def test_invalid_dict_type(self):
        """Test error on invalid dict type."""
        with pytest.raises(ValueError, match="must be a dictionary"):
            from_dict(123)

    def test_multiple_keys_error(self):
        """Test error on multiple keys."""
        with pytest.raises(ValueError, match="exactly one key"):
            from_dict({"translation": [1, 2], "scale": [3, 4]})

    def test_unknown_transform_type(self):
        """Test error on unknown transform type."""
        with pytest.raises(ValueError, match="Unknown transform type"):
            from_dict({"unknown": [1, 2, 3]})

    def test_missing_path_error(self):
        """Test error on missing path in lookup table."""
        # Registry now wraps factory errors in FactoryValidationError
        from noid_registry import FactoryValidationError

        with pytest.raises(
            FactoryValidationError,
            match="Factory for.*failed with data",
        ):
            from_dict({"displacements": {"interpolation": "linear"}})


class TestFromJson:
    """Test from_json function."""

    def test_identity_from_json(self):
        """Test identity creation from JSON."""
        json_str = '"identity"'
        identity = from_json(json_str)
        assert isinstance(identity, Identity)

    def test_translation_from_json(self):
        """Test translation creation from JSON."""
        json_str = '{"translation": [10, 20, 5]}'
        trans = from_json(json_str)
        assert isinstance(trans, Translation)
        assert trans.translation == [10.0, 20.0, 5.0]

    def test_invalid_json_error(self):
        """Test error on invalid JSON."""
        with pytest.raises(ValueError, match="Expecting"):
            from_json('{"translation": [10, 20, 5')  # Missing closing bracket


class TestIntegration:
    """Integration tests for factory functions."""

    def test_round_trip_serialization(self):
        """Test that factory functions can recreate transforms from their dict representation."""
        transforms = [
            identity(),
            translation([10, 20, 5]),
            scale([2.0, 1.5, 0.5]),
            mapaxis([1, 0, 2]),
            homogeneous(
                [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
            ),
        ]

        for original in transforms:
            dict_repr = original.to_dict()
            recreated = from_dict(dict_repr)
            assert type(recreated) == type(original)
            assert recreated.to_dict() == dict_repr

    def test_json_round_trip(self):
        """Test JSON serialization round trip."""
        original = translation([10, 20, 5])
        json_str = json.dumps(original.to_dict())
        recreated = from_json(json_str)
        assert isinstance(recreated, Translation)
        assert recreated.translation == original.translation
