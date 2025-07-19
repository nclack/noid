"""
Integration tests for the complete registry system.

This module tests the end-to-end flow from JSON-LD input through registry dispatch
to transform creation and back to JSON-LD serialization.
"""

import json

from pyld import jsonld
import pytest

# Import the full system
from noid_transforms import (
    from_dict,
    from_jsonld,
    identity,
    scale,
    to_jsonld,
    translation,
)
from noid_registry import get_schema_namespace

# Import enhanced version for testing enhanced functionality
from noid_transforms.models import Identity, Scale, Translation


def validate_jsonld_spec(data) -> bool:
    """
    Validate that JSON-LD data conforms to the JSON-LD specification.

    Uses PyLD to attempt expansion, compaction, and flattening operations.
    If these succeed without exceptions, the JSON-LD is valid.

    Args:
        data: JSON-LD data (dict or list)

    Returns:
        True if valid JSON-LD, False otherwise
    """
    try:
        # Test expansion (most fundamental operation)
        expanded = jsonld.expand(data)
        if not isinstance(expanded, list):
            return False

        # Test flattening
        flattened = jsonld.flatten(data)
        if not isinstance(flattened, dict | list):
            return False

        # Test compaction if context is available
        if isinstance(data, dict) and "@context" in data:
            context = data["@context"]
            jsonld.compact(data, context)

        return True

    except Exception:
        # JSON-LD validation failed - this is expected for invalid data
        return False


class TestBasicIntegration:
    """Test basic integration with existing functionality."""

    def test_from_dict_registry_integration(self):
        """Test that from_dict uses the registry system internally."""
        # Test that registry-based dispatch works for standard transforms
        trans = from_dict({"translation": [10, 20, 30]})
        assert isinstance(trans, Translation)
        assert trans.translation == [10, 20, 30]

        sc = from_dict({"scale": [2.0, 1.5, 0.5]})
        assert isinstance(sc, Scale)
        assert sc.scale == [2.0, 1.5, 0.5]

        ident = from_dict("identity")
        assert isinstance(ident, Identity)

    def test_clean_error_messages(self):
        """Test clean error messages for unknown transforms."""
        with pytest.raises(ValueError) as exc_info:
            from_dict({"unknown_transform": [1, 2, 3]})

        error_msg = str(exc_info.value)
        # Should provide a clean error message
        assert "Unknown transform type: 'unknown_transform'" in error_msg

    def test_backward_compatibility(self):
        """Test that existing functionality still works."""
        # Test that all the existing factory functions work
        trans = translation([1, 2, 3])
        sc = scale([2.0, 1.5])
        ident = identity()

        assert isinstance(trans, Translation)
        assert isinstance(sc, Scale)
        assert isinstance(ident, Identity)

        # Test serialization - enhanced version returns dict when indent=None
        jsonld_data = to_jsonld(trans)
        assert isinstance(jsonld_data, dict)
        assert "@context" in jsonld_data

        # Test that we can get a string when indent is specified
        jsonld_str = to_jsonld(trans, indent=2)
        assert isinstance(jsonld_str, str)
        assert "translation" in jsonld_str


