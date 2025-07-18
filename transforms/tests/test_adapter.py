"""
Tests for the PyLD data adapter.

This module tests the PyLD data normalization functionality that converts
PyLD expansion output to clean Python data structures.
"""

import pytest

from noid_transforms.adapter import PyLDDataAdapter


class TestPyLDDataAdapter:
    """Test PyLD data normalization."""

    def setup_method(self):
        """Set up test environment."""
        self.adapter = PyLDDataAdapter()

    def test_simple_array_normalization(self):
        """Test normalization of simple array data."""
        # PyLD wraps array values in @value objects
        pyld_array = [{"@value": 10}, {"@value": 20}, {"@value": 30}]

        result = self.adapter.normalize(pyld_array)
        assert result == [10, 20, 30]

    def test_scalar_normalization(self):
        """Test normalization of scalar data (unwrapped from array)."""
        # PyLD wraps even scalars in arrays
        pyld_scalar = [{"@value": "linear"}]

        result = self.adapter.normalize(pyld_scalar)
        assert result == "linear"

    def test_typed_value_normalization(self):
        """Test normalization of typed literal values."""
        test_cases = [
            # Float values
            (
                [{"@value": "10.5", "@type": "http://www.w3.org/2001/XMLSchema#float"}],
                10.5,
            ),
            (
                [
                    {
                        "@value": "3.14159",
                        "@type": "http://www.w3.org/2001/XMLSchema#double",
                    }
                ],
                3.14159,
            ),
            (
                [
                    {
                        "@value": "2.71828",
                        "@type": "http://www.w3.org/2001/XMLSchema#decimal",
                    }
                ],
                2.71828,
            ),
            # Integer values
            (
                [{"@value": "42", "@type": "http://www.w3.org/2001/XMLSchema#integer"}],
                42,
            ),
            ([{"@value": "100", "@type": "http://www.w3.org/2001/XMLSchema#int"}], 100),
            (
                [{"@value": "999", "@type": "http://www.w3.org/2001/XMLSchema#long"}],
                999,
            ),
            # Boolean values
            (
                [
                    {
                        "@value": "true",
                        "@type": "http://www.w3.org/2001/XMLSchema#boolean",
                    }
                ],
                True,
            ),
            (
                [
                    {
                        "@value": "false",
                        "@type": "http://www.w3.org/2001/XMLSchema#boolean",
                    }
                ],
                False,
            ),
            (
                [{"@value": "1", "@type": "http://www.w3.org/2001/XMLSchema#boolean"}],
                True,
            ),
            # String values
            (
                [
                    {
                        "@value": "hello",
                        "@type": "http://www.w3.org/2001/XMLSchema#string",
                    }
                ],
                "hello",
            ),
        ]

        for pyld_input, expected in test_cases:
            result = self.adapter.normalize(pyld_input)
            assert result == expected, f"Failed for input {pyld_input}"

    def test_mixed_array_normalization(self):
        """Test normalization of arrays with mixed @value and regular objects."""
        pyld_mixed = [
            {"@value": 10},
            {"@value": 20},
            {"some_key": "regular_value"},  # Not a @value object
        ]

        result = self.adapter.normalize(pyld_mixed)
        # Should normalize recursively
        expected = [10, 20, {"some_key": "regular_value"}]
        assert result == expected

    def test_nested_object_normalization(self):
        """Test normalization of nested complex objects."""
        pyld_nested = {
            "array_field": [{"@value": 1}, {"@value": 2}],
            "scalar_field": [{"@value": "test"}],
            "regular_field": "unchanged",
        }

        result = self.adapter.normalize(pyld_nested)
        expected = {
            "array_field": [1, 2],
            "scalar_field": "test",
            "regular_field": "unchanged",
        }
        assert result == expected

    def test_single_value_object_normalization(self):
        """Test normalization of single @value object (defensive case)."""
        pyld_single = {"@value": 42}

        result = self.adapter.normalize(pyld_single)
        assert result == 42

    def test_unknown_type_passthrough(self):
        """Test that unknown types are passed through unchanged."""
        pyld_unknown = [{"@value": "test", "@type": "http://unknown.com/custom"}]

        result = self.adapter.normalize(pyld_unknown)
        assert result == "test"  # Value extracted but not converted

    def test_non_pyld_passthrough(self):
        """Test that non-PyLD data is passed through unchanged."""
        test_cases = [
            "regular_string",
            42,
            3.14,
            True,
            None,
            [1, 2, 3],
            {"key": "value"},
        ]

        for test_input in test_cases:
            result = self.adapter.normalize(test_input)
            assert result == test_input

    def test_empty_array_normalization(self):
        """Test normalization of empty arrays."""
        result = self.adapter.normalize([])
        assert result == []

    def test_complex_nested_structure(self):
        """Test normalization of complex nested structure."""
        pyld_complex = {
            "transforms": [
                {"translation": [{"@value": 10}, {"@value": 20}, {"@value": 30}]},
                {"scale": [{"@value": 2.0}, {"@value": 1.5}]},
            ],
            "metadata": {
                "interpolation": [{"@value": "linear"}],
                "created": [
                    {
                        "@value": "2023-01-01",
                        "@type": "http://www.w3.org/2001/XMLSchema#string",
                    }
                ],
            },
        }

        result = self.adapter.normalize(pyld_complex)
        expected = {
            "transforms": [{"translation": [10, 20, 30]}, {"scale": [2.0, 1.5]}],
            "metadata": {"interpolation": "linear", "created": "2023-01-01"},
        }
        assert result == expected


