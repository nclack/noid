"""
Tests for the validation module.

Tests the validation functions for transform objects.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from noid_transforms.validation import (
    validate, validate_dimension_consistency,
    check_transform_compatibility, ValidationError
)
from noid_transforms.factory import (
    identity, translation, scale, mapaxis,
    homogeneous, displacement_lookup, coordinate_lookup
)
# Aliases for backward compatibility in tests
create_identity = identity
create_translation = translation
create_scale = scale
create_mapaxis = mapaxis
create_homogeneous = homogeneous
create_displacement_lookup = displacement_lookup
create_coordinate_lookup = coordinate_lookup
from noid_transforms.models import SamplerConfig


class TestValidate:
    """Test validate function."""
    
    def test_valid_identity(self):
        """Test validation of valid identity transform."""
        ident = identity()
        assert validate(ident) is True
    
    def test_valid_translation(self):
        """Test validation of valid translation transform."""
        trans = translation([10, 20, 5])
        assert validate(trans) is True
    
    def test_valid_scale(self):
        """Test validation of valid scale transform."""
        sc = scale([2.0, 1.5, 0.5])
        assert validate(sc) is True
    
    def test_valid_mapaxis(self):
        """Test validation of valid mapaxis transform."""
        ma = mapaxis([1, 0, 2])
        assert validate(ma) is True
    
    def test_valid_homogeneous(self):
        """Test validation of valid homogeneous transform."""
        matrix = [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
        homogeneous = create_homogeneous(matrix)
        assert validate(homogeneous) is True
    
    def test_valid_displacement_lookup(self):
        """Test validation of valid displacement lookup transform."""
        disp = create_displacement_lookup("path/to/field.zarr", "linear", "zero")
        assert validate(disp) is True
    
    def test_valid_coordinate_lookup(self):
        """Test validation of valid coordinate lookup transform."""
        lookup = create_coordinate_lookup("path/to/lut.zarr", "cubic", "reflect")
        assert validate(lookup) is True
    
    def test_invalid_sampler_config(self):
        """Test validation error on invalid sampler config."""
        from noid_transforms.models import DisplacementLookupTable, SamplerConfig
        
        # Create invalid sampler config
        config = SamplerConfig(interpolation="invalid_method")
        disp = DisplacementLookupTable("path/to/field.zarr", displacements=config)
        
        with pytest.raises(ValidationError, match="Invalid interpolation method"):
            validate(disp)
    
    def test_mapaxis_duplicate_indices(self):
        """Test validation error on duplicate indices in mapaxis."""
        mapaxis = create_mapaxis([1, 0, 1])  # Duplicate index
        with pytest.raises(ValidationError, match="duplicate indices"):
            validate(mapaxis)
    
    def test_validation_non_strict(self):
        """Test non-strict validation returns False on error."""
        mapaxis = create_mapaxis([1, 0, 1])  # Duplicate index
        assert validate(mapaxis, strict=False) is False


# TestValidateSequence removed - validate_sequence was redundant
# Users can simply use: all(validate(t) for t in transforms)


class TestValidateDimensionConsistency:
    """Test validate_dimension_consistency function."""
    
    def test_consistent_dimensions(self):
        """Test validation of consistent dimensions."""
        transforms = [
            create_translation([10, 20, 5]),
            create_scale([2.0, 1.5, 0.5])
        ]
        assert validate_dimension_consistency(transforms) is True
    
    def test_inconsistent_dimensions(self):
        """Test error on inconsistent dimensions."""
        transforms = [
            create_translation([10, 20]),      # 2D
            create_scale([2.0, 1.5, 0.5])     # 3D
        ]
        with pytest.raises(ValidationError, match="Dimension mismatch"):
            validate_dimension_consistency(transforms)
    
    def test_mixed_transform_types(self):
        """Test dimension consistency with mixed transform types."""
        transforms = [
            create_identity(),
            create_translation([10, 20, 5]),
            create_mapaxis([1, 0, 2])
        ]
        # Should not raise error (identity is dimension-agnostic)
        assert validate_dimension_consistency(transforms) is True
    
    def test_empty_sequence_consistency(self):
        """Test empty sequence consistency."""
        assert validate_dimension_consistency([]) is True
    
    def test_dimension_consistency_non_strict(self):
        """Test non-strict dimension consistency."""
        transforms = [
            create_translation([10, 20]),      # 2D
            create_scale([2.0, 1.5, 0.5])     # 3D
        ]
        assert validate_dimension_consistency(transforms, strict=False) is False


class TestCheckTransformCompatibility:
    """Test check_transform_compatibility function."""
    
    def test_identity_compatibility(self):
        """Test that identity transforms are always compatible."""
        identity = create_identity()
        trans = create_translation([10, 20, 5])
        
        assert check_transform_compatibility(identity, trans) is True
        assert check_transform_compatibility(trans, identity) is True
    
    def test_same_dimension_compatibility(self):
        """Test compatibility of same-dimension transforms."""
        trans = create_translation([10, 20, 5])
        scale = create_scale([2.0, 1.5, 0.5])
        
        assert check_transform_compatibility(trans, scale) is True
        assert check_transform_compatibility(scale, trans) is True
    
    def test_different_dimension_incompatibility(self):
        """Test incompatibility of different-dimension transforms."""
        trans_2d = create_translation([10, 20])
        scale_3d = create_scale([2.0, 1.5, 0.5])
        
        assert check_transform_compatibility(trans_2d, scale_3d) is False
        assert check_transform_compatibility(scale_3d, trans_2d) is False
    
    def test_mapaxis_compatibility(self):
        """Test mapaxis compatibility."""
        mapaxis = create_mapaxis([1, 0, 2])  # 3 outputs
        trans = create_translation([10, 20, 5])  # 3D
        
        assert check_transform_compatibility(mapaxis, trans) is True
    
    def test_mapaxis_incompatibility(self):
        """Test mapaxis incompatibility."""
        mapaxis = create_mapaxis([1, 0])  # 2 outputs
        trans = create_translation([10, 20, 5])  # 3D
        
        assert check_transform_compatibility(mapaxis, trans) is False
    
    def test_unknown_transform_compatibility(self):
        """Test that unknown transform combinations are assumed compatible."""
        homogeneous = create_homogeneous([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        disp = create_displacement_lookup("path/to/field.zarr")
        
        # Should assume compatibility for unknown combinations
        assert check_transform_compatibility(homogeneous, disp) is True


class TestValidationIntegration:
    """Integration tests for validation functions."""
    
    def test_full_validation_workflow(self):
        """Test complete validation workflow."""
        transforms = [
            create_identity(),
            create_translation([10, 20, 5]),
            create_scale([2.0, 1.5, 0.5]),
            create_mapaxis([2, 1, 0])
        ]
        
        # Individual validation
        for transform in transforms:
            assert validate(transform) is True
        
        # Sequence validation using all()
        assert all(validate(t) for t in transforms) is True
        
        # Dimension consistency
        assert validate_dimension_consistency(transforms) is True
        
        # Pairwise compatibility
        for i in range(len(transforms) - 1):
            assert check_transform_compatibility(transforms[i], transforms[i + 1]) is True
    
    def test_validation_error_messages(self):
        """Test that validation error messages are informative."""
        # Create invalid transform
        mapaxis = create_mapaxis([1, 0, 1])  # Duplicate indices
        
        try:
            validate(mapaxis)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "duplicate indices" in str(e)
    
    def test_sampler_config_validation(self):
        """Test detailed sampler config validation."""
        config = SamplerConfig(interpolation="linear", extrapolation="nearest")
        disp = create_displacement_lookup("path/to/field.zarr")
        disp.displacements = config
        
        assert validate(disp) is True
        
        # Invalid interpolation
        config.interpolation = "invalid"
        with pytest.raises(ValidationError, match="Invalid interpolation method"):
            validate(disp)
        
        # Invalid extrapolation
        config.interpolation = "linear"
        config.extrapolation = "invalid"
        with pytest.raises(ValidationError, match="Invalid extrapolation method"):
            validate(disp)