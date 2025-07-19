"""Integration tests for noid-spaces package."""

import json
import pytest

import noid_spaces
from noid_spaces import (
    CoordinateSystem,
    CoordinateTransform,
    Dimension,
    coordinate_system,
    coordinate_transform,
    dimension,
    from_dict,
    from_json,
    validate_dimension_unit,
)


class TestPackageAPI:
    """Test the main package API."""

    def test_package_imports(self):
        """Test that all expected symbols are importable."""
        # Test main classes
        assert hasattr(noid_spaces, 'Dimension')
        assert hasattr(noid_spaces, 'CoordinateSystem')
        assert hasattr(noid_spaces, 'CoordinateTransform')

        # Test factory functions
        assert hasattr(noid_spaces, 'dimension')
        assert hasattr(noid_spaces, 'coordinate_system')
        assert hasattr(noid_spaces, 'coordinate_transform')
        assert hasattr(noid_spaces, 'from_dict')
        assert hasattr(noid_spaces, 'from_json')

        # Test validation functions
        assert hasattr(noid_spaces, 'validate_dimension_unit')
        assert hasattr(noid_spaces, 'validate_udunits_string')

        # Test JSON-LD functions (from noid-registry)
        assert hasattr(noid_spaces, 'to_jsonld')
        assert hasattr(noid_spaces, 'from_jsonld')

    def test_package_version(self):
        """Test package version is defined."""
        assert hasattr(noid_spaces, '__version__')
        assert noid_spaces.__version__ == "0.1.0"


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def test_bioimaging_workflow(self):
        """Test a complete bioimaging data workflow."""
        # Step 1: Create physical coordinate system
        x_dim = dimension("x", "micrometer", "space")
        y_dim = dimension("y", "micrometer", "space")
        z_dim = dimension("z", "micrometer", "space")
        t_dim = dimension("t", "second", "time")
        c_dim = dimension("c", "arbitrary", "other")

        physical_cs = coordinate_system(
            "physical_space",
            [x_dim, y_dim, z_dim, t_dim, c_dim],
            "5D microscopy coordinate system"
        )

        assert physical_cs.dimension_count == 5
        assert len(physical_cs.spatial_dimensions) == 3
        assert len(physical_cs.temporal_dimensions) == 1
        assert physical_cs.get_dimension_by_id("x").unit == "micrometer"

        # Step 2: Create array coordinate system
        array_cs = coordinate_system(
            "array_space",
            [
                dimension("i", "index", "index"),
                dimension("j", "index", "index"),
                dimension("k", "index", "index"),
                dimension("t_idx", "index", "index"),
                dimension("c_idx", "index", "index")
            ],
            "Array index coordinate system"
        )

        assert array_cs.dimension_count == 5
        assert len(array_cs.index_dimensions) == 5

        # Step 3: Create coordinate transform
        transform = coordinate_transform(
            "physical_to_array",
            "physical_space",
            "array_space",
            {
                "scale": [0.1, 0.1, 0.5, 1.0, 1.0],
                "translation": [0, 0, 0, 0, 0]
            },
            "Physical to array transform"
        )

        assert transform.id == "physical_to_array"
        assert transform.description == "Physical to array transform"

        # Step 4: Test serialization
        physical_dict = physical_cs.to_dict()
        assert physical_dict["id"] == "physical_space"
        assert len(physical_dict["dimensions"]) == 5

        transform_dict = transform.to_dict()
        assert transform_dict["id"] == "physical_to_array"
        assert "scale" in str(transform_dict["transform"])

    def test_geospatial_workflow(self):
        """Test a geospatial coordinate system workflow."""
        # Geographic coordinate system (WGS84)
        wgs84_data = {
            "coordinate-system": {
                "id": "wgs84",
                "dimensions": [
                    {"id": "longitude", "unit": "degree", "type": "space"},
                    {"id": "latitude", "unit": "degree", "type": "space"},
                    {"id": "elevation", "unit": "meter", "type": "space"}
                ],
                "description": "WGS84 geographic coordinate system"
            }
        }
        wgs84_cs = from_dict(wgs84_data)

        # UTM projected coordinate system
        utm_data = {
            "coordinate-system": {
                "id": "utm_10n",
                "dimensions": [
                    {"id": "easting", "unit": "meter", "type": "space"},
                    {"id": "northing", "unit": "meter", "type": "space"},
                    {"id": "elevation", "unit": "meter", "type": "space"}
                ],
                "description": "UTM Zone 10N coordinate system"
            }
        }
        utm_cs = from_dict(utm_data)

        # Transform between coordinate systems
        transform_data = {
            "coordinate-transform": {
                "id": "wgs84_to_utm10n",
                "input": "wgs84",
                "output": "utm_10n",
                "transform": {
                    "projection": "utm",
                    "zone": 10,
                    "hemisphere": "north"
                },
                "description": "WGS84 to UTM Zone 10N projection"
            }
        }
        transform = from_dict(transform_data)

        assert wgs84_cs.dimension_count == 3
        assert utm_cs.dimension_count == 3
        assert len(wgs84_cs.spatial_dimensions) == 3
        assert len(utm_cs.spatial_dimensions) == 3
        assert transform.id == "wgs84_to_utm10n"

    def test_mixed_dimension_workflow(self):
        """Test workflow with mixed dimension types and references."""
        # Create coordinate system with mixed dimensions
        mixed_data = {
            "coordinate-system": {
                "id": "mixed_system",
                "dimensions": [
                    {"id": "x", "unit": "micrometer", "type": "space"},
                    "y_reference",  # String reference
                    {"id": "t", "unit": "second", "type": "time"},
                    {"id": "i", "unit": "index", "type": "index"},
                    {"id": "c", "unit": "arbitrary", "type": "other"}
                ]
            }
        }

        mixed_cs = from_dict(mixed_data)
        assert mixed_cs.dimension_count == 5

        # Check that we can handle both objects and references
        dimensions = mixed_cs.dimensions
        assert isinstance(dimensions[0], Dimension)  # x dimension
        assert dimensions[1] == "y_reference"  # string reference
        assert isinstance(dimensions[2], Dimension)  # t dimension

        # Test filtering - only counts actual Dimension objects
        spatial_dims = mixed_cs.spatial_dimensions
        temporal_dims = mixed_cs.temporal_dimensions
        index_dims = mixed_cs.index_dimensions

        assert len(spatial_dims) == 1  # Only x, not y_reference
        assert len(temporal_dims) == 1  # t
        assert len(index_dims) == 1    # i