class TestPyLDDetection:
    """Test PyLD format detection."""

    def setup_method(self):
        self.adapter = PyLDDataAdapter()

    def test_pyld_expanded_detection_array(self):
        """Test detection of PyLD expanded array format."""
        pyld_array = [{"@value": 1}, {"@value": 2}]
        assert self.adapter.is_pyld_expanded(pyld_array) is True

        # Mixed array should return False
        mixed_array = [{"@value": 1}, {"other": 2}]
        assert self.adapter.is_pyld_expanded(mixed_array) is False

        # Regular array should return False
        regular_array = [1, 2, 3]
        assert self.adapter.is_pyld_expanded(regular_array) is False

    def test_pyld_expanded_detection_object(self):
        """Test detection of PyLD expanded object format."""
        pyld_object = {"@value": 42}
        assert self.adapter.is_pyld_expanded(pyld_object) is True

        # Regular object should return False
        regular_object = {"key": "value"}
        assert self.adapter.is_pyld_expanded(regular_object) is False

    def test_pyld_expanded_detection_primitives(self):
        """Test detection for primitive values."""
        primitives = ["string", 42, 3.14, True, None]

        for primitive in primitives:
            assert self.adapter.is_pyld_expanded(primitive) is False


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        self.adapter = PyLDDataAdapter()

    def test_malformed_value_object(self):
        """Test handling of malformed @value objects."""
        # Missing @value key
        malformed = [{"@type": "http://www.w3.org/2001/XMLSchema#string"}]

        # Should not crash, should pass through as-is or handle gracefully
        result = self.adapter.normalize(malformed)
        # The exact behavior depends on implementation, but it shouldn't crash
        assert result is not None

    def test_none_values_in_array(self):
        """Test handling of None values in arrays."""
        pyld_with_none = [{"@value": 1}, None, {"@value": 2}]

        result = self.adapter.normalize(pyld_with_none)
        # Should handle gracefully - might normalize the @value objects and pass None through
        assert isinstance(result, list)
        assert len(result) == 3

    def test_deeply_nested_structure(self):
        """Test handling of deeply nested structures."""
        deep_structure = {
            "level1": {"level2": {"level3": {"values": [{"@value": 1}, {"@value": 2}]}}}
        }

        result = self.adapter.normalize(deep_structure)
        assert result["level1"]["level2"]["level3"]["values"] == [1, 2]

    def test_boolean_string_variations(self):
        """Test various string representations of booleans."""
        boolean_cases = [
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("false", False),
            ("FALSE", False),
            ("False", False),
            ("1", True),
            ("0", False),
        ]

        for input_str, expected in boolean_cases:
            pyld_bool = [
                {
                    "@value": input_str,
                    "@type": "http://www.w3.org/2001/XMLSchema#boolean",
                }
            ]
            result = self.adapter.normalize(pyld_bool)
            assert result == expected, f"Failed for boolean string '{input_str}'"


if __name__ == "__main__":
    pytest.main([__file__])
