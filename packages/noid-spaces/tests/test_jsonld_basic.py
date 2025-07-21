"""Tests for basic JSON-LD serialization and deserialization."""

import json

from noid_registry import from_jsonld, to_jsonld

from noid_spaces.models import Dimension, DimensionType, Unit


class TestUnitTermJsonLD:
    """Tests for UnitTerm JSON-LD serialization."""

    def test_unit_term_to_jsonld(self):
        """Test converting UnitTerm to JSON-LD."""
        # Physical unit
        unit = Unit("m")
        jsonld = to_jsonld(unit)

        # Check that it's a JSON-LD object with the unit term
        assert isinstance(jsonld, dict)
        assert "@context" in jsonld
        # The key should be the prefixed unit-term IRI
        unit_key = None
        for key in jsonld:
            if key != "@context" and "unit" in key:
                unit_key = key
                break
        assert unit_key is not None
        assert jsonld[unit_key] == "m"

    def test_unit_term_from_jsonld(self):
        """Test creating UnitTerm from JSON-LD."""
        # Need to provide proper JSON-LD structure
        jsonld = {
            "@context": {"sp": "https://github.com/nclack/noid/schemas/space/"},
            "sp:unit": "m",
        }

        result = from_jsonld(jsonld)
        assert "sp:unit" in result
        assert isinstance(result["sp:unit"], Unit)
        assert result["sp:unit"].value == "m"

    def test_unit_term_roundtrip(self):
        """Test roundtrip conversion."""
        # Physical units
        units = ["m", "s", "kg/m^3", "µm", "ms"]
        for unit_str in units:
            original = Unit(unit_str)
            jsonld = to_jsonld(original)

            # from_jsonld returns a dict, extract the unit term
            result = from_jsonld(jsonld)

            assert "spac" in result["@context"]  # expected namespace
            unit_key = "spac:unit"
            restored = result[unit_key]
            assert isinstance(restored, Unit)
            assert restored == original

        # Non-physical units
        for unit_str in ["index", "arbitrary"]:
            original = Unit(unit_str)
            jsonld = to_jsonld(original)
            result = from_jsonld(jsonld)

            assert "spac" in result["@context"]  # expected namespace
            unit_key = "spac:unit"
            restored = result[unit_key]
            assert isinstance(restored, Unit)
            assert restored == original

    def test_unit_term_in_context(self):
        """Test UnitTerm in a larger JSON-LD context."""
        data = {
            "@context": {"sp": "https://github.com/nclack/noid/schemas/space/"},
            "sp:unit": "nm",
        }

        # The unit value should be extractable
        jsonld = from_jsonld(data)
        unit = jsonld["sp:unit"]
        assert unit.value == "nm"


class TestDimensionJsonLD:
    """Tests for Dimension JSON-LD serialization."""

    def test_dimension_to_jsonld_basic(self):
        """Test converting Dimension to JSON-LD."""
        dim = Dimension(dimension_id="x", unit="m", kind=DimensionType.SPACE)
        jsonld = to_jsonld(dim)

        # Check structure
        assert isinstance(jsonld, dict)
        assert "spac:dimension" in jsonld
        dim = jsonld["spac:dimension"]
        assert dim["id"] == "x"
        assert dim["unit"] == "m"
        assert dim["type"] == "space"

    def test_dimension_to_jsonld_inferred_type(self):
        """Test Dimension with inferred type to JSON-LD."""
        dim = Dimension(dimension_id="y", unit="mm")  # Type inferred as SPACE
        jsonld = to_jsonld(dim)

        # Check structure
        assert isinstance(jsonld, dict)
        assert "spac:dimension" in jsonld
        dim = jsonld["spac:dimension"]
        assert dim["id"] == "y"
        assert dim["unit"] == "mm"
        assert dim["type"] == "space"  # Inferred

    def test_dimension_from_jsonld_basic(self):
        """Test creating Dimension from JSON-LD."""
        jsonld = {
            "@context": {"spac": "https://github.com/nclack/noid/schemas/space/"},
            "@type": "spac:dimension",
            "id": "x",
            "unit": "m",
            "type": "space",
        }

        dim = from_jsonld(jsonld)
        assert isinstance(dim, Dimension)
        assert dim.id == "x"
        assert dim.unit.value == "m"
        assert dim.type == DimensionType.SPACE

    def test_dimension_from_jsonld_no_type(self):
        """Test creating Dimension from JSON-LD without type field."""
        jsonld = {
            "@context": {"spac": "https://github.com/nclack/noid/schemas/space/"},
            "@type": "spac:dimension",
            "id": "time",
            "unit": "s",
            # No type field - should be inferred
        }

        dim = from_jsonld(jsonld)
        assert dim.id == "time"
        assert dim.unit.value == "s"
        assert dim.type == DimensionType.TIME  # Inferred from unit

    def test_dimension_roundtrip(self):
        """Test roundtrip conversion."""
        # Test various dimension configurations
        test_cases = [
            # Explicit type
            Dimension(dimension_id="x", unit="m", kind=DimensionType.SPACE),
            # Inferred spatial
            Dimension(dimension_id="y", unit="mm"),
            # Inferred temporal
            Dimension(dimension_id="time", unit="ms"),
            # Inferred index
            Dimension(dimension_id="idx", unit="index"),
            # Type override
            Dimension(dimension_id="wavelength", unit="nm", kind=DimensionType.OTHER),
        ]

        for original in test_cases:
            jsonld = to_jsonld(original)
            result = from_jsonld(jsonld)
            # Extract dimension from property-based result
            restored = result["spac:dimension"]
            assert restored == original
            assert restored.id == original.id
            assert restored.unit.value == original.unit.value
            assert restored.type == original.type

    def test_dimension_from_jsonld_with_context(self):
        """Test Dimension from JSON-LD with full context."""
        jsonld = {
            "@context": {
                "@vocab": "https://github.com/nclack/noid/schemas/space/",
                "id": "@id",
            },
            "@type": "dimension",
            "id": "z",
            "unit": "µm",
            "type": "space",
        }

        dim = from_jsonld(jsonld)
        assert dim.id == "z"
        assert dim.unit.value == "µm"
        assert dim.type == DimensionType.SPACE

    def test_dimension_json_string(self):
        """Test full JSON string serialization."""
        dim = Dimension(dimension_id="x", unit="m")

        # Convert to JSON-LD then to JSON string
        jsonld = to_jsonld(dim)
        json_str = json.dumps(jsonld)

        # Parse back
        parsed = json.loads(json_str)
        result = from_jsonld(parsed)
        # Extract dimension from property-based result
        restored = result["spac:dimension"]

        assert restored == dim
