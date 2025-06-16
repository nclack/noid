"""Comprehensive tests for transform parameter validation, serialization, and deserialization."""

import pytest
from pydantic import ValidationError

from noid.transforms import Transform


class TestTransformValidation:
    """Test validation of each transform type."""
    
    def test_identity_valid(self):
        """Test valid identity transform."""
        data = {"identity": []}
        transform = Transform(data)
        assert transform.root.identity == []
    
    def test_identity_invalid_non_empty(self):
        """Test identity transform with non-empty array fails."""
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
        # Scale items are wrapped in ScaleItem objects
        assert transform.root.scale[0].root == 2.0
        assert transform.root.scale[1].root == 1.5
        assert transform.root.scale[2].root == 0.5
    
    def test_scale_invalid_negative(self):
        """Test scale transform with negative values fails."""
        data = {"scale": [2.0, -1.5, 0.5]}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_scale_invalid_zero(self):
        """Test scale transform with zero values fails."""
        data = {"scale": [2.0, 0.0, 0.5]}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_mapaxis_valid(self):
        """Test valid mapAxis transform."""
        data = {"mapAxis": {"x": "y", "y": "x", "z": "z"}}
        transform = Transform(data)
        assert transform.root.mapAxis == {"x": "y", "y": "x", "z": "z"}
    
    def test_mapaxis_invalid_bad_key(self):
        """Test mapAxis transform with invalid key fails."""
        data = {"mapAxis": {"123invalid": "y"}}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_mapaxis_invalid_bad_value(self):
        """Test mapAxis transform with invalid value fails."""
        data = {"mapAxis": {"x": "123invalid"}}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_rotation_valid(self):
        """Test valid rotation transform."""
        data = {"rotation": [[0, -1, 0], [1, 0, 0], [0, 0, 1]]}
        transform = Transform(data)
        assert transform.root.rotation == [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    
    def test_rotation_invalid_too_small(self):
        """Test rotation transform with too few rows fails."""
        data = {"rotation": [[1]]}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_homogeneous_valid(self):
        """Test valid homogeneous transform."""
        data = {"homogeneous": [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]}
        transform = Transform(data)
        assert len(transform.root.homogeneous) == 4
        assert len(transform.root.homogeneous[0]) == 4
    
    def test_sequence_valid(self):
        """Test valid sequence transform."""
        data = {"sequence": [{"scale": [2.0, 2.0]}, {"translation": [10, 20]}]}
        transform = Transform(data)
        assert len(transform.root.sequence) == 2
    
    def test_sequence_invalid_empty(self):
        """Test sequence transform with empty array fails."""
        data = {"sequence": []}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_displacements_valid_string(self):
        """Test valid displacements transform with string path."""
        data = {"displacements": "path/to/displacement_field.zarr"}
        transform = Transform(data)
        assert transform.root.displacements == "path/to/displacement_field.zarr"
    
    def test_displacements_valid_object(self):
        """Test valid displacements transform with object config."""
        data = {"displacements": {"path": "path/to/field.zarr", "interpolation": "linear"}}
        transform = Transform(data)
        assert transform.root.displacements.path == "path/to/field.zarr"
        assert transform.root.displacements.interpolation.value == "linear"
    
    def test_displacements_invalid_missing_path(self):
        """Test displacements transform without required path fails."""
        data = {"displacements": {"interpolation": "linear"}}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_coordinates_valid(self):
        """Test valid coordinates transform."""
        data = {"coordinates": {"lookup_table": "path/to/lut.zarr", "interpolation": "linear"}}
        transform = Transform(data)
        assert transform.root.coordinates.lookup_table == "path/to/lut.zarr"
        assert transform.root.coordinates.interpolation.value == "linear"
    
    def test_coordinates_invalid_missing_lookup_table(self):
        """Test coordinates transform without required lookup_table fails."""
        data = {"coordinates": {"interpolation": "linear"}}
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
        data = {"identity": []}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert serialized == {"identity": []}
    
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
        data = {"mapAxis": {"x": "y", "y": "x", "z": "z"}}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert serialized == {"mapAxis": {"x": "y", "y": "x", "z": "z"}}
    
    def test_rotation_serialization(self):
        """Test rotation transform serialization."""
        data = {"rotation": [[0, -1, 0], [1, 0, 0], [0, 0, 1]]}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert serialized == {"rotation": [[0, -1, 0], [1, 0, 0], [0, 0, 1]]}
    
    def test_sequence_serialization(self):
        """Test sequence transform serialization."""
        data = {"sequence": [{"scale": [2.0, 2.0]}, {"translation": [10, 20]}]}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert "sequence" in serialized
        assert len(serialized["sequence"]) == 2
    
    def test_displacements_object_serialization(self):
        """Test displacements transform object serialization."""
        data = {"displacements": {"path": "path/to/field.zarr", "interpolation": "linear"}}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert "displacements" in serialized
        assert serialized["displacements"]["path"] == "path/to/field.zarr"
        assert serialized["displacements"]["interpolation"].value == "linear"
        assert serialized["displacements"]["extrapolation"] is None
    
    def test_coordinates_serialization(self):
        """Test coordinates transform serialization."""
        data = {"coordinates": {"lookup_table": "path/to/lut.zarr", "interpolation": "linear"}}
        transform = Transform(data)
        serialized = transform.model_dump()
        assert "coordinates" in serialized
        assert serialized["coordinates"]["lookup_table"] == "path/to/lut.zarr"
        assert serialized["coordinates"]["interpolation"].value == "linear"
        assert serialized["coordinates"]["extrapolation"] is None


class TestTransformDeserialization:
    """Test deserialization of transform parameters."""
    
    def test_identity_json_roundtrip(self):
        """Test identity transform JSON roundtrip."""
        original_data = {"identity": []}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.identity == []
    
    def test_translation_json_roundtrip(self):
        """Test translation transform JSON roundtrip."""
        original_data = {"translation": [10.0, 20.0, 5.0]}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.translation == [10.0, 20.0, 5.0]
    
    def test_mapaxis_json_roundtrip(self):
        """Test mapAxis transform JSON roundtrip."""
        original_data = {"mapAxis": {"x": "y", "y": "x", "z": "z"}}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.mapAxis == {"x": "y", "y": "x", "z": "z"}
    
    def test_rotation_json_roundtrip(self):
        """Test rotation transform JSON roundtrip."""
        original_data = {"rotation": [[0, -1, 0], [1, 0, 0], [0, 0, 1]]}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.rotation == [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    
    def test_displacements_string_json_roundtrip(self):
        """Test displacements transform string JSON roundtrip."""
        original_data = {"displacements": "path/to/displacement_field.zarr"}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.displacements == "path/to/displacement_field.zarr"
    
    def test_coordinates_json_roundtrip(self):
        """Test coordinates transform JSON roundtrip."""
        original_data = {"coordinates": {"lookup_table": "path/to/lut.zarr", "interpolation": "linear"}}
        transform = Transform(original_data)
        json_str = transform.model_dump_json()
        reconstructed = Transform.model_validate_json(json_str)
        assert reconstructed.root.coordinates.lookup_table == "path/to/lut.zarr"
        assert reconstructed.root.coordinates.interpolation.value == "linear"
    
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
        data = {"displacements": {"path": "test.zarr", "interpolation": "invalid_method"}}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_sequence_with_invalid_nested_transform(self):
        """Test sequence containing invalid nested transform fails."""
        data = {"sequence": [{"invalid_transform": [1, 2, 3]}]}
        with pytest.raises(ValidationError):
            Transform(data)
    
    def test_sequence_nested_validation(self):
        """Test sequence with valid nested transforms."""
        data = {"sequence": [
            {"scale": [2.0, 2.0]}, 
            {"translation": [10, 20]},
            {"rotation": [[0, -1], [1, 0]]}
        ]}
        transform = Transform(data)
        assert len(transform.root.sequence) == 3


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