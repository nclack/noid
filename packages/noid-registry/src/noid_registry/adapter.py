"""
PyLD data normalization adapter.

This module provides utilities for normalizing PyLD JSON-LD expansion output
into clean Python data structures suitable for factory functions. It's designed
to be schema-agnostic and extractable as part of a standalone library.

PyLD expansion wraps all values in @value objects and arrays:
- [10, 20, 30] → [{"@value": 10}, {"@value": 20}, {"@value": 30}]
- "linear" → [{"@value": "linear"}]
- 42 → [{"@value": 42}]

This adapter unwraps these structures back to clean Python data.
"""

from typing import Any


class PyLDDataAdapter:
    """Normalize PyLD expanded data before passing to factory functions.

    PyLD expansion wraps all values in @value objects and arrays. This adapter
    converts that back to clean Python data structures that factory functions expect.
    """

    def normalize(self, data: Any) -> Any:
        """Convert PyLD expansion output to clean factory input.

        Args:
            data: Output from PyLD expand() operation

        Returns:
            Normalized Python data suitable for factory functions

        Examples:
            # Array normalization
            >>> adapter = PyLDDataAdapter()
            >>> pyld_array = [{"@value": 10}, {"@value": 20}, {"@value": 30}]
            >>> adapter.normalize(pyld_array)
            [10, 20, 30]

            # Scalar normalization (PyLD wraps scalars in arrays)
            >>> pyld_scalar = [{"@value": "linear"}]
            >>> adapter.normalize(pyld_scalar)
            'linear'

            # Typed value normalization
            >>> pyld_typed = [{"@value": "10.5", "@type": "http://www.w3.org/2001/XMLSchema#float"}]
            >>> adapter.normalize(pyld_typed)
            10.5
        """
        # PyLD always returns arrays, even for scalars
        if isinstance(data, list):
            # Handle array of @value objects: [{"@value": 10}, {"@value": 20}] → [10, 20]
            if all(isinstance(item, dict) and "@value" in item for item in data):
                normalized_items = [self._extract_value(item) for item in data]

                # If single item, unwrap from array (scalar case)
                if len(normalized_items) == 1:
                    return normalized_items[0]
                return normalized_items

            # Handle mixed or complex arrays (recursively normalize)
            return [self.normalize(item) for item in data]

        # Handle single @value object (defensive - shouldn't happen with PyLD but possible)
        if isinstance(data, dict) and "@value" in data:
            return self._extract_value(data)

        # Handle complex objects (recursively normalize)
        if isinstance(data, dict):
            return {key: self.normalize(value) for key, value in data.items()}

        # Pass through other values (strings, numbers, booleans, None)
        return data

    def _extract_value(self, item: dict[str, Any]) -> Any:
        """Extract value from @value wrapper, handling type conversion.

        Args:
            item: PyLD @value object (e.g., {"@value": "10.5", "@type": "xsd:float"})

        Returns:
            Extracted and type-converted value
        """
        value = item["@value"]

        # Handle typed values with conversion
        if "@type" in item:
            type_iri = item["@type"]
            return self._convert_typed_value(value, type_iri)

        return value

    def _convert_typed_value(self, value: Any, type_iri: str) -> Any:
        """Convert typed literals to appropriate Python types.

        Args:
            value: String value from @value
            type_iri: Type IRI from @type

        Returns:
            Value converted to appropriate Python type
        """
        # Convert based on XML Schema type IRI
        match type_iri:
            case (
                "http://www.w3.org/2001/XMLSchema#float"
                | "http://www.w3.org/2001/XMLSchema#double"
                | "http://www.w3.org/2001/XMLSchema#decimal"
            ):
                return float(value)
            case (
                "http://www.w3.org/2001/XMLSchema#integer"
                | "http://www.w3.org/2001/XMLSchema#int"
                | "http://www.w3.org/2001/XMLSchema#long"
            ):
                return int(value)
            case "http://www.w3.org/2001/XMLSchema#boolean":
                return str(value).lower() in ("true", "1")
            case "http://www.w3.org/2001/XMLSchema#string":
                return str(value)
            case _:
                # Default passthrough for unknown types
                return value

    def is_pyld_expanded(self, data: Any) -> bool:
        """Check if data appears to be PyLD expanded format.

        Args:
            data: Data to check

        Returns:
            True if data looks like PyLD expanded format
        """
        if isinstance(data, list):
            return all(isinstance(item, dict) and "@value" in item for item in data)

        if isinstance(data, dict):
            return "@value" in data

        return False
