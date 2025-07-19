"""Tests for noid_spaces.factory module."""

import json

import pytest

from noid_spaces.factory import (
    coordinate_system,
    coordinate_transform,
    dimension,
    from_dict,
    from_json,
)
from noid_spaces.models import CoordinateSystem, CoordinateTransform, Dimension


class TestFactoryFunctions:
    """Test cases for factory functions."""

    def test_dimension_factory(self):
        """Test dimension factory function."""
        dim = dimension(id="x", unit="micrometer", type="space")
        assert isinstance(dim, Dimension)
        assert dim.id == "x"
        assert dim.unit == "micrometer"
        assert dim.type == "space"

    def test_dimension_factory_index(self):
        """Test dimension factory for index dimensions."""
        dim = dimension(id="i", unit="index", type="index")
        assert isinstance(dim, Dimension)
        assert dim.is_index
        assert dim.unit == "index"

    def test_dimension_factory_invalid(self):
        """Test dimension factory with invalid parameters."""
        with pytest.raises(ValueError):
            dimension(id="", unit="meter", type="space")

        with pytest.raises(ValueError):
            dimension(id="x", unit="meter", type="invalid")

    def test_coordinate_system_factory_with_dicts(self):
        """Test coordinate system factory with dimension dictionaries."""
        coord_sys = coordinate_system(
            id="physical",
            dimensions=[
                {"id": "x", "unit": "micrometer", "type": "space"},
                {"id": "y", "unit": "micrometer", "type": "space"},
            ],
            description="Physical space",
        )
        assert isinstance(coord_sys, CoordinateSystem)
        assert coord_sys.id == "physical"
        assert len(coord_sys.dimensions) == 2
        assert coord_sys.description == "Physical space"
        assert all(isinstance(dim, Dimension) for dim in coord_sys.dimensions)

    def test_coordinate_system_factory_with_strings(self):
        """Test coordinate system factory with string references."""
        coord_sys = coordinate_system(id="array", dimensions=["i", "j", "k"])
        assert isinstance(coord_sys, CoordinateSystem)
        assert coord_sys.id == "array"
        assert len(coord_sys.dimensions) == 3
        assert coord_sys.dimensions[0] == "i"

    def test_coordinate_system_factory_mixed(self):
        """Test coordinate system factory with mixed dimension types."""
        coord_sys = coordinate_system(
            id="mixed",
            dimensions=[{"id": "x", "unit": "meter", "type": "space"}, "ref_dim"],
        )
        assert isinstance(coord_sys, CoordinateSystem)
        assert len(coord_sys.dimensions) == 2
        assert isinstance(coord_sys.dimensions[0], Dimension)
        assert coord_sys.dimensions[1] == "ref_dim"

    def test_coordinate_transform_factory(self):
        """Test coordinate transform factory function."""
        transform = coordinate_transform(
            id="physical_to_array",
            input="physical_space",
            output="array_space",
            transform={"scale": [0.5, 0.5, 1.0]},
            description="Scale transform",
        )
        assert isinstance(transform, CoordinateTransform)
        assert transform.id == "physical_to_array"
        assert transform.input == "physical_space"
        assert transform.output == "array_space"
        assert transform.transform == {"scale": [0.5, 0.5, 1.0]}
        assert transform.description == "Scale transform"

    def test_coordinate_transform_factory_minimal(self):
        """Test coordinate transform factory with minimal parameters."""
        transform = coordinate_transform(
            id="simple", input="input", output="output", transform={"identity": True}
        )
        assert isinstance(transform, CoordinateTransform)
        assert transform.description is None


