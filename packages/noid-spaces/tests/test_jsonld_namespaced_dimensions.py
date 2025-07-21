"""Tests for JSON-LD serialization with namespaced dimension IDs."""

from noid_registry import from_jsonld, to_jsonld

from noid_spaces import coordinate_system


class TestJsonLDNamespacedDimensions:
    """Test JSON-LD serialization with the new namespaced dimension ID system."""

    def test_coordinate_system_with_namespaced_dimensions_jsonld(self):
        """Test JSON-LD roundtrip for coordinate system with namespaced dimension IDs."""
        # Create coordinate system with mixed dimension ID types
        original_cs = coordinate_system(
            dimensions=[
                {"id": "x", "unit": "mm", "type": "space"},  # Explicit ID
                {"unit": "mm", "type": "space"},  # Auto-generated ID
                {"id": "time", "unit": "ms", "type": "time"},  # Explicit ID
            ],
            id="test-system",
            description="Test coordinate system for JSON-LD",
        )

        # Verify original dimension IDs are properly namespaced
        assert original_cs.dimensions[0].id == "test-system#x"
        assert original_cs.dimensions[1].id == "test-system#dim_1"
        assert original_cs.dimensions[2].id == "test-system#time"

        # Serialize to JSON-LD
        jsonld_data = to_jsonld(original_cs)

        # Verify JSON-LD structure contains namespaced dimension IDs
        assert isinstance(jsonld_data, dict)
        assert "@context" in jsonld_data

        # Extract the coordinate system data from JSON-LD
        cs_key = None
        for key in jsonld_data.keys():
            if key != "@context" and "coordinate-system" in key:
                cs_key = key
                break
        assert cs_key is not None

        cs_data = jsonld_data[cs_key]
        assert "dimensions" in cs_data
        assert len(cs_data["dimensions"]) == 3

        # Verify each dimension ID is properly namespaced in JSON-LD
        dim_data = cs_data["dimensions"]
        assert dim_data[0]["id"] == "test-system#x"
        assert dim_data[1]["id"] == "test-system#dim_1"
        assert dim_data[2]["id"] == "test-system#time"

        # Deserialize from JSON-LD
        jsonld_result = from_jsonld(jsonld_data)
        reconstructed_cs = jsonld_result[cs_key]

        # Verify roundtrip integrity
        assert reconstructed_cs.id == original_cs.id
        assert reconstructed_cs.description == original_cs.description
        assert len(reconstructed_cs.dimensions) == len(original_cs.dimensions)

        # Verify each dimension is perfectly reconstructed
        for orig_dim, reconst_dim in zip(
            original_cs.dimensions, reconstructed_cs.dimensions, strict=False
        ):
            assert orig_dim.id == reconst_dim.id
            assert orig_dim.unit.value == reconst_dim.unit.value
            assert orig_dim.type == reconst_dim.type

    def test_coordinate_system_without_id_jsonld(self):
        """Test JSON-LD roundtrip for coordinate system without ID (simple dimension IDs)."""
        # Create coordinate system without ID - dimensions should remain simple
        original_cs = coordinate_system(
            dimensions=[
                {"id": "x", "unit": "pixel", "type": "space"},
                {"unit": "pixel", "type": "space"},  # Auto-generated: dim_0
            ]
        )

        # Without coordinate system ID, dimensions should have simple IDs
        assert original_cs.dimensions[0].id == "x"
        assert original_cs.dimensions[1].id == "dim_1"

        # Test JSON-LD roundtrip
        jsonld_data = to_jsonld(original_cs)
        jsonld_result = from_jsonld(jsonld_data)

        # Extract coordinate system
        cs_key = None
        for key in jsonld_result.keys():
            if key != "@context" and "coordinate-system" in key:
                cs_key = key
                break
        assert cs_key is not None

        reconstructed_cs = jsonld_result[cs_key]

        # Verify simple IDs are preserved
        assert reconstructed_cs.dimensions[0].id == "x"
        assert reconstructed_cs.dimensions[1].id == "dim_1"
        assert len(reconstructed_cs.dimensions) == 2

    def test_mixed_dimension_scenarios_jsonld(self):
        """Test JSON-LD with various dimension identity scenarios."""
        scenarios = [
            # All explicit IDs
            {
                "dimensions": [
                    {"id": "x", "unit": "μm", "type": "space"},
                    {"id": "y", "unit": "μm", "type": "space"},
                    {"id": "z", "unit": "μm", "type": "space"},
                ],
                "id": "all-explicit",
                "expected_ids": ["all-explicit#x", "all-explicit#y", "all-explicit#z"],
            },
            # All auto-generated IDs
            {
                "dimensions": [
                    {"unit": "nm", "type": "space"},
                    {"unit": "nm", "type": "space"},
                    {"unit": "ms", "type": "time"},
                ],
                "id": "all-auto",
                "expected_ids": ["all-auto#dim_0", "all-auto#dim_1", "all-auto#dim_2"],
            },
            # Mixed explicit and auto IDs with type inference
            {
                "dimensions": [
                    {"id": "width", "unit": "mm"},  # Explicit ID, inferred type
                    {"unit": "mm"},  # Auto ID, inferred type
                    {"id": "t", "unit": "s"},  # Explicit ID, inferred type
                ],
                "id": "mixed-inferred",
                "expected_ids": [
                    "mixed-inferred#width",
                    "mixed-inferred#dim_1",
                    "mixed-inferred#t",
                ],
            },
        ]

        for scenario in scenarios:
            # Create coordinate system
            cs = coordinate_system(
                **{k: v for k, v in scenario.items() if k != "expected_ids"}
            )

            # Verify expected dimension IDs
            actual_ids = [dim.id for dim in cs.dimensions]
            assert actual_ids == scenario["expected_ids"]

            # Test JSON-LD roundtrip
            jsonld_data = to_jsonld(cs)
            jsonld_result = from_jsonld(jsonld_data)

            # Extract and verify reconstructed coordinate system
            cs_key = [
                k
                for k in jsonld_result.keys()
                if k != "@context" and "coordinate-system" in k
            ][0]
            reconstructed_cs = jsonld_result[cs_key]

            # Verify dimension IDs are preserved through JSON-LD roundtrip
            reconstructed_ids = [dim.id for dim in reconstructed_cs.dimensions]
            assert reconstructed_ids == scenario["expected_ids"]