class TestJSONSerialization:
    """Test JSON serialization and deserialization."""

    def test_dimension_json_roundtrip(self):
        """Test dimension JSON serialization roundtrip."""
        original_data = {
            "dimension": {
                "id": "x",
                "unit": "micrometer",
                "type": "space"
            }
        }

        # Create from JSON
        json_str = json.dumps(original_data)
        dim = from_json(json_str)

        # Verify properties
        assert isinstance(dim, Dimension)
        assert dim.id == "x"
        assert dim.unit == "micrometer"
        assert dim.type == "space"

        # Convert back to dict
        dim_dict = dim.to_dict()
        assert dim_dict["id"] == "x"
        assert dim_dict["unit"] == "micrometer"
        assert dim_dict["type"] == "space"

    def test_coordinate_system_json_roundtrip(self):
        """Test coordinate system JSON serialization roundtrip."""
        original_data = {
            "coordinate-system": {
                "id": "test_system",
                "dimensions": [
                    {"id": "x", "unit": "meter", "type": "space"},
                    {"id": "y", "unit": "meter", "type": "space"},
                    {"id": "t", "unit": "second", "type": "time"}
                ],
                "description": "Test coordinate system"
            }
        }

        # Create from JSON
        json_str = json.dumps(original_data)
        cs = from_json(json_str)

        # Verify properties
        assert isinstance(cs, CoordinateSystem)
        assert cs.id == "test_system"
        assert cs.dimension_count == 3
        assert cs.description == "Test coordinate system"

        # Convert back to dict
        cs_dict = cs.to_dict()
        assert cs_dict["id"] == "test_system"
        assert len(cs_dict["dimensions"]) == 3
        assert cs_dict["description"] == "Test coordinate system"

    def test_coordinate_transform_json_roundtrip(self):
        """Test coordinate transform JSON serialization roundtrip."""
        original_data = {
            "coordinate-transform": {
                "id": "test_transform",
                "input": "input_space",
                "output": "output_space",
                "transform": {
                    "scale": [2.0, 1.5, 0.5],
                    "translation": [10, 20, 5]
                },
                "description": "Test transform"
            }
        }

        # Create from JSON
        json_str = json.dumps(original_data)
        transform = from_json(json_str)

        # Verify properties
        assert isinstance(transform, CoordinateTransform)
        assert transform.id == "test_transform"
        assert transform.input == "input_space"
        assert transform.output == "output_space"
        assert transform.description == "Test transform"

        # Convert back to dict
        transform_dict = transform.to_dict()
        assert transform_dict["id"] == "test_transform"
        assert transform_dict["input"] == "input_space"
        assert transform_dict["output"] == "output_space"


