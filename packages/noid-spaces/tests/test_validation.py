"""Tests for noid_spaces.validation module."""

import pytest
from unittest.mock import Mock, patch

from noid_spaces.validation import (
    UdunitsValidationError,
    get_udunits_info,
    is_valid_dimension_unit,
    is_valid_udunits_string,
    validate_dimension_unit,
    validate_udunits_string,
)


class TestUdunitsValidation:
    """Test cases for UDUNITS-2 validation functions."""

    @patch('noid_spaces.validation.py_udunits2')
    def test_validate_udunits_string_valid(self, mock_py_udunits2):
        """Test validation of valid UDUNITS-2 strings."""
        # Mock successful unit creation
        mock_unit = Mock()
        mock_py_udunits2.Unit.return_value = mock_unit

        # Should not raise an exception
        result = validate_udunits_string("meter")
        assert result is True

        mock_py_udunits2.Unit.assert_called_once_with("meter")

    @patch('noid_spaces.validation.py_udunits2')
    def test_validate_udunits_string_invalid(self, mock_py_udunits2):
        """Test validation of invalid UDUNITS-2 strings."""
        # Mock unit creation failure
        mock_py_udunits2.Unit.side_effect = Exception("Invalid unit")

        with pytest.raises(UdunitsValidationError, match="Invalid UDUNITS-2 unit string: 'invalid_unit'"):
            validate_udunits_string("invalid_unit")

    @patch('noid_spaces.validation.py_udunits2', None)
    def test_validate_udunits_string_no_library(self):
        """Test validation when py_udunits2 is not available."""
        with pytest.raises(ImportError, match="udunits2 is required for UDUNITS-2 validation"):
            validate_udunits_string("meter")

    @patch('noid_spaces.validation.py_udunits2')
    def test_is_valid_udunits_string_valid(self, mock_py_udunits2):
        """Test non-throwing validation of valid UDUNITS-2 strings."""
        mock_unit = Mock()
        mock_py_udunits2.Unit.return_value = mock_unit

        result = is_valid_udunits_string("meter")
        assert result is True

    @patch('noid_spaces.validation.py_udunits2')
    def test_is_valid_udunits_string_invalid(self, mock_py_udunits2):
        """Test non-throwing validation of invalid UDUNITS-2 strings."""
        mock_py_udunits2.Unit.side_effect = Exception("Invalid unit")

        result = is_valid_udunits_string("invalid_unit")
        assert result is False

    @patch('noid_spaces.validation.py_udunits2', None)
    def test_is_valid_udunits_string_no_library(self):
        """Test non-throwing validation when py_udunits2 is not available."""
        result = is_valid_udunits_string("meter")
        assert result is False


class TestDimensionUnitValidation:
    """Test cases for dimension-specific unit validation."""

    def test_validate_dimension_unit_special_units(self):
        """Test validation of special units for all dimension types."""
        dimension_types = ["space", "time", "other", "index"]
        special_units = ["index", "arbitrary"]

        for unit in special_units:
            for dim_type in dimension_types:
                # Special units should be valid for all dimension types
                result = validate_dimension_unit(unit, dim_type)
                assert result is True

    def test_validate_dimension_unit_index_constraint(self):
        """Test that index dimensions must use 'index' unit."""
        # Valid index dimension
        result = validate_dimension_unit("index", "index")
        assert result is True

        # Invalid index dimension
        with pytest.raises(UdunitsValidationError, match="Index dimensions must use 'index' unit"):
            validate_dimension_unit("meter", "index")

    @patch('noid_spaces.validation.py_udunits2')
    def test_validate_dimension_unit_space_time_validation(self, mock_py_udunits2):
        """Test that space/time dimensions require valid UDUNITS-2 units."""
        mock_unit = Mock()
        mock_py_udunits2.Unit.return_value = mock_unit

        # Valid spatial unit
        result = validate_dimension_unit("meter", "space")
        assert result is True
        mock_py_udunits2.Unit.assert_called_with("meter")

        # Valid temporal unit
        result = validate_dimension_unit("second", "time")
        assert result is True
        mock_py_udunits2.Unit.assert_called_with("second")

    @patch('noid_spaces.validation.py_udunits2')
    def test_validate_dimension_unit_space_time_invalid(self, mock_py_udunits2):
        """Test invalid UDUNITS-2 units for space/time dimensions."""
        mock_py_udunits2.Unit.side_effect = Exception("Invalid unit")

        with pytest.raises(UdunitsValidationError):
            validate_dimension_unit("invalid_unit", "space")

        with pytest.raises(UdunitsValidationError):
            validate_dimension_unit("invalid_unit", "time")

    def test_validate_dimension_unit_other_type(self):
        """Test that 'other' dimensions allow any unit."""
        # Should not validate with UDUNITS-2, just accept any unit
        result = validate_dimension_unit("custom_unit", "other")
        assert result is True

        result = validate_dimension_unit("wavelength", "other")
        assert result is True

    def test_validate_dimension_unit_invalid_dimension_type(self):
        """Test validation with invalid dimension type."""
        with pytest.raises(ValueError, match="Invalid dimension type: 'invalid'"):
            validate_dimension_unit("meter", "invalid")

    def test_is_valid_dimension_unit_valid_cases(self):
        """Test non-throwing validation for valid cases."""
        # Special units
        assert is_valid_dimension_unit("index", "index") is True
        assert is_valid_dimension_unit("arbitrary", "other") is True

        # Other dimensions with custom units
        assert is_valid_dimension_unit("custom_unit", "other") is True

    def test_is_valid_dimension_unit_invalid_cases(self):
        """Test non-throwing validation for invalid cases."""
        # Index constraint violation
        assert is_valid_dimension_unit("meter", "index") is False

        # Invalid dimension type
        assert is_valid_dimension_unit("meter", "invalid") is False

    @patch('noid_spaces.validation.py_udunits2')
    def test_is_valid_dimension_unit_udunits_validation(self, mock_py_udunits2):
        """Test non-throwing validation with UDUNITS-2."""
        # Valid case
        mock_unit = Mock()
        mock_py_udunits2.Unit.return_value = mock_unit
        assert is_valid_dimension_unit("meter", "space") is True

        # Invalid case
        mock_py_udunits2.Unit.side_effect = Exception("Invalid unit")
        assert is_valid_dimension_unit("invalid", "space") is False


