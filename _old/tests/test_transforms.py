"""Comprehensive tests for transform parameter validation, serialization, and deserialization."""

import pytest
from pydantic import ValidationError

from noid import Transform
from noid.schema import Interpolation


class TestTransformValidation:
    """Test validation of each transform type."""

    def test_identity_valid(self):
        """Test valid identity transform."""
        data = "identity"
        transform = Transform(data)
        assert transform.root == "identity"

    def test_identity_invalid_wrong_type(self):
        """Test identity transform with wrong type fails."""
        data = {"identity": [1, 2]}
        with pytest.raises(ValidationError):
            Transform(data)

    def test_translation_valid(self):
        """Test valid translation transform."""
        data = {"translation": [10.0, 20.0, 5.0]}
        transform = Transform(data)
        assert transform.root.translation == [10.0, 20.0, 5.0]

    def test_translation_invalid_empty(self):
        """Test translation transform with empty array fails."""
        data = {"translation": []}
        with pytest.raises(ValidationError):
            Transform(data)

    def test_translation_invalid_non_numeric(self):
        """Test translation transform with non-numeric values fails."""
        data = {"translation": ["not", "numbers"]}
        with pytest.raises(ValidationError):
            Transform(data)

    def test_scale_valid(self):
        """Test valid scale transform."""
        data = {"scale": [2.0, 1.5, 0.5]}
        transform = Transform(data)
        assert len(transform.root.scale) == 3
        assert transform.root.scale[0] == 2.0
        assert transform.root.scale[1] == 1.5
        assert transform.root.scale[2] == 0.5

    def test_scale_negative_allowed(self):
        """Test scale transform with negative values is allowed by schema."""
        data = {"scale": [2.0, -1.5, 0.5]}
        transform = Transform(data)
        assert transform.root.scale == [2.0, -1.5, 0.5]

    def test_scale_zero_allowed(self):
        """Test scale transform with zero values is allowed by schema."""
        data = {"scale": [2.0, 0.0, 0.5]}
        transform = Transform(data)
        assert transform.root.scale == [2.0, 0.0, 0.5]

    def test_mapaxis_valid(self):
        """Test valid mapAxis transform."""
        data = {"mapAxis": [1, 0, 2]}
        transform = Transform(data)
        # Check the values by accessing the root attribute of each MapAxi object
        assert [x.root for x in transform.root.mapAxis] == [1, 0, 2]

    def test_mapaxis_invalid_negative_index(self):
        """Test mapAxis transform with negative index fails."""
        data = {"mapAxis": [1, -1, 2]}
        with pytest.raises(ValidationError):
            Transform(data)

    def test_mapaxis_invalid_non_integer(self):
        """Test mapAxis transform with non-integer values fails."""
        data = {"mapAxis": [1.5, 0, 2]}
        with pytest.raises(ValidationError):
            Transform(data)

    def test_homogeneous_valid(self):
        """Test valid homogeneous transform."""
        data = {
            "homogeneous": [
                [2.0, 0, 0, 10],
                [0, 1.5, 0, 20],
                [0, 0, 0.5, 5],
                [0, 0, 0, 1],
            ]
        }
        transform = Transform(data)
        assert len(transform.root.homogeneous) == 4
        assert len(transform.root.homogeneous[0]) == 4

    def test_displacements_valid_string(self):
        """Test valid displacements transform with string path."""
        data = {"displacements": "path/to/displacement_field.zarr"}
        transform = Transform(data)
        assert transform.root.displacements == "path/to/displacement_field.zarr"

    def test_displacements_valid_object(self):
        """Test valid displacements transform with object config."""
        data = {
            "displacements": {"path": "path/to/field.zarr", "interpolation": "linear"}
        }
        transform = Transform(data)
        assert transform.root.displacements.path == "path/to/field.zarr"
        assert transform.root.displacements.interpolation.value == "linear"

    def test_displacements_invalid_missing_path(self):
        """Test displacements transform without required path fails."""
        data = {"displacements": {"interpolation": "linear"}}
        with pytest.raises(ValidationError):
            Transform(data)

    def test_coordinates_valid(self):
        """Test valid coordinate lookup table transform."""
        data = {
            "lookup_table": {
                "path": "path/to/lut.zarr",
                "interpolation": "linear",
            }
        }
        transform = Transform(data)
        assert transform.root.lookup_table.path == "path/to/lut.zarr"
        assert transform.root.lookup_table.interpolation.value == "linear"

    def test_coordinates_invalid_missing_path(self):
        """Test coordinate lookup table transform without required path fails."""
        data = {"lookup_table": {"interpolation": "linear"}}
        with pytest.raises(ValidationError):
            Transform(data)

    def test_invalid_unknown_transform(self):
        """Test unknown transform type fails."""
        data = {"unknown_transform": [1, 2, 3]}
        with pytest.raises(ValidationError):
            Transform(data)

    def test_invalid_multiple_transforms(self):
        """Test multiple transform types in one object fails."""
        data = {"translation": [1, 2], "scale": [1, 2]}
        with pytest.raises(ValidationError):
            Transform(data)


