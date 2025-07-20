"""Tests for space model classes."""

import pint
import pytest

from noid_spaces.models import Dimension, DimensionType, UnitTerm


class TestUnitTerm:
    """Tests for UnitTerm class."""

    def test_non_physical_unit_index(self):
        """Test creating index non-physical unit."""
        unit = UnitTerm("index")
        assert unit.is_non_physical
        assert unit.to_dimension_type() == DimensionType.INDEX
        assert unit.dimensionality == "index"
        assert unit.to_data() == "index"
        assert str(unit) == "index"
        assert repr(unit) == "UnitTerm('index')"
        # Non-physical units should still have Pint representation
        assert unit.pint_unit is not None
        assert unit.pint_unit.dimensionless

    def test_non_physical_unit_arbitrary(self):
        """Test creating arbitrary non-physical unit."""
        unit = UnitTerm("arbitrary")
        assert unit.is_non_physical
        assert unit.to_dimension_type() == DimensionType.OTHER
        assert unit.dimensionality == "arbitrary"
        assert unit.to_data() == "arbitrary"
        # Non-physical units should still have Pint representation
        assert unit.pint_unit is not None
        assert unit.pint_unit.dimensionless

    def test_physical_unit_meter(self):
        """Test creating meter physical unit."""
        unit = UnitTerm("m")
        assert not unit.is_non_physical
        assert unit.to_data() == "m"
        assert unit.pint_unit is not None

    def test_physical_unit_second(self):
        """Test creating second physical unit."""
        unit = UnitTerm("s")
        assert not unit.is_non_physical
        assert unit.to_data() == "s"

    def test_physical_unit_dimensionless(self):
        """Test creating dimensionless physical unit."""
        unit = UnitTerm("1")
        assert not unit.is_non_physical
        assert unit.to_data() == "1"

    def test_physical_unit_complex(self):
        """Test creating complex physical unit."""
        unit = UnitTerm("kg/m^3")
        assert not unit.is_non_physical
        assert unit.to_data() == "kg/m^3"

    def test_invalid_unit_empty(self):
        """Test that empty unit raises error."""
        with pytest.raises(ValueError, match="Unit must be a non-empty string"):
            UnitTerm("")

    def test_invalid_physical_unit(self):
        """Test that invalid physical unit raises error."""
        with pytest.raises(pint.UndefinedUnitError):
            UnitTerm("invalidunit12345")

    def test_invalid_unit_with_magnitude(self):
        """Test that unit strings with magnitudes raise error."""
        with pytest.raises(ValueError, match="contains a magnitude"):
            UnitTerm("5 m")

        with pytest.raises(ValueError, match="contains a magnitude"):
            UnitTerm("2.5 seconds")

    def test_equality(self):
        """Test unit equality."""
        unit1 = UnitTerm("m")
        unit2 = UnitTerm("m")
        unit3 = UnitTerm("s")

        assert unit1 == unit2
        assert unit1 != unit3
        assert unit1 != "m"  # Different type

    def test_hash(self):
        """Test unit hashing."""
        unit1 = UnitTerm("m")
        unit2 = UnitTerm("m")
        unit3 = UnitTerm("s")

        assert hash(unit1) == hash(unit2)
        assert hash(unit1) != hash(unit3)

        # Test in set
        unit_set = {unit1, unit2, unit3}
        assert len(unit_set) == 2  # unit1 and unit2 are the same

    def test_to_dimension_type(self):
        """Test projecting units to dimension types."""
        # Spatial units
        meter = UnitTerm("m")
        assert meter.to_dimension_type() == DimensionType.SPACE

        micrometer = UnitTerm("µm")
        assert micrometer.to_dimension_type() == DimensionType.SPACE

        # Temporal units
        second = UnitTerm("s")
        assert second.to_dimension_type() == DimensionType.TIME

        # Special index unit
        index = UnitTerm("index")
        assert index.to_dimension_type() == DimensionType.INDEX

        # Non-physical arbitrary unit
        arbitrary = UnitTerm("arbitrary")
        assert arbitrary.to_dimension_type() == DimensionType.OTHER

        # Other physical units (chemistry, etc.)
        molarity = UnitTerm("M")
        assert molarity.to_dimension_type() == DimensionType.OTHER

    def test_to_quantity_method(self):
        """Test converting units to Pint quantities."""
        # Physical units
        meter = UnitTerm("m")
        quantity = meter.to_quantity(5.0)
        assert quantity.magnitude == 5.0
        assert str(quantity.units) == "meter"

        # Non-physical units map to dimensionless
        index = UnitTerm("index")
        quantity = index.to_quantity(3)
        assert quantity.magnitude == 3
        assert quantity.dimensionless

        arbitrary = UnitTerm("arbitrary")
        quantity = arbitrary.to_quantity(1.5)
        assert quantity.magnitude == 1.5
        assert quantity.dimensionless

    def test_biomedical_units(self):
        """Test biomedical-specific units."""
        # Microscopy units
        micrometer = UnitTerm("µm")
        assert micrometer.to_dimension_type() == DimensionType.SPACE
        assert micrometer.to_data() == "µm"

        nanometer = UnitTerm("nm")
        assert nanometer.to_dimension_type() == DimensionType.SPACE
        assert nanometer.to_data() == "nm"

        # Chemistry units
        molarity = UnitTerm("M")
        assert molarity.to_dimension_type() == DimensionType.OTHER
        assert molarity.to_data() == "M"

        # Test aliases
        micron = UnitTerm("micron")
        assert micron.to_dimension_type() == DimensionType.SPACE
        assert micron.to_data() == "micron"

    def test_list_units(self):
        """Test listing units by category."""
        # Test getting all units
        all_units = UnitTerm.list_units()
        assert len(all_units) > 0
        assert "micrometer" in all_units or "µm" in all_units

        # Test spatial units
        spatial_units = UnitTerm.list_units("spatial")
        assert len(spatial_units) > 0
        # Should contain microscopy units
        spatial_unit_names = " ".join(spatial_units)
        assert any(
            unit in spatial_unit_names for unit in ["micrometer", "nanometer", "meter"]
        )

        # Test temporal units
        temporal_units = UnitTerm.list_units("temporal")
        assert len(temporal_units) > 0

        # Test chemistry units
        chemistry_units = UnitTerm.list_units("chemistry")
        assert len(chemistry_units) > 0