class TestUdunitsInfo:
    """Test cases for getting UDUNITS-2 information."""

    @patch('noid_spaces.validation.py_udunits2')
    def test_get_udunits_info_valid(self, mock_py_udunits2):
        """Test getting info for valid UDUNITS-2 string."""
        mock_unit = Mock()
        mock_unit.__str__ = Mock(return_value="1 meter")
        mock_py_udunits2.Unit.return_value = mock_unit

        info = get_udunits_info("meter")

        assert info is not None
        assert info["unit_string"] == "meter"
        assert info["is_valid"] is True
        assert info["definition"] == "1 meter"

    @patch('noid_spaces.validation.py_udunits2')
    def test_get_udunits_info_invalid(self, mock_py_udunits2):
        """Test getting info for invalid UDUNITS-2 string."""
        mock_py_udunits2.Unit.side_effect = Exception("Invalid unit")

        info = get_udunits_info("invalid_unit")

        assert info is not None
        assert info["unit_string"] == "invalid_unit"
        assert info["is_valid"] is False
        assert info["definition"] is None

    @patch('noid_spaces.validation.py_udunits2', None)
    def test_get_udunits_info_no_library(self):
        """Test getting info when py_udunits2 is not available."""
        info = get_udunits_info("meter")
        assert info is None


class TestRealWorldUnits:
    """Test cases with realistic unit strings."""

    @pytest.mark.parametrize("unit,dimension_type,should_be_valid", [
        # Special units
        ("index", "index", True),
        ("arbitrary", "other", True),
        ("index", "space", True),  # Special units valid for all types
        ("arbitrary", "time", True),

        # Index constraints
        ("meter", "index", False),  # Non-index unit for index dimension
        ("second", "index", False),

        # Other dimension - accepts anything
        ("custom_wavelength", "other", True),
        ("intensity", "other", True),
        ("channel_name", "other", True),

        # Common spatial units (these would be validated with UDUNITS-2 in real usage)
        # We'll test the logic without actually calling UDUNITS-2

        # Invalid dimension types
        ("meter", "invalid_type", False),
    ])
    def test_dimension_unit_validation_matrix(self, unit, dimension_type, should_be_valid):
        """Test validation matrix for various unit/dimension type combinations."""
        if should_be_valid:
            if dimension_type not in ["space", "time"] or unit in ["index", "arbitrary"]:
                # These should pass without UDUNITS-2 validation
                assert is_valid_dimension_unit(unit, dimension_type) == should_be_valid
        else:
            assert is_valid_dimension_unit(unit, dimension_type) == should_be_valid

    def test_bioimaging_units(self):
        """Test typical bioimaging unit validations."""
        # These should work without UDUNITS-2 validation
        assert is_valid_dimension_unit("index", "index") is True
        assert is_valid_dimension_unit("arbitrary", "other") is True

        # Index constraints
        assert is_valid_dimension_unit("micrometer", "index") is False

        # Other dimensions accept custom units
        assert is_valid_dimension_unit("wavelength", "other") is True
        assert is_valid_dimension_unit("fluorescence_intensity", "other") is True

    def test_geospatial_units(self):
        """Test typical geospatial unit validations."""
        # These should work without UDUNITS-2 validation for 'other' dimensions
        assert is_valid_dimension_unit("degrees_east", "other") is True
        assert is_valid_dimension_unit("degrees_north", "other") is True
        assert is_valid_dimension_unit("utm_easting", "other") is True


class TestValidationIntegration:
    """Integration tests for validation functions."""

    def test_validation_in_model_context(self):
        """Test how validation integrates with model creation."""
        from noid_spaces.models import Dimension

        # These should work based on model validation logic
        # (which calls our validation functions)

        # Valid cases
        dim1 = Dimension(id="x", unit="micrometer", type="space")
        assert dim1.unit == "micrometer"

        dim2 = Dimension(id="i", unit="index", type="index")
        assert dim2.unit == "index"

        dim3 = Dimension(id="c", unit="arbitrary", type="other")
        assert dim3.unit == "arbitrary"

        # Invalid case - index constraint
        with pytest.raises(ValueError, match="Index type dimensions must have 'index' unit"):
            Dimension(id="i", unit="meter", type="index")

    def test_comprehensive_workflow_validation(self):
        """Test validation in a complete workflow."""
        from noid_spaces.factory import coordinate_system, dimension

        # Create dimensions with various unit types
        spatial_dim = dimension(id="x", unit="micrometer", type="space")
        index_dim = dimension(id="i", unit="index", type="index")
        other_dim = dimension(id="c", unit="arbitrary", type="other")

        # Should be able to create coordinate system
        coord_sys = coordinate_system(
            id="mixed_system",
            dimensions=[spatial_dim, index_dim, other_dim]
        )

        assert coord_sys.dimension_count == 3
        assert len(coord_sys.spatial_dimensions) == 1
        assert len(coord_sys.index_dimensions) == 1