class TestFromDict:
    """Test cases for from_dict function."""

    def test_from_dict_dimension(self):
        """Test creating dimension from dictionary."""
        data = {"dimension": {"id": "x", "unit": "micrometer", "type": "space"}}
        result = from_dict(data)
        assert isinstance(result, Dimension)
        assert result.id == "x"
        assert result.unit == "micrometer"
        assert result.type == "space"

    def test_from_dict_coordinate_system(self):
        """Test creating coordinate system from dictionary."""
        data = {
            "coordinate-system": {
                "id": "physical",
                "dimensions": [
                    {"id": "x", "unit": "micrometer", "type": "space"},
                    {"id": "y", "unit": "micrometer", "type": "space"},
                ],
                "description": "Physical coordinate system",
            }
        }
        result = from_dict(data)
        assert isinstance(result, CoordinateSystem)
        assert result.id == "physical"
        assert len(result.dimensions) == 2
        assert result.description == "Physical coordinate system"

    def test_from_dict_coordinate_transform(self):
        """Test creating coordinate transform from dictionary."""
        data = {
            "coordinate-transform": {
                "id": "physical_to_array",
                "input": "physical_space",
                "output": "array_space",
                "transform": {"scale": [0.5, 0.5, 1.0]},
            }
        }
        result = from_dict(data)
        assert isinstance(result, CoordinateTransform)
        assert result.id == "physical_to_array"
        assert result.input == "physical_space"
        assert result.output == "array_space"
        assert result.transform == {"scale": [0.5, 0.5, 1.0]}

    def test_from_dict_invalid_format(self):
        """Test from_dict with invalid dictionary format."""
        # Multiple keys
        with pytest.raises(
            ValueError, match="Space dictionary must have exactly one key"
        ):
            from_dict(
                {
                    "dimension": {"id": "x", "unit": "meter", "type": "space"},
                    "coordinate-system": {"id": "test", "dimensions": []},
                }
            )

        # No keys
        with pytest.raises(
            ValueError, match="Space dictionary must have exactly one key"
        ):
            from_dict({})

    def test_from_dict_unknown_type(self):
        """Test from_dict with unknown space type."""
        data = {"unknown-type": {"id": "test"}}
        with pytest.raises(ValueError, match="Unknown space type: 'unknown-type'"):
            from_dict(data)

    def test_from_dict_non_dict_input(self):
        """Test from_dict with non-dictionary input."""
        # This should now raise an error since we removed the non-dict check
        # in the updated factory.py
        with pytest.raises(
            ValueError, match="Space dictionary must have exactly one key"
        ):
            from_dict("not a dict")


class TestFromJson:
    """Test cases for from_json function."""

    def test_from_json_dimension(self):
        """Test creating dimension from JSON string."""
        json_str = json.dumps(
            {"dimension": {"id": "x", "unit": "micrometer", "type": "space"}}
        )
        result = from_json(json_str)
        assert isinstance(result, Dimension)
        assert result.id == "x"
        assert result.unit == "micrometer"
        assert result.type == "space"

    def test_from_json_coordinate_system(self):
        """Test creating coordinate system from JSON string."""
        json_str = json.dumps(
            {
                "coordinate-system": {
                    "id": "physical",
                    "dimensions": [
                        {"id": "x", "unit": "meter", "type": "space"},
                        {"id": "y", "unit": "meter", "type": "space"},
                    ],
                }
            }
        )
        result = from_json(json_str)
        assert isinstance(result, CoordinateSystem)
        assert result.id == "physical"
        assert len(result.dimensions) == 2

    def test_from_json_coordinate_transform(self):
        """Test creating coordinate transform from JSON string."""
        json_str = json.dumps(
            {
                "coordinate-transform": {
                    "id": "test_transform",
                    "input": "input_space",
                    "output": "output_space",
                    "transform": {"translation": [10, 20, 5]},
                }
            }
        )
        result = from_json(json_str)
        assert isinstance(result, CoordinateTransform)
        assert result.id == "test_transform"
        assert result.transform == {"translation": [10, 20, 5]}

    def test_from_json_invalid_json(self):
        """Test from_json with invalid JSON string."""
        with pytest.raises(json.JSONDecodeError):
            from_json("invalid json {")

    def test_from_json_invalid_content(self):
        """Test from_json with invalid content structure."""
        json_str = json.dumps({"unknown-type": {"id": "test"}})
        with pytest.raises(ValueError, match="Unknown space type"):
            from_json(json_str)


