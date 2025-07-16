"""
Serialization utilities for transform objects.

This module provides functions for serializing transform objects to various formats
including JSON, JSON-LD, and dictionary representations. It leverages the LinkML-generated
JSON-LD context for semantic serialization.
"""

import json
from pathlib import Path
from typing import Dict, List, Union, Any, Optional, Sequence, TypeAlias

from .models import Transform

# Type aliases for cleaner signatures
DictRepr: TypeAlias = Union[Dict[str, Any], str]

# Load the JSON-LD context
_context_path = Path(__file__).parent.parent.parent / "_out" / "transforms.context.jsonld"


def _load_jsonld_context() -> Dict[str, Any]:
    """Load the JSON-LD context from the generated file."""
    try:
        with open(_context_path, 'r') as f:
            context_data = json.load(f)
        return context_data.get("@context", {})
    except FileNotFoundError:
        raise FileNotFoundError(
            f"JSON-LD context file not found at {_context_path}. "
            "Please run 'python build.py' to generate the required files."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in context file: {e}")


def to_dict(transform: Union[Transform, Sequence[Transform]]) -> Union[DictRepr, List[DictRepr]]:
    """
    Convert a transform or sequence of transforms to dictionary representation.
    
    Args:
        transform: Transform object or list of transform objects to serialize
        
    Returns:
        Dictionary representation of the transform(s)
        
    Example:
        >>> from .factory import translation, identity
        >>> trans = translation([10, 20, 5])
        >>> to_dict(trans)
        {'translation': [10.0, 20.0, 5.0]}
        >>> 
        >>> sequence = [identity(), trans]
        >>> to_dict(sequence)
        ['identity', {'translation': [10.0, 20.0, 5.0]}]
    """
    if not isinstance(transform, Transform):
        return [t.to_dict() for t in transform]
    return transform.to_dict()


def to_json(transform: Union[Transform, Sequence[Transform]], indent: Optional[int] = None) -> str:
    """
    Convert a transform or sequence of transforms to JSON string.
    
    Args:
        transform: Transform object or list of transform objects to serialize
        indent: Optional indentation for pretty printing
        
    Returns:
        JSON string representation of the transform(s)
        
    Example:
        >>> from .factory import scale, identity
        >>> sc = scale([2.0, 1.5, 0.5])
        >>> to_json(sc)
        '{"scale": [2.0, 1.5, 0.5]}'
        >>> 
        >>> sequence = [identity(), sc]
        >>> to_json(sequence)
        '["identity", {"scale": [2.0, 1.5, 0.5]}]'
    """
    return json.dumps(to_dict(transform), indent=indent)


def to_jsonld(transform: Union[Transform, Sequence[Transform]], 
              include_context: bool = True,
              indent: Optional[int] = None) -> str:
    """
    Convert a transform or sequence of transforms to JSON-LD string with semantic context.
    
    Args:
        transform: Transform object or list of transform objects to serialize
        include_context: Whether to include @context in the output
        indent: Optional indentation for pretty printing
        
    Returns:
        JSON-LD string representation of the transform(s)
        
    Example:
        >>> from .factory import homogeneous, identity
        >>> matrix = [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
        >>> homo = homogeneous(matrix)
        >>> jsonld = to_jsonld(homo)
        >>> "@context" in jsonld
        True
        >>> 
        >>> sequence = [identity(), homo]
        >>> jsonld = to_jsonld(sequence)
        >>> "@context" in jsonld
        True
    """
    data = to_dict(transform)
    
    if include_context:
        context = _load_jsonld_context()
        if isinstance(data, list):
            # For sequences, wrap in a transforms container
            jsonld_data = {
                "@context": context,
                "transforms": data
            }
        elif isinstance(data, dict):
            jsonld_data = {
                "@context": context,
                **data
            }
        else:
            jsonld_data = {
                "@context": context,
                "@value": data
            }
    else:
        jsonld_data = data
    
    return json.dumps(jsonld_data, indent=indent)


def from_jsonld(jsonld_str: str) -> Transform:
    """
    Create a transform from JSON-LD string.
    
    Args:
        jsonld_str: JSON-LD string representation
        
    Returns:
        Transform object
        
    Raises:
        ValueError: If JSON-LD is invalid or transform format is unsupported
        
    Example:
        >>> jsonld = '{"@context": {}, "translation": [10, 20, 5]}'
        >>> trans = from_jsonld(jsonld)
        >>> trans.to_dict()
        {'translation': [10.0, 20.0, 5.0]}
    """
    from .factory import from_dict
    
    try:
        data = json.loads(jsonld_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON-LD: {e}")
    
    # Remove @context if present
    if "@context" in data:
        data = {k: v for k, v in data.items() if k != "@context"}
    
    # Handle @value wrapper for simple values
    if "@value" in data:
        return from_dict(data["@value"])
    
    return from_dict(data)


def serialize_sequence(transforms: Sequence[Transform], 
                      format: str = "json",
                      include_context: bool = True,
                      indent: Optional[int] = None) -> str:
    """
    Serialize a sequence of transforms to the specified format.
    
    Args:
        transforms: List of transform objects
        format: Output format ("json", "jsonld", or "dict")
        include_context: Whether to include @context in JSON-LD output
        indent: Optional indentation for pretty printing
        
    Returns:
        Serialized string representation
        
    Raises:
        ValueError: If format is unsupported
        
    Example:
        >>> from .factory import identity, translation
        >>> transforms = [identity(), translation([10, 20, 5])]
        >>> json_str = serialize_sequence(transforms, "json")
        >>> "identity" in json_str
        True
    """
    if format == "dict":
        return str([to_dict(t) for t in transforms])
    elif format == "json":
        return json.dumps([to_dict(t) for t in transforms], indent=indent)
    elif format == "jsonld":
        sequence_data = [to_dict(t) for t in transforms]
        
        if include_context:
            context = _load_jsonld_context()
            jsonld_data = {
                "@context": context,
                "transforms": sequence_data
            }
        else:
            jsonld_data = {"transforms": sequence_data}
        
        return json.dumps(jsonld_data, indent=indent)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json', 'jsonld', or 'dict'.")


def deserialize_sequence(data_str: str, format: str = "json") -> List[Transform]:
    """
    Deserialize a sequence of transforms from the specified format.
    
    Args:
        data_str: Serialized string representation
        format: Input format ("json" or "jsonld")
        
    Returns:
        List of transform objects
        
    Raises:
        ValueError: If format is unsupported or data is invalid
        
    Example:
        >>> json_str = '["identity", {"translation": [10, 20, 5]}]'
        >>> transforms = deserialize_sequence(json_str, "json")
        >>> len(transforms)
        2
    """
    from .factory import from_dict
    
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    
    if format == "json":
        if not isinstance(data, list):
            raise ValueError("JSON data must be a list for sequence deserialization")
        return [from_dict(item) for item in data]
    elif format == "jsonld":
        # Handle JSON-LD with @context
        if isinstance(data, dict):
            if "transforms" in data:
                sequence_data = data["transforms"]
            else:
                # Single transform in JSON-LD format
                sequence_data = [data]
        else:
            sequence_data = data
        
        if not isinstance(sequence_data, list):
            raise ValueError("JSON-LD data must contain a list of transforms")
        
        return [from_dict(item) for item in sequence_data]
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json' or 'jsonld'.")


def export_schema_context() -> Dict[str, Any]:
    """
    Export the LinkML-generated JSON-LD context.
    
    Returns:
        JSON-LD context dictionary
        
    Example:
        >>> context = export_schema_context()
        >>> "translation" in context
        True
    """
    return _load_jsonld_context()