"""
Enhanced JSON-LD processing with PyLD integration.

This module provides sophisticated JSON-LD processing that preserves original key names,
uses PyLD expansion for IRI resolution, and integrates with a registry system for
extensible object creation.
"""

from collections.abc import Sequence
import json
import logging
from typing import Any

from pyld import jsonld

from .adapter import PyLDDataAdapter
from .registry import registry


def from_jsonld(jsonld_data: dict[str, Any] | str) -> dict[str, Any] | Any:
    """Process JSON-LD with strict validation and registry-based object creation.

    This function supports two patterns:
    1. Single object with @type at root: Returns the created object directly
    2. Property-based structure: Returns dict with original keys mapped to objects

    All terms must be properly mapped to IRIs in the @context.
    Uses PyLD expansion for IRI resolution and the registry system for object creation.

    Args:
        jsonld_data: JSON-LD document (dict) or JSON-LD string

    Returns:
        Single object (if @type at root) or dictionary with original keys mapped to objects

    Raises:
        ValueError: If terms cannot be mapped to IRIs or document is empty

    Examples:
        >>> # Single object with @type at root
        >>> jsonld_doc = {
        ...     "@context": {"spac": "https://github.com/nclack/noid/schemas/space/"},
        ...     "@type": "spac:dimension",
        ...     "id": "x",
        ...     "unit": "m"
        ... }
        >>> result = from_jsonld(jsonld_doc)
        >>> # Returns: Dimension(id="x", unit="m")  # if registered

        >>> # Property-based structure
        >>> jsonld_doc = {
        ...     "@context": {
        ...         "example": "https://example.com/schemas/"
        ...     },
        ...     "example:widget": {"name": "my_widget", "value": 42},
        ...     "other_data": "preserved"
        ... }
        >>> result = from_jsonld(jsonld_doc)
        >>> # Returns: {
        >>> #   "@context": {...},
        >>> #   "example:widget": Widget(name="my_widget", value=42),  # if registered
        >>> #   "other_data": "preserved"
        >>> # }
    """
    # Parse JSON string if needed
    if isinstance(jsonld_data, str):
        jsonld_data = json.loads(jsonld_data)

    if not isinstance(jsonld_data, dict):
        raise ValueError("JSON-LD data must be a dictionary")

    # Check for single object pattern (@type at root)
    if "@type" in jsonld_data:
        return _handle_single_object_from_jsonld(jsonld_data)

    # Property-based pattern - original logic
    return _handle_property_based_from_jsonld(jsonld_data)


def _handle_single_object_from_jsonld(jsonld_data: dict[str, Any]) -> Any:
    """Handle JSON-LD document with @type at root - creates single object.

    Args:
        jsonld_data: JSON-LD document with @type field

    Returns:
        Created object from registry

    Raises:
        ValueError: If @type cannot be expanded to IRI
    """
    # Expand to get full IRI for @type
    expanded = jsonld.expand(jsonld_data)

    if not expanded or not isinstance(expanded[0], dict):
        raise ValueError("Failed to expand JSON-LD document")

    expanded_item = expanded[0]
    type_iri = expanded_item.get("@type")

    if not type_iri:
        raise ValueError("No @type found in expanded document")

    # Handle case where @type is a list (take first one)
    if isinstance(type_iri, list):
        type_iri = type_iri[0]


    # Extract data for object creation from original document
    # (unprefixed properties won't be in expanded form)
    data = {}
    for key, value in jsonld_data.items():
        if key not in ("@context", "@type", "@id"):
            data[key] = value

    # Initialize adapter for PyLD data normalization
    adapter = PyLDDataAdapter()
    normalized_data = adapter.normalize(data)

    # Create object using registry
    try:
        return registry.create(type_iri, normalized_data)
    except Exception as e:
        logging.warning(f"Failed to create object for type IRI '{type_iri}': {e}")
        raise