class TestEnhancedJSONLDIntegration:
    """Test enhanced JSON-LD processing with PyLD integration."""

    def test_simple_jsonld_roundtrip(self):
        """Test round-trip processing of JSON-LD."""
        transform_namespace = get_schema_namespace("transform")
        input_jsonld = {
            "@context": {"tr": transform_namespace},
            "tr:translation": [10, 20, 30],
            "other_data": "preserved",
        }

        # Process with enhanced from_jsonld
        result = from_jsonld(input_jsonld)

        # Should have preserved context and converted transform
        assert "@context" in result
        assert "other_data" in result
        assert result["other_data"] == "preserved"

        # Should have created Transform object
        transform_found = False
        for _key, value in result.items():
            if isinstance(value, Translation):
                assert value.translation == [10, 20, 30]
                transform_found = True
                break

        assert transform_found, "No Translation object found in result"

    def test_multi_namespace_processing(self):
        """Test processing JSON-LD with multiple namespaces."""
        transform_namespace = get_schema_namespace("transform")
        input_jsonld = {
            "@context": {
                "tr": transform_namespace,
                "other": "https://example.com/other/",
            },
            "tr:translation": [1, 2, 3],
            "tr:scale": [2.0, 1.5],
            "other:metadata": "some_value",
        }

        result = from_jsonld(input_jsonld)

        # Should process transforms and preserve other data
        transform_count = 0
        for key, value in result.items():
            if isinstance(value, Translation | Scale):
                transform_count += 1
            elif key == "other:metadata":
                assert value == "some_value"

        assert transform_count == 2, "Should have processed 2 transforms"

    def test_enhanced_serialization(self):
        """Test enhanced serialization with optimal abbreviations."""
        transforms = {
            "my_translation": translation([10, 20, 30]),
            "my_scale": scale([2.0, 1.5, 0.5]),
            "metadata": "preserved",
        }

        result = to_jsonld(transforms, include_context=True, indent=None)

        # Should be a dictionary with context and clean abbreviations
        assert isinstance(result, dict)
        if "@context" in result:
            context = result["@context"]
            # Should have some abbreviation for transform namespace
            assert any("transform" in str(v) for v in context.values())

        # Should have serialized transforms with abbreviated keys
        transform_keys = [
            k for k in result.keys() if k != "@context" and k != "metadata"
        ]
        assert len(transform_keys) == 2  # 2 transforms

        # Metadata should be preserved
        assert result.get("metadata") == "preserved"

        # Validate JSON-LD specification compliance
        assert validate_jsonld_spec(result)

    def test_to_jsonld_single_object(self):
        """Test serialization of a single object."""
        trans = translation([10, 20, 30])
        result = to_jsonld(trans, include_context=True)

        # Should be a dictionary containing the single object
        assert isinstance(result, dict)
        assert "@context" in result

        # Should have one transform with a key derived from the object
        transform_keys = [k for k in result.keys() if k != "@context"]
        assert len(transform_keys) == 1

        # The value should be the serialized transform
        for key in transform_keys:
            serialized_data = result[key]
            assert isinstance(serialized_data, dict)
            if hasattr(trans, "to_dict"):
                expected = trans.to_dict()
                assert serialized_data == expected

        # Validate JSON-LD specification compliance
        assert validate_jsonld_spec(result)

    def test_to_jsonld_list_uses_at_list(self):
        """Test that lists are serialized using JSON-LD @list construct."""
        transforms = [
            translation([10, 20, 30]),
            scale([2.0, 1.5, 0.5]),
            identity(),
        ]

        result = to_jsonld(transforms, include_context=True)

        # Should be a dictionary with @context and @list
        assert isinstance(result, dict)
        assert "@context" in result
        assert "@list" in result

        # The @list should contain the serialized transforms
        transform_list = result["@list"]
        assert isinstance(transform_list, list)
        assert len(transform_list) == 3

        # Each item should be properly serialized
        for i, (original, serialized) in enumerate(
            zip(transforms, transform_list, strict=False)
        ):
            if hasattr(original, "to_dict"):
                expected = original.to_dict()
                assert serialized == expected

        # Validate JSON-LD specification compliance
        assert validate_jsonld_spec(result)

    def test_to_jsonld_tuple_uses_at_list(self):
        """Test that tuples are serialized using JSON-LD @list construct."""
        transforms = (
            translation([10, 20, 30]),
            scale([2.0, 1.5, 0.5]),
        )

        result = to_jsonld(transforms, include_context=True)

        # Should be a dictionary with @context and @list
        assert isinstance(result, dict)
        assert "@context" in result
        assert "@list" in result

        # The @list should contain the serialized transforms
        transform_list = result["@list"]
        assert isinstance(transform_list, list)
        assert len(transform_list) == 2

        # Validate JSON-LD specification compliance
        assert validate_jsonld_spec(result)

    def test_to_jsonld_empty_list_uses_at_list(self):
        """Test that empty lists are serialized using JSON-LD @list construct."""
        transforms = []

        result = to_jsonld(transforms, include_context=False)

        # Should be a dictionary with empty @list
        assert isinstance(result, dict)
        assert "@list" in result
        assert result["@list"] == []
        # Should not have @context for empty list when include_context=False
        assert "@context" not in result

        # Validate JSON-LD specification compliance
        assert validate_jsonld_spec(result)

    def test_to_jsonld_dict_preserves_keys(self):
        """Test that dictionaries preserve their original key structure."""
        transforms = {
            "my_translation": translation([10, 20, 30]),
            "my_scale": scale([2.0, 1.5, 0.5]),
            "metadata": "preserved",
        }

        result = to_jsonld(transforms, include_context=True)

        # Should be a dictionary with context and original structure
        assert isinstance(result, dict)
        assert "@context" in result

        # Should NOT use @list for dictionaries
        assert "@list" not in result

        # Should preserve metadata
        assert result.get("metadata") == "preserved"

        # Validate JSON-LD specification compliance
        assert validate_jsonld_spec(result)

    def test_to_jsonld_list_without_context(self):
        """Test list serialization without including context."""
        transforms = [
            translation([10, 20, 30]),
            scale([2.0, 1.5, 0.5]),
        ]

        result = to_jsonld(transforms, include_context=False)

        # Should use @list but not include @context
        assert isinstance(result, dict)
        assert "@list" in result
        assert "@context" not in result

        # The @list should contain the serialized transforms
        transform_list = result["@list"]
        assert len(transform_list) == 2

        # Validate JSON-LD specification compliance
        assert validate_jsonld_spec(result)

    def test_to_jsonld_list_preserves_order(self):
        """Test that @list preserves order according to JSON-LD specification."""
        # Create transforms with different values to test ordering
        transforms = [
            translation([10, 20, 30]),
            translation([40, 50, 60]),
            translation([70, 80, 90]),
        ]

        result = to_jsonld(transforms, include_context=False)

        # Should use @list
        assert "@list" in result
        transform_list = result["@list"]
        assert len(transform_list) == 3

        # Order should be preserved
        expected_translations = [[10, 20, 30], [40, 50, 60], [70, 80, 90]]
        for i, (expected_trans, serialized) in enumerate(
            zip(expected_translations, transform_list, strict=False)
        ):
            # Compare the translation values
            assert serialized["translation"] == expected_trans

        # Validate JSON-LD specification compliance
        assert validate_jsonld_spec(result)

    def test_strict_validation(self):
        """Test strict validation requires all terms to be mappable."""

        # Test that unmappable terms raise clear errors
        invalid_cases = [
            {"translation": [1, 2, 3]},  # No context
            {
                "@context": {"tr": "https://example.com/"},
                "unmapped": [1, 2, 3],  # Term not in context
            },
            {},  # Empty document
            {"@context": {"tr": "https://example.com/"}},  # Only context
        ]

        for invalid_data in invalid_cases:
            with pytest.raises(
                ValueError, match="No expandable terms found|Document contains no data"
            ):
                from_jsonld(invalid_data)

        # Test that valid JSON-LD with proper mappings still works
        transform_namespace = get_schema_namespace("transform")
        valid_data = {
            "@context": {"tr": transform_namespace},
            "tr:translation": [1, 2, 3],
        }

        result = from_jsonld(valid_data)
        assert isinstance(result, dict)
        assert "@context" in result

        # Should have created a Translation object
        transform_found = any(isinstance(v, Translation) for v in result.values())
        assert transform_found, "Should have created a Translation object"

        # Legacy serialization still has its own behavior
        from noid_transforms.serialization import from_jsonld as legacy_from_jsonld

        legacy_result = legacy_from_jsonld(json.dumps({"translation": [1, 2, 3]}))
        assert isinstance(legacy_result, Translation)

    def test_jsonld_validation_catches_invalid_data(self):
        """Test that our validation function correctly identifies invalid JSON-LD."""

        # Test with invalid JSON-LD structure
        invalid_cases = [
            # Invalid @context structure
            {
                "@context": 123,
                "name": "test",
            },  # @context must be object, array, or string
            # Malformed IRI in context - this might be valid in some contexts
            # {"@context": {"test": "not-a-valid-iri:"}, "test": "value"},
        ]

        for invalid_data in invalid_cases:
            # This should return False for invalid JSON-LD
            assert not validate_jsonld_spec(invalid_data)

        # Test with valid JSON-LD to ensure our validation isn't too strict
        valid_data = {
            "@context": {"name": "http://schema.org/name"},
            "name": "Test Person",
        }
        assert validate_jsonld_spec(valid_data)


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_batch_transform_processing(self):
        """Test processing multiple transforms in batch."""
        transforms_data = [
            {"translation": [10, 20, 30]},
            {"scale": [2.0, 1.5, 0.5]},
            "identity",
            {"translation": [5, 10, 15]},
        ]

        results = []
        for transform_data in transforms_data:
            result = from_dict(transform_data)
            results.append(result)

        # Check results
        assert len(results) == 4
        assert isinstance(results[0], Translation)
        assert isinstance(results[1], Scale)
        assert isinstance(results[2], Identity)
        assert isinstance(results[3], Translation)

        # Check values
        assert results[0].translation == [10, 20, 30]
        assert results[1].scale == [2.0, 1.5, 0.5]
        assert results[3].translation == [5, 10, 15]

    def test_error_handling_in_batch(self):
        """Test error handling when processing multiple transforms."""
        transforms_data = [
            {"translation": [1, 2, 3]},  # Valid
            {"unknown_transform": [1, 2, 3]},  # Invalid
            {"scale": [2.0, 1.5]},  # Valid
        ]

        results = []
        errors = []

        for transform_data in transforms_data:
            try:
                result = from_dict(transform_data)
                results.append(result)
            except ValueError as e:
                errors.append(str(e))

        # Should have 2 successful results and 1 error
        assert len(results) == 2
        assert len(errors) == 1

        # Check that error has clean message
        assert "unknown_transform" in errors[0]
        assert "Unknown transform type" in errors[0]

    def test_mixed_data_processing(self):
        """Test processing JSON-LD with mixed transform and non-transform data."""
        transform_namespace = get_schema_namespace("transform")
        mixed_jsonld = {
            "@context": {
                "tr": transform_namespace,
                "meta": "https://example.com/metadata/",
            },
            "tr:translation": [1, 2, 3],
            "meta:title": "My Dataset",
            "meta:description": "A sample dataset with transforms",
            "tr:scale": [2.0, 1.5],
            "version": "1.0",
            "tags": ["transform", "geometry"],
        }

        result = from_jsonld(mixed_jsonld)

        # Should preserve all data
        assert "@context" in result
        assert result.get("meta:title") == "My Dataset"
        assert result.get("meta:description") == "A sample dataset with transforms"
        assert result.get("version") == "1.0"
        assert result.get("tags") == ["transform", "geometry"]

        # Should process transforms
        transform_count = sum(
            1 for v in result.values() if isinstance(v, Translation | Scale)
        )
        assert transform_count == 2


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling."""

    def test_large_batch_processing(self):
        """Test processing a large number of transforms."""
        # Create 100 transforms
        large_batch = []
        for i in range(100):
            if i % 3 == 0:
                large_batch.append({"translation": [i, i + 1, i + 2]})
            elif i % 3 == 1:
                large_batch.append({"scale": [1.0 + i * 0.1, 1.5 + i * 0.1]})
            else:
                large_batch.append("identity")

        # Process all transforms
        results = []
        for transform_data in large_batch:
            result = from_dict(transform_data)
            results.append(result)

        # Verify results
        assert len(results) == 100

        # Check type distribution
        translation_count = sum(1 for r in results if isinstance(r, Translation))
        scale_count = sum(1 for r in results if isinstance(r, Scale))
        identity_count = sum(1 for r in results if isinstance(r, Identity))

        assert translation_count + scale_count + identity_count == 100
        # Should be roughly evenly distributed
        assert translation_count >= 30 and translation_count <= 40
        assert scale_count >= 30 and scale_count <= 40
        assert identity_count >= 20 and identity_count <= 40


if __name__ == "__main__":
    pytest.main([__file__])
