"""
Test suite for NOID SHACL validation.

Tests both valid and invalid cases to ensure SHACL validation is working correctly.
"""

import pytest
from pathlib import Path
from noid.validation import validate_transforms, validate_coordinate_spaces, validate_with_shacl
from pyld import jsonld
import json


# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"


class TestTransformValidation:
    """Test validation of transform data using SHACL shapes."""
    
    def test_valid_translation(self):
        """Valid translation transform should pass validation."""
        test_file = TEST_DATA_DIR / "valid_translation.jsonld"
        errors = validate_transforms(test_file)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
    
    def test_invalid_translation_missing_property(self):
        """Translation transform missing required property should fail validation."""
        test_file = TEST_DATA_DIR / "invalid_translation_missing_property.jsonld"
        errors = validate_transforms(test_file)
        assert len(errors) > 0, "Expected validation errors for missing translation property"
        
        # Check that the error mentions the missing translation property
        error_text = " ".join(errors)
        assert "translation" in error_text.lower(), f"Expected error about 'translation' property, got: {errors}"
        assert ("mincount" in error_text.lower() or "min count" in error_text.lower() or 
                "less than 1" in error_text.lower()), f"Expected minCount/missing property error, got: {errors}"
    
    def test_valid_scale(self):
        """Valid scale transform should pass validation."""
        test_file = TEST_DATA_DIR / "valid_scale.jsonld"
        errors = validate_transforms(test_file)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
    
    def test_valid_homogeneous(self):
        """Valid homogeneous transform should pass validation."""
        test_file = TEST_DATA_DIR / "valid_homogeneous.jsonld"
        errors = validate_transforms(test_file)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
    
    def test_invalid_homogeneous_missing_matrix(self):
        """Homogeneous transform missing matrix should fail validation."""
        test_file = TEST_DATA_DIR / "invalid_homogeneous_missing_matrix.jsonld"
        errors = validate_transforms(test_file)
        assert len(errors) > 0, "Expected validation errors for missing matrix property"
        
        error_text = " ".join(errors)
        assert "matrix" in error_text.lower(), f"Expected error about 'matrix' property, got: {errors}"
        assert ("mincount" in error_text.lower() or "min count" in error_text.lower() or 
                "less than 1" in error_text.lower()), f"Expected minCount/missing property error, got: {errors}"
    
    def test_valid_identity(self):
        """Valid identity transform should pass validation."""
        test_file = TEST_DATA_DIR / "valid_identity.jsonld"
        errors = validate_transforms(test_file)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
    
    def test_valid_mapaxis(self):
        """Valid mapAxis transform should pass validation."""
        test_file = TEST_DATA_DIR / "valid_mapaxis.jsonld"
        errors = validate_transforms(test_file)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"


class TestCoordinateSpaceValidation:
    """Test validation of coordinate space data using SHACL shapes."""
    
    def test_valid_coordinate_space(self):
        """Valid coordinate space should pass validation."""
        test_file = TEST_DATA_DIR / "valid_coordinate_space.jsonld"
        errors = validate_coordinate_spaces(test_file)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
    
    def test_valid_time_coordinate_space(self):
        """Valid time coordinate space should pass validation."""
        test_file = TEST_DATA_DIR / "valid_time_coordinate_space.jsonld"
        errors = validate_coordinate_spaces(test_file)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
    
    def test_invalid_coordinate_space_missing_dimensions(self):
        """Coordinate space missing dimensions should fail validation."""
        test_file = TEST_DATA_DIR / "invalid_coordinate_space_missing_dimensions.jsonld"
        errors = validate_coordinate_spaces(test_file)
        assert len(errors) > 0, "Expected validation errors for missing dimensions"
        
        error_text = " ".join(errors)
        assert "dimensions" in error_text.lower(), f"Expected error about 'dimensions' property, got: {errors}"
    
    def test_invalid_dimension_missing_name(self):
        """Dimension missing name should fail validation."""
        test_file = TEST_DATA_DIR / "invalid_dimension_missing_name.jsonld"
        errors = validate_coordinate_spaces(test_file)
        assert len(errors) > 0, "Expected validation errors for missing dimension name"
        
        error_text = " ".join(errors)
        assert "name" in error_text.lower(), f"Expected error about 'name' property, got: {errors}"
    
    def test_invalid_dimension_bad_type(self):
        """Dimension with invalid type should fail validation."""
        test_file = TEST_DATA_DIR / "invalid_dimension_bad_type.jsonld"
        errors = validate_coordinate_spaces(test_file)
        assert len(errors) > 0, "Expected validation errors for invalid dimension type"
        
        error_text = " ".join(errors)
        # Should fail because "invalid_type" is not in the allowed list of ["space", "time", "other"]
        assert ("type" in error_text.lower() or "invalid_type" in error_text.lower()), f"Expected error about invalid 'type', got: {errors}"


class TestJSONLDValidation:
    """Test JSON-LD validity using pyld."""
    
    def test_transforms_vocabulary_pyld_expand(self):
        """Transforms vocabulary should be valid JSON-LD that pyld can expand."""
        vocab_file = Path(__file__).parent.parent / "schemas" / "transforms" / "vocabulary.jsonld"
        
        with open(vocab_file, 'r') as f:
            vocab_data = json.load(f)
        
        # Test that pyld can expand it without errors
        expanded = jsonld.expand(vocab_data)
        assert isinstance(expanded, list), "Expanded JSON-LD should be a list"
        assert len(expanded) > 0, "Expanded JSON-LD should contain items"


class TestValidationInfrastructure:
    """Test the validation infrastructure itself."""
    
    def test_validate_with_shacl_nonexistent_file(self):
        """Validation should handle nonexistent files gracefully."""
        nonexistent_file = TEST_DATA_DIR / "does_not_exist.jsonld"
        from noid.validation import _get_schemas_path
        schemas_path = _get_schemas_path()
        shapes_file = schemas_path / "transforms" / "shapes.ttl"
        
        errors = validate_with_shacl(nonexistent_file, shapes_file)
        assert len(errors) > 0, "Expected error for nonexistent file"
        assert "validation error" in errors[0].lower(), f"Expected validation error, got: {errors}"
    
    def test_validate_transforms_missing_shapes(self):
        """Validation should handle missing SHACL shapes file."""
        test_file = TEST_DATA_DIR / "valid_translation.jsonld"
        
        # Temporarily rename shapes file to test missing file handling
        from noid.validation import _get_schemas_path
        schemas_path = _get_schemas_path()
        shapes_file = schemas_path / "transforms" / "shapes.ttl"
        backup_file = schemas_path / "transforms" / "shapes.ttl.backup"
        
        if shapes_file.exists():
            shapes_file.rename(backup_file)
        
        try:
            errors = validate_transforms(test_file)
            assert len(errors) > 0, "Expected error for missing shapes file"
            assert "not found" in errors[0].lower(), f"Expected 'not found' error, got: {errors}"
        finally:
            # Restore the shapes file
            if backup_file.exists():
                backup_file.rename(shapes_file)


# Pytest fixtures for setup/teardown if needed