def _handle_property_based_from_jsonld(jsonld_data: dict[str, Any]) -> dict[str, Any]:
    """Handle JSON-LD document with property-based structure - original logic.

    Args:
        jsonld_data: JSON-LD document with properties mapped to objects

    Returns:
        Dictionary with original keys mapped to registered objects and preserved context
    """
    # PyLD expansion (handles @context → full IRIs)
    expanded = jsonld.expand(jsonld_data)

    if not expanded:
        # Strict validation - all terms must be mappable to IRIs
        unmappable_terms = [k for k in jsonld_data.keys() if not k.startswith("@")]
        if not unmappable_terms:
            # Empty document or only @context - this is considered an error in strict mode
            raise ValueError("Document contains no data")
        raise ValueError(
            f"No expandable terms found. All terms must be mapped to IRIs in @context. "
            f"Unmappable terms: {unmappable_terms}"
        )

    # Initialize adapter for PyLD data normalization
    adapter = PyLDDataAdapter()

    # Process expanded data
    result = {}

    # Preserve original context
    if "@context" in jsonld_data:
        result["@context"] = jsonld_data["@context"]

    # Get context for IRI-to-key conversion
    context = jsonld_data.get("@context", {})
    processed_original_keys = set()

    # Process each expanded item
    for expanded_item in expanded:
        if not isinstance(expanded_item, dict):
            continue

        for iri, raw_value in expanded_item.items():
            if iri.startswith("@"):
                continue  # Skip JSON-LD keywords

            # Convert IRI back to short key using context
            short_key = _iri_to_short_key(iri, context)
            processed_original_keys.add(short_key)

            # Get original data from the source document (expanded may lose unnamespaced properties)
            original_data = jsonld_data.get(short_key, raw_value)

            # Normalize data before dispatch
            normalized_data = adapter.normalize(original_data)

            # Try registry dispatch with adapter
            try:
                registry_obj = registry.create(iri, normalized_data)
                result[short_key] = registry_obj
            except Exception as e:
                # Unknown object type or registry creation failed - pass through normalized data
                logging.warning(
                    f"Failed to create object for IRI '{iri}' (key: '{short_key}'): {e}. "
                    f"Passing through normalized data."
                )
                result[short_key] = normalized_data

    # Preserve any original data that wasn't expanded (no namespace mapping)
    for key, value in jsonld_data.items():
        if key not in processed_original_keys and not key.startswith("@"):
            result[key] = value

    return result


def _iri_to_short_key(iri: str, context: dict[str, Any]) -> str:
    """Convert full IRI back to short key using context.

    Args:
        iri: Full IRI
        context: JSON-LD context for abbreviation

    Returns:
        Short key name

    Example:
        >>> context = {"example": "https://example.com/schemas/"}
        >>> _iri_to_short_key("https://example.com/schemas/widget", context)
        'example:widget'
    """
    # Try to find a prefix in context that matches the IRI namespace
    for prefix, namespace in context.items():
        if isinstance(namespace, str) and iri.startswith(namespace):
            local_name = iri[len(namespace) :]
            return f"{prefix}:{local_name}"

    # Fallback to just the local name
    # Split on last occurrence of / or #
    for delimiter in ["/", "#"]:
        if delimiter in iri:
            return iri.split(delimiter)[-1]

    # No delimiter found - return the whole IRI
    return iri


def _create_context_for_objects(
    data_dict: dict[str, Any],
) -> tuple[dict[str, str], Any]:
    """Extract namespaces from objects and create context with abbreviations.

    Args:
        data_dict: Dictionary of objects to extract namespaces from

    Returns:
        Tuple of (context_dict, abbreviator_instance)
    """
    from .abbreviation import (
        create_abbreviator_for_namespaces,
        extract_namespaces_from_objects,
    )

    namespaces = extract_namespaces_from_objects(data_dict)
    abbreviator = create_abbreviator_for_namespaces(namespaces) if namespaces else None

    # Build context with abbreviations
    context = {}
    if abbreviator:
        for abbrev, namespace in abbreviator.get_all_abbreviations().items():
            context[abbrev] = namespace

    return context, abbreviator


def _handle_sequence_serialization(
    data: Sequence[Any], context: dict[str, str], indent: int | None
) -> str | dict[str, Any]:
    """Handle serialization of sequences (lists/tuples) using JSON-LD @list construct.

    Args:
        data: List or tuple of objects to serialize
        context: Pre-built context dictionary to include
        indent: Optional indentation for JSON formatting

    Returns:
        JSON-LD string or dictionary with @list structure
    """
    # Serialize each item in the list
    serialized_items = []
    for item in data:
        if hasattr(item, "to_data"):
            serialized_items.append(item.to_data())
        else:
            serialized_items.append(item)

    # Create JSON-LD list structure
    result = {"@list": serialized_items}

    # Add context if provided
    if context:
        result["@context"] = context

    return json.dumps(result, indent=indent) if indent is not None else result


def _convert_single_object_to_dict(data: Any) -> dict[str, Any]:
    """Convert a single object to a dictionary with key based on object's IRI.

    Args:
        data: Single object to convert

    Returns:
        Dictionary with the object as a value
    """
    from .registry import registry

    iri = registry.get_iri_for_object(data)
    if iri:
        # Extract local name from IRI for the key
        local_name = (
            iri.split("/")[-1]
            if "/" in iri
            else iri.split("#")[-1]
            if "#" in iri
            else iri
        )
        return {local_name: data}
    else:
        # Unknown object type - use generic key
        return {"item": data}


def _get_abbreviated_key_for_object(original_key: str, obj: Any, abbreviator) -> str:
    """Determine abbreviated key name for an object using namespace prefixes.

    Args:
        original_key: Original key name
        obj: Object to get key for
        abbreviator: Abbreviator instance for creating namespace prefixes

    Returns:
        Abbreviated key name (e.g., "ex:widget" instead of full IRI)
    """
    from .registry import registry

    abbreviated_key = original_key  # Default fallback
    if abbreviator:
        iri = registry.get_iri_for_object(obj)
        if iri:
            # Extract local name from IRI and create abbreviated key with namespace prefix
            namespace = _extract_namespace_from_iri(iri)
            local_name = iri[len(namespace) :]
            abbrev = abbreviator.get_abbreviation(namespace)
            abbreviated_key = f"{abbrev}:{local_name}"

    return abbreviated_key


