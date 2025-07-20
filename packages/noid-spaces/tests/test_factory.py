"""Tests for factory functions."""

import json

import pint
import pytest

from noid_spaces.factory import dimension, from_data, from_json, unit_term
from noid_spaces.models import Dimension, DimensionType, UnitTerm


class TestUnitTermFactory:
    """Tests for unit_term factory function."""

    def test_create_special_unit(self):
        """Test creating special unit via factory."""
        unit = unit_term("index")
        assert isinstance(unit, UnitTerm)
        assert unit.is_non_physical
        assert unit.to_data() == "index"

    def test_create_physical_unit(self):
        """Test creating physical unit via factory."""
        unit = unit_term("m")
        assert isinstance(unit, UnitTerm)
        assert not unit.is_non_physical
        assert unit.to_dimension_type() == DimensionType.SPACE
        assert unit.to_data() == "m"

    def test_invalid_unit(self):
        """Test that invalid unit raises error."""
        with pytest.raises(pint.UndefinedUnitError):
            unit_term("invalidunit12345")

    def test_biomedical_units_factory(self):
        """Test creating biomedical units via factory."""
        # Microscopy units
        micrometer = unit_term("µm")
        assert isinstance(micrometer, UnitTerm)
        assert micrometer.to_dimension_type() == DimensionType.SPACE

        # Chemistry units
        molarity = unit_term("M")
        assert isinstance(molarity, UnitTerm)
        assert molarity.to_data() == "M"

        # Specialized biomedical units
        ppm = unit_term("ppm")
        assert isinstance(ppm, UnitTerm)
        # ppm is dimensionless - can check via Pint
        assert ppm.to_quantity().dimensionless


class TestFromData:
    """Tests for from_data function."""

    def test_from_string(self):
        """Test creating unit from string."""
        unit = from_data("m")
        assert isinstance(unit, UnitTerm)
        assert unit.to_data() == "m"

    def test_from_dict(self):
        """Test creating unit from dictionary."""
        data = {"unit": "m"}
        unit = from_data(data)
        assert isinstance(unit, UnitTerm)
        assert unit.to_data() == "m"

    def test_invalid_dict_multiple_keys(self):
        """Test that dict with multiple keys raises error."""
        data = {"unit": "m", "other": "value"}
        with pytest.raises(ValueError, match="exactly one key"):
            from_data(data)

    def test_invalid_dict_no_keys(self):
        """Test that empty dict raises error."""
        with pytest.raises(ValueError, match="exactly one key"):
            from_data({})

    def test_unknown_type(self):
        """Test that unknown type raises error."""
        data = {"unknown-type": "value"}
        with pytest.raises(ValueError, match="Unknown space type"):
            from_data(data)


class TestFromJson:
    """Tests for from_json function."""

    def test_from_json_string(self):
        """Test creating unit from JSON string."""
        json_str = '"m"'
        unit = from_json(json_str)
        assert isinstance(unit, UnitTerm)
        assert unit.to_data() == "m"

    def test_from_json_dict(self):
        """Test creating unit from JSON dictionary."""
        data = {"unit": "m"}
        json_str = json.dumps(data)
        unit = from_json(json_str)
        assert isinstance(unit, UnitTerm)
        assert unit.to_data() == "m"

    def test_invalid_json(self):
        """Test that invalid JSON raises error."""
        with pytest.raises(json.JSONDecodeError):
            from_json("invalid json")


class TestDimensionFactory:
    """Tests for dimension factory function."""

    def test_create_dimension_with_type(self):
        """Test creating dimension with explicit type."""
        dim = dimension(id="x", unit="m", type="space")
        assert isinstance(dim, Dimension)
        assert dim.id == "x"
        assert dim.unit.value == "m"
        assert dim.type == DimensionType.SPACE

    def test_create_dimension_type_inference(self):
        """Test creating dimension with inferred type."""
        # Spatial unit
        dim_m = dimension(id="x", unit="m")
        assert dim_m.type == DimensionType.SPACE

        # Temporal unit
        dim_s = dimension(id="time", unit="s")
        assert dim_s.type == DimensionType.TIME

        # Index unit
        dim_idx = dimension(id="idx", unit="index")
        assert dim_idx.type == DimensionType.INDEX

        # Arbitrary unit
        dim_arb = dimension(id="channel", unit="arbitrary")
        assert dim_arb.type == DimensionType.OTHER

    def test_dimension_from_data(self):
        """Test creating dimension via from_data."""
        # With explicit type
        data = {"dimension": {"id": "x", "unit": "m", "type": "space"}}
        dim = from_data(data)
        assert isinstance(dim, Dimension)
        assert dim.id == "x"
        assert dim.unit.value == "m"
        assert dim.type == DimensionType.SPACE

        # With type inference
        data_no_type = {"dimension": {"id": "y", "unit": "mm"}}
        dim2 = from_data(data_no_type)
        assert dim2.id == "y"
        assert dim2.unit.value == "mm"
        assert dim2.type == DimensionType.SPACE  # Inferred

    def test_dimension_from_json(self):
        """Test creating dimension from JSON."""
        # With explicit type
        json_str = '{"dimension": {"id": "time", "unit": "ms", "type": "time"}}'
        dim = from_json(json_str)
        assert isinstance(dim, Dimension)
        assert dim.id == "time"
        assert dim.unit.value == "ms"
        assert dim.type == DimensionType.TIME

        # With type inference
        json_str_no_type = '{"dimension": {"id": "z", "unit": "µm"}}'
        dim2 = from_json(json_str_no_type)
        assert dim2.id == "z"
        assert dim2.unit.value == "µm"
        assert dim2.type == DimensionType.SPACE  # Inferred

    def test_dimension_invalid_data(self):
        """Test dimension factory with invalid data."""
        # Invalid dimension type
        with pytest.raises(
            ValueError, match="'invalid_type' is not a valid DimensionType"
        ):
            dimension(id="x", unit="m", type="invalid_type")

        # Invalid unit
        with pytest.raises(pint.UndefinedUnitError):
            dimension(id="x", unit="invalid_unit_xyz")
