"""Tests for registry dispatch and integration."""

import pytest

from noid_spaces import from_data
from noid_spaces.models import Dimension, DimensionType, Unit


class TestRegistryIntegration:
    """Test registry dispatch functionality."""

    def test_registry_integration_unit_term(self):
        """Test that from_data uses registry dispatch for unit terms."""
        # Test unit (registered factory name)
        unit_data = {"unit": "m/s"}
        unit = from_data(unit_data)
        assert isinstance(unit, Unit)
        assert unit.value == "m/s"

    def test_registry_integration_dimension(self):
        """Test that from_data uses registry dispatch for dimensions."""
        # Test dimension
        dim_data = {"dimension": {"id": "velocity", "unit": "m/s", "type": "other"}}
        dim = from_data(dim_data)
        assert isinstance(dim, Dimension)
        assert dim.id == "velocity"
        assert dim.unit.value == "m/s"
        assert dim.type == DimensionType.OTHER

    def test_unknown_type_error(self):
        """Test error handling for unknown space types."""
        with pytest.raises(ValueError, match="Unknown space type"):
            from_data({"unknown-type": {"some": "data"}})