def _serialize_dict_objects(
    data_dict: dict[str, Any],
    include_context: bool,
    context: dict[str, str],
    abbreviator,
) -> dict[str, Any]:
    """Serialize dictionary of objects with abbreviated namespace-prefixed keys.

    Args:
        data_dict: Dictionary of objects to serialize
        include_context: Whether to include @context in output
        context: Context dictionary for abbreviations
        abbreviator: Abbreviator instance for creating namespace prefixes

    Returns:
        Serialized result dictionary
    """
    result = {}

    if include_context and context:
        result["@context"] = context

    for original_key, obj in data_dict.items():
        if original_key == "@context":
            if include_context and not context:
                # Preserve existing context if we don't have new abbreviations
                result["@context"] = obj
            continue

        # Determine abbreviated key name
        abbreviated_key = _get_abbreviated_key_for_object(
            original_key, obj, abbreviator
        )

        # Serialize the object
        if hasattr(obj, "to_data"):
            result[abbreviated_key] = obj.to_data()
        else:
            result[abbreviated_key] = obj

    return result


def to_jsonld(
    data: Any | Sequence[Any] | dict[str, Any],
    include_context: bool = True,
    indent: int | None = None,
) -> str | dict[str, Any]:
    """Serialize objects to clean JSON-LD with optimal per-call abbreviations.

    This function extracts namespaces from the objects, creates optimal
    abbreviations for this specific serialization, and produces clean JSON-LD output.

    Lists and tuples are serialized using the JSON-LD @list construct to preserve
    order according to the JSON-LD specification.

    Args:
        data: Object, list of objects, or dict of objects to serialize
        include_context: Whether to include @context in output
        indent: Optional indentation for JSON formatting

    Returns:
        JSON-LD string or dictionary with clean abbreviations and serialized objects

    Examples:
        >>> # Single object (assuming appropriate registry entries)
        >>> obj = SomeRegisteredClass(param="value")
        >>> result = to_jsonld(obj)

        >>> # Dictionary of objects
        >>> objects = {
        ...     "my_widget": Widget(name="test"),
        ...     "my_config": Config(setting="enabled")
        ... }
        >>> result = to_jsonld(objects)
        >>> # Returns JSON-LD with abbreviated namespace-prefixed keys:
        >>> # {
        >>> #   "@context": {"ex": "https://example.com/schemas/"},
        >>> #   "ex:widget": {"name": "test"},
        >>> #   "ex:config": {"setting": "enabled"}
        >>> # }

        >>> # List of objects (uses JSON-LD @list construct)
        >>> objects = [Widget(name="test1"), Widget(name="test2")]
        >>> result = to_jsonld(objects)
        >>> # Returns:
        >>> # {
        >>> #   "@context": {"ex": "https://example.com/schemas/"},
        >>> #   "@list": [{"name": "test1"}, {"name": "test2"}]
        >>> # }
    """
    # Handle sequences - create context and delegate serialization
    if isinstance(data, list | tuple):
        if include_context:
            # Create temporary dict for namespace extraction
            temp_dict = {f"item_{i}": item for i, item in enumerate(data)}
            context, _ = _create_context_for_objects(temp_dict)
        else:
            context = {}
        return _handle_sequence_serialization(data, context, indent)

    # Convert input to dictionary format
    if isinstance(data, dict):
        data_dict = data
    else:
        # Single object - create a dictionary with key based on object's IRI
        data_dict = _convert_single_object_to_dict(data)

    # Early return for simple serialization case
    if not include_context:
        result = {}
        for key, obj in data_dict.items():
            if key == "@context":
                continue
            if hasattr(obj, "to_data"):
                result[key] = obj.to_data()
            else:
                result[key] = obj
        return json.dumps(result, indent=indent) if indent is not None else result

    context, abbreviator = _create_context_for_objects(data_dict)
    result = _serialize_dict_objects(data_dict, include_context, context, abbreviator)

    # Return string or dict based on indent parameter
    return json.dumps(result, indent=indent) if indent is not None else result


def _extract_namespace_from_iri(iri: str) -> str:
    """Extract namespace from full IRI.

    Args:
        iri: Full IRI

    Returns:
        Namespace IRI

    Example:
        >>> _extract_namespace_from_iri("https://example.com/schemas/widget")
        'https://example.com/schemas/'
    """
    # Find the last occurrence of / or # to separate namespace from local name
    for delimiter in ["/", "#"]:
        if delimiter in iri:
            idx = iri.rfind(delimiter)
            return iri[: idx + 1]  # Include the delimiter

    # No delimiter found - the whole thing is the namespace
    return iri + "/"  # Add trailing slash