class TestDimensionType:
    """Tests for DimensionType enum."""

    def test_enum_members(self):
        """Test enum members and their values."""
        assert DimensionType.SPACE.value == "space"
        assert DimensionType.TIME.value == "time"
        assert DimensionType.OTHER.value == "other"
        assert DimensionType.INDEX.value == "index"

    def test_enum_values(self):
        """Test enum values and basic functionality."""
        space = DimensionType.SPACE
        time = DimensionType.TIME
        other = DimensionType.OTHER
        index = DimensionType.INDEX

        # Test they are different
        assert space != time
        assert space != other
        assert space != index
        assert time != other

    def test_from_string(self):
        """Test creating enum from string value."""
        space = DimensionType("space")
        assert space == DimensionType.SPACE

        time = DimensionType("time")
        assert time == DimensionType.TIME

    def test_invalid_string(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            DimensionType("invalid")

    def test_to_data(self):
        """Test serialization method."""
        assert DimensionType.SPACE.to_data() == "space"
        assert DimensionType.TIME.to_data() == "time"
        assert DimensionType.OTHER.to_data() == "other"
        assert DimensionType.INDEX.to_data() == "index"

    def test_string_representation(self):
        """Test string representation."""
        space = DimensionType.SPACE
        assert str(space) == "DimensionType.SPACE"
        assert repr(space) == "<DimensionType.SPACE: 'space'>"

    def test_equality(self):
        """Test equality comparison."""
        space1 = DimensionType.SPACE
        space2 = DimensionType("space")
        time1 = DimensionType.TIME

        assert space1 == space2
        assert space1 != time1

        # Enum values don't equal strings by default
        assert space1.value == "space"

    def test_membership(self):
        """Test membership in containers."""
        space = DimensionType.SPACE
        time = DimensionType.TIME

        # Test in set
        type_set = {space, time}
        assert len(type_set) == 2
        assert space in type_set
        assert time in type_set

        # Test in list
        type_list = list(DimensionType)
        assert len(type_list) == 4
        assert DimensionType.SPACE in type_list


class TestDimension:
    """Tests for Dimension class."""

    def test_basic_creation(self):
        """Test creating dimension with explicit type."""
        dim = Dimension(id="x", unit="m", kind=DimensionType.SPACE)
        assert dim.id == "x"
        assert dim.unit.value == "m"
        assert dim.type == DimensionType.SPACE

    def test_type_inference_spatial(self):
        """Test type inference for spatial units."""
        # Meter
        dim_m = Dimension(id="x", unit="m")
        assert dim_m.type == DimensionType.SPACE

        # Millimeter
        dim_mm = Dimension(id="y", unit="mm")
        assert dim_mm.type == DimensionType.SPACE

        # Micrometer
        dim_um = Dimension(id="z", unit="µm")
        assert dim_um.type == DimensionType.SPACE

        # Nanometer
        dim_nm = Dimension(id="w", unit="nm")
        assert dim_nm.type == DimensionType.SPACE

    def test_type_inference_temporal(self):
        """Test type inference for temporal units."""
        # Second
        dim_s = Dimension(id="time", unit="s")
        assert dim_s.type == DimensionType.TIME

        # Millisecond
        dim_ms = Dimension(id="time2", unit="ms")
        assert dim_ms.type == DimensionType.TIME

        # Microsecond
        dim_us = Dimension(id="time3", unit="µs")
        assert dim_us.type == DimensionType.TIME

    def test_type_inference_special(self):
        """Test type inference for special units."""
        # Index
        dim_idx = Dimension(id="idx", unit="index")
        assert dim_idx.type == DimensionType.INDEX

        # Arbitrary
        dim_arb = Dimension(id="channel", unit="arbitrary")
        assert dim_arb.type == DimensionType.OTHER

    def test_type_inference_other(self):
        """Test type inference for other physical units."""
        # Molarity (chemistry)
        dim_m = Dimension(id="concentration", unit="M")
        assert dim_m.type == DimensionType.OTHER

        # Kelvin (temperature)
        dim_k = Dimension(id="temperature", unit="K")
        assert dim_k.type == DimensionType.OTHER

    def test_type_override(self):
        """Test overriding inferred type."""
        # Override spatial unit to OTHER (e.g., wavelength)
        dim = Dimension(id="wavelength", unit="nm", kind=DimensionType.OTHER)
        assert dim.type == DimensionType.OTHER

        # Override arbitrary unit to SPACE
        dim2 = Dimension(id="custom", unit="arbitrary", kind=DimensionType.SPACE)
        assert dim2.type == DimensionType.SPACE

        # Override temporal unit to OTHER
        dim3 = Dimension(id="duration", unit="ms", kind=DimensionType.OTHER)
        assert dim3.type == DimensionType.OTHER

    def test_index_type_validation(self):
        """Test that index type must have index unit."""
        with pytest.raises(
            ValueError, match="Dimension type 'index' requires unit 'index'"
        ):
            Dimension(id="bad", unit="m", kind=DimensionType.INDEX)

    def test_dimension_creation_shortcuts(self):
        """Test creating dimensions with common patterns."""
        # Spatial with inferred type
        x = Dimension(id="x", unit="mm")
        assert x.id == "x"
        assert x.unit.value == "mm"
        assert x.type == DimensionType.SPACE

        # Temporal with inferred type
        t = Dimension(id="time", unit="ms")
        assert t.id == "time"
        assert t.unit.value == "ms"
        assert t.type == DimensionType.TIME

        # Index with inferred type
        idx = Dimension(id="array_idx", unit="index")
        assert idx.id == "array_idx"
        assert idx.unit.value == "index"
        assert idx.type == DimensionType.INDEX

        # Channel with explicit type override (no warning expected)
        ch = Dimension(id="wavelength", unit="nm", kind=DimensionType.OTHER)
        assert ch.id == "wavelength"
        assert ch.unit.value == "nm"
        assert ch.type == DimensionType.OTHER

    def test_serialization(self):
        """Test dimension serialization."""
        dim = Dimension(id="x", unit="m", kind=DimensionType.SPACE)
        data = dim.to_data()

        assert data == {"id": "x", "unit": "m", "type": "space"}

        # Round trip
        dim2 = Dimension.from_data(data)
        assert dim == dim2

    def test_deserialization_with_type_inference(self):
        """Test deserializing dimension without explicit type."""
        # Without type field
        data = {"id": "y", "unit": "mm"}
        dim = Dimension.from_data(data)
        assert dim.id == "y"
        assert dim.unit.value == "mm"
        assert dim.type == DimensionType.SPACE  # Inferred

        # With type field
        data_with_type = {"id": "z", "unit": "s", "type": "time"}
        dim2 = Dimension.from_data(data_with_type)
        assert dim2.id == "z"
        assert dim2.unit.value == "s"
        assert dim2.type == DimensionType.TIME

    def test_equality(self):
        """Test dimension equality."""
        dim1 = Dimension(id="x", unit="m")
        dim2 = Dimension(id="x", unit="m", kind=DimensionType.SPACE)
        dim3 = Dimension(id="y", unit="m")

        assert dim1 == dim2  # Same, type inferred
        assert dim1 != dim3  # Different ID
        assert dim1 != "not a dimension"

    def test_string_representations(self):
        """Test string representations."""
        dim = Dimension(id="time", unit="ms", kind=DimensionType.TIME)

        # User-friendly
        assert str(dim) == "time [ms] (time)"

        # Developer-friendly
        assert repr(dim) == "Dimension(id='time', unit='ms', type='time')"

    def test_invalid_inputs(self):
        """Test invalid input handling."""
        # Empty ID
        with pytest.raises(ValueError, match="Dimension id must be a non-empty string"):
            Dimension(id="", unit="m")

        # Invalid unit
        with pytest.raises(pint.UndefinedUnitError):
            Dimension(id="x", unit="invalid_unit_xyz")

        # Invalid type string
        with pytest.raises(
            ValueError, match="'invalid_type' is not a valid DimensionType"
        ):
            Dimension(id="x", unit="m", kind="invalid_type")