class TestTransformSerialization:
    """Test serialization of transform parameters."""

    def test_identity_serialization(self):
        """Test identity transform serialization."""
        data = "identity"
        transform = Transform(data)
        serialized = transform.model_dump()
        assert serialized == "identity"

    def test_translation_serialization(self):
        """Test translation transform serialization."""
        data = {"translation": [10.0, 20.0, 5.0]}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert serialized == {"translation": [10.0, 20.0, 5.0]}

    def test_scale_serialization(self):
        """Test scale transform serialization."""
        data = {"scale": [2.0, 1.5, 0.5]}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert "scale" in serialized
        assert len(serialized["scale"]) == 3
        assert serialized["scale"] == [2.0, 1.5, 0.5]

    def test_mapaxis_serialization(self):
        """Test mapAxis transform serialization."""
        data = {"mapAxis": [1, 0, 2]}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert serialized == {"mapAxis": [1, 0, 2]}

    def test_displacements_object_serialization(self):
        """Test displacements transform object serialization."""
        data = {
            "displacements": {"path": "path/to/field.zarr", "interpolation": "linear"}
        }
        transform = Transform(data)
        serialized = transform.model_dump()
        assert "displacements" in serialized
        assert serialized["displacements"]["path"] == "path/to/field.zarr"
        assert serialized["displacements"]["interpolation"] == Interpolation.linear
        assert serialized["displacements"]["extrapolation"] is None

    def test_coordinates_serialization(self):
        """Test coordinate lookup table transform serialization."""
        data = {
            "lookup_table": {
                "path": "path/to/lut.zarr",
                "interpolation": "linear",
            }
        }
        transform = Transform(data)
        serialized = transform.model_dump()
        assert "lookup_table" in serialized
        assert serialized["lookup_table"]["path"] == "path/to/lut.zarr"
        assert serialized["lookup_table"]["interpolation"] == Interpolation.linear
        assert serialized["lookup_table"]["extrapolation"] is None


class TestTransformDeserialization:
    """Test deserialization of transform parameters."""

    def test_identity_json_roundtrip(self):
        """Test identity transform JSON roundtrip."""
        original_data = "identity"
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root == "identity"

    def test_translation_json_roundtrip(self):
        """Test translation transform JSON roundtrip."""
        original_data = {"translation": [10.0, 20.0, 5.0]}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.translation == [10.0, 20.0, 5.0]

    def test_mapaxis_json_roundtrip(self):
        """Test mapAxis transform JSON roundtrip."""
        original_data = {"mapAxis": [1, 0, 2]}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        # Check the values by accessing the root attribute of each MapAxi object
        assert [x.root for x in reconstructed.root.mapAxis] == [1, 0, 2]

    def test_displacements_string_json_roundtrip(self):
        """Test displacements transform string JSON roundtrip."""
        original_data = {"displacements": "path/to/displacement_field.zarr"}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.displacements == "path/to/displacement_field.zarr"

    def test_coordinates_json_roundtrip(self):
        """Test coordinate lookup table transform JSON roundtrip."""
        original_data = {
            "lookup_table": {
                "path": "path/to/lut.zarr",
                "interpolation": "linear",
            }
        }
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.lookup_table.path == "path/to/lut.zarr"
        assert reconstructed.root.lookup_table.interpolation == Interpolation.linear

    def test_parse_from_dict(self):
        """Test parsing from dictionary."""
        data = {"translation": [10.0, 20.0, 5.0]}
        transform = Transform.model_validate(data)
        assert transform.root.translation == [10.0, 20.0, 5.0]

    def test_parse_from_json_string(self):
        """Test parsing from JSON string."""
        json_str = '{"translation": [10.0, 20.0, 5.0]}'
        transform = Transform.model_validate_json(json_str)
        assert transform.root.translation == [10.0, 20.0, 5.0]


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_object(self):
        """Test empty object fails validation."""
        with pytest.raises(ValidationError):
            Transform({})

    def test_none_value(self):
        """Test None value fails validation."""
        with pytest.raises(ValidationError):
            Transform(None)

    def test_invalid_enum_values(self):
        """Test invalid enum values fail validation."""
        data = {
            "displacements": {"path": "test.zarr", "interpolation": "invalid_method"}
        }
        with pytest.raises(ValidationError):
            Transform(data)


if __name__ == "__main__":
    # Run a few basic tests when called directly
    test = TestTransformValidation()
    test.test_translation_valid()
    test.test_scale_valid()
    test.test_mapaxis_valid()

    print("✓ Basic validation tests passed!")

    test2 = TestTransformSerialization()
    test2.test_translation_serialization()
    test2.test_scale_serialization()

    print("✓ Basic serialization tests passed!")

    test3 = TestTransformDeserialization()
    test3.test_translation_json_roundtrip()

    print("✓ Basic deserialization tests passed!")
    print("✓ All manual tests completed successfully!")