class TestValidationIntegration:
    """Test validation integration in real workflows."""

    def test_unit_validation_workflow(self):
        """Test unit validation in typical workflows."""
        # These should work - special units
        validate_dimension_unit("index", "index")
        validate_dimension_unit("arbitrary", "other")
        validate_dimension_unit("index", "space")  # Special units work everywhere

        # This should fail - index constraint
        with pytest.raises(Exception):  # UdunitsValidationError
            validate_dimension_unit("meter", "index")

        # Other dimensions accept custom units
        validate_dimension_unit("custom_wavelength", "other")
        validate_dimension_unit("fluorescence_intensity", "other")

    def test_model_validation_integration(self):
        """Test how validation integrates with model creation."""
        # Valid cases
        dim1 = Dimension("x", "micrometer", "space")  # Would validate with UDUNITS-2
        dim2 = Dimension("i", "index", "index")       # Special case
        dim3 = Dimension("c", "arbitrary", "other")   # Custom unit for other

        # Invalid case - index constraint
        with pytest.raises(ValueError, match="Index type dimensions must have 'index' unit"):
            Dimension("i", "meter", "index")

        # Create coordinate system with validated dimensions
        cs = CoordinateSystem("test", [dim1, dim2, dim3])
        assert cs.dimension_count == 3


class TestErrorHandling:
    """Test error handling across the package."""

    def test_invalid_dimension_creation(self):
        """Test error handling in dimension creation."""
        with pytest.raises(ValueError):
            dimension("", "meter", "space")  # Empty ID

        with pytest.raises(ValueError):
            dimension("x", "meter", "invalid")  # Invalid type

        with pytest.raises(ValueError):
            dimension("i", "meter", "index")  # Index constraint violation

    def test_invalid_factory_usage(self):
        """Test error handling in factory functions."""
        with pytest.raises(ValueError):
            from_dict({})  # Empty dict

        with pytest.raises(ValueError):
            from_dict({"unknown-type": {"id": "test"}})  # Unknown type

        with pytest.raises(json.JSONDecodeError):
            from_json("invalid json")  # Invalid JSON

    def test_invalid_coordinate_system_creation(self):
        """Test error handling in coordinate system creation."""
        with pytest.raises(ValueError):
            coordinate_system("", [])  # Empty ID and dimensions

        with pytest.raises(ValueError):
            coordinate_system("test", [])  # No dimensions

        with pytest.raises(ValueError):
            coordinate_system("test", [123])  # Invalid dimension type


class TestPerformanceAndEdgeCases:
    """Test performance and edge cases."""

    def test_large_coordinate_system(self):
        """Test coordinate system with many dimensions."""
        # Create 100 dimensions
        dimensions = []
        for i in range(100):
            dimensions.append({
                "id": f"dim_{i}",
                "unit": "arbitrary" if i % 2 == 0 else "index",
                "type": "other" if i % 2 == 0 else "index"
            })

        cs_data = {
            "coordinate-system": {
                "id": "large_system",
                "dimensions": dimensions
            }
        }

        cs = from_dict(cs_data)
        assert cs.dimension_count == 100

        # Test filtering operations
        other_dims = cs.spatial_dimensions  # Should be empty
        assert len(other_dims) == 0

        # Get dimension by ID should work
        dim_50 = cs.get_dimension_by_id("dim_50")
        assert dim_50 is not None
        assert dim_50.id == "dim_50"

    def test_nested_coordinate_transforms(self):
        """Test coordinate transforms with complex nested structures."""
        complex_transform_data = {
            "coordinate-transform": {
                "id": "complex_transform",
                "input": {
                    "dimensions": [
                        {"id": "x", "unit": "meter", "type": "space"},
                        {"id": "y", "unit": "meter", "type": "space"}
                    ]
                },
                "output": {
                    "dimensions": [
                        {"id": "i", "unit": "index", "type": "index"},
                        {"id": "j", "unit": "index", "type": "index"}
                    ]
                },
                "transform": {
                    "homogeneous": [
                        [0.1, 0, 0],
                        [0, 0.1, 0],
                        [0, 0, 1]
                    ]
                }
            }
        }

        transform = from_dict(complex_transform_data)
        assert transform.id == "complex_transform"
        assert isinstance(transform.input, dict)
        assert isinstance(transform.output, dict)
        assert "homogeneous" in str(transform.transform)
