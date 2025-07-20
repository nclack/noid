"""Tests for validation functions."""

import pytest

from noid_spaces.models import UnitTerm
from noid_spaces.validation import ValidationError, validate


class TestValidation:
    """Tests for validation functions."""

    def test_validate_unit_term(self):
        """Test validating a unit term."""
        unit = UnitTerm("m")
        validate(unit)  # Should not raise

    def test_validate_special_unit(self):
        """Test validating a special unit."""
        unit = UnitTerm("index")
        validate(unit)  # Should not raise

    def test_validate_simple_object(self):
        """Test validating a simple object."""
        validate("simple string")  # Should not raise
        validate(42)  # Should not raise

    def test_validate_broken_object(self):
        """Test validating an object that fails serialization."""

        class BrokenObject:
            def to_data(self):
                raise RuntimeError("Broken!")

        obj = BrokenObject()
        with pytest.raises(ValidationError, match="Object failed serialization test"):
            validate(obj)