class TestRegistryIntegration:
    """Test cases for registry integration."""

    def test_registry_dimension_creation(self):
        """Test that dimension factory is properly registered."""
        # This tests that the @register decorator worked
        from noid_registry import get_schema_namespace, registry

        namespace = get_schema_namespace("space")
        namespace = namespace.rstrip("/") + "/"
        full_iri = f"{namespace}dimension"

        # Should be able to create through registry
        result = registry.create(
            full_iri, {"id": "test", "unit": "meter", "type": "space"}
        )
        assert isinstance(result, Dimension)
        assert result.id == "test"

    def test_registry_coordinate_system_creation(self):
        """Test that coordinate system factory is properly registered."""
        from noid_registry import get_schema_namespace, registry

        namespace = get_schema_namespace("space")
        namespace = namespace.rstrip("/") + "/"
        full_iri = f"{namespace}coordinate-system"

        result = registry.create(
            full_iri,
            {
                "id": "test_system",
                "dimensions": [{"id": "x", "unit": "meter", "type": "space"}],
            },
        )
        assert isinstance(result, CoordinateSystem)
        assert result.id == "test_system"

    def test_registry_coordinate_transform_creation(self):
        """Test that coordinate transform factory is properly registered."""
        from noid_registry import get_schema_namespace, registry

        namespace = get_schema_namespace("space")
        namespace = namespace.rstrip("/") + "/"
        full_iri = f"{namespace}coordinate-transform"

        result = registry.create(
            full_iri,
            {
                "id": "test_transform",
                "input": "input",
                "output": "output",
                "transform": {"identity": True},
            },
        )
        assert isinstance(result, CoordinateTransform)
        assert result.id == "test_transform"


class TestComplexExamples:
    """Test cases with complex, realistic examples."""

    def test_complete_bioimaging_workflow(self):
        """Test a complete bioimaging coordinate space workflow."""
        # Create physical coordinate system
        physical_data = {
            "coordinate-system": {
                "id": "physical_space",
                "dimensions": [
                    {"id": "x", "unit": "micrometer", "type": "space"},
                    {"id": "y", "unit": "micrometer", "type": "space"},
                    {"id": "z", "unit": "micrometer", "type": "space"},
                    {"id": "t", "unit": "second", "type": "time"},
                    {"id": "c", "unit": "arbitrary", "type": "other"},
                ],
                "description": "5D microscopy coordinate system",
            }
        }
        physical_cs = from_dict(physical_data)
        assert isinstance(physical_cs, CoordinateSystem)
        assert physical_cs.dimension_count == 5

        # Create array coordinate system
        array_data = {
            "coordinate-system": {
                "id": "array_space",
                "dimensions": [
                    {"id": "i", "unit": "index", "type": "index"},
                    {"id": "j", "unit": "index", "type": "index"},
                    {"id": "k", "unit": "index", "type": "index"},
                    {"id": "t_idx", "unit": "index", "type": "index"},
                    {"id": "c_idx", "unit": "index", "type": "index"},
                ],
                "description": "Array index coordinate system",
            }
        }
        array_cs = from_dict(array_data)
        assert isinstance(array_cs, CoordinateSystem)
        assert array_cs.dimension_count == 5

        # Create coordinate transform
        transform_data = {
            "coordinate-transform": {
                "id": "physical_to_array",
                "input": "physical_space",
                "output": "array_space",
                "transform": {
                    "scale": [0.1, 0.1, 0.5, 1.0, 1.0],
                    "translation": [0, 0, 0, 0, 0],
                },
                "description": "Physical to array coordinate transform",
            }
        }
        transform = from_dict(transform_data)
        assert isinstance(transform, CoordinateTransform)
        assert transform.id == "physical_to_array"

    def test_geospatial_integration_example(self):
        """Test geospatial coordinate system example."""
        # Geographic coordinate system
        geo_data = {
            "coordinate-system": {
                "id": "wgs84",
                "dimensions": [
                    {"id": "longitude", "unit": "degree", "type": "space"},
                    {"id": "latitude", "unit": "degree", "type": "space"},
                    {"id": "elevation", "unit": "meter", "type": "space"},
                ],
                "description": "WGS84 geographic coordinate system",
            }
        }
        geo_cs = from_dict(geo_data)
        assert isinstance(geo_cs, CoordinateSystem)
        assert len(geo_cs.spatial_dimensions) == 3

        # UTM projected coordinate system
        utm_data = {
            "coordinate-system": {
                "id": "utm_zone_10n",
                "dimensions": [
                    {"id": "easting", "unit": "meter", "type": "space"},
                    {"id": "northing", "unit": "meter", "type": "space"},
                    {"id": "elevation", "unit": "meter", "type": "space"},
                ],
                "description": "UTM Zone 10N projected coordinate system",
            }
        }
        utm_cs = from_dict(utm_data)
        assert isinstance(utm_cs, CoordinateSystem)
        assert len(utm_cs.spatial_dimensions) == 3
