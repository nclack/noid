"""
Factory functions for creating transform objects.

This module provides convenient factory functions for creating transform objects
from various input formats, including dictionaries, JSON, and direct parameters.
"""

import json
from typing import Dict, List, Union, Any, Optional, Sequence

from .models import (
    Transform,
    Identity,
    Translation,
    Scale,
    MapAxis,
    Homogeneous,
    DisplacementLookupTable,
    CoordinateLookupTable,
    SamplerConfig,
)


def identity() -> Identity:
    """
    Create an identity transform.
    
    Returns:
        Identity transform object
        
    Example:
        >>> identity = identity()
        >>> identity.to_dict()
        'identity'
    """
    return Identity()


def translation(translation: Union[Sequence[float], Sequence[int]]) -> Translation:
    """
    Create a translation transform.
    
    Args:
        translation: Translation vector as sequence of numbers (supports lists, tuples, numpy arrays)
        
    Returns:
        Translation transform object
        
    Raises:
        ValueError: If translation vector is empty (handled by model constructor)
        
    Example:
        >>> trans = translation([10, 20, 5])
        >>> trans.to_dict()
        {'translation': [10.0, 20.0, 5.0]}
        >>> trans = translation((10, 20, 5))  # tuples work
        >>> trans = translation(np.array([10, 20, 5]))  # numpy arrays work
    """
    return Translation(translation=translation)


def scale(scale: Union[Sequence[float], Sequence[int]]) -> Scale:
    """
    Create a scale transform.
    
    Args:
        scale: Scale factors as sequence of numbers (supports lists, tuples, numpy arrays)
        
    Returns:
        Scale transform object
        
    Raises:
        ValueError: If scale vector is empty or contains zeros (handled by model constructor)
        
    Example:
        >>> sc = scale([2.0, 1.5, 0.5])
        >>> sc.to_dict()
        {'scale': [2.0, 1.5, 0.5]}
        >>> sc = scale((2.0, 1.5, 0.5))  # tuples work
        >>> sc = scale(np.array([2.0, 1.5, 0.5]))  # numpy arrays work
    """
    return Scale(scale=scale)


def mapaxis(mapAxis: Union[Sequence[int], Sequence[int]]) -> MapAxis:
    """
    Create an axis mapping transform.
    
    Args:
        mapAxis: Permutation vector of 0-based input dimension indices (supports lists, tuples, numpy arrays)
        
    Returns:
        MapAxis transform object
        
    Raises:
        ValueError: If mapAxis is empty or contains invalid indices (handled by model constructor)
        
    Example:
        >>> ma = mapaxis([1, 0, 2])
        >>> ma.to_dict()
        {'mapAxis': [1, 0, 2]}
        >>> ma = mapaxis((1, 0, 2))  # tuples work
        >>> ma = mapaxis(np.array([1, 0, 2]))  # numpy arrays work
    """
    return MapAxis(mapAxis=mapAxis)


def homogeneous(matrix: Union[Sequence[Sequence[float]], Sequence[Sequence[int]], Sequence[float], Sequence[int]]) -> Homogeneous:
    """
    Create a homogeneous transformation matrix.
    
    Args:
        matrix: 2D transformation matrix or flat list (supports lists, tuples, numpy arrays)
        
    Returns:
        Homogeneous transform object
        
    Raises:
        ValueError: If matrix is empty, not rectangular, or invalid format (handled by model constructor)
        
    Example:
        >>> # 2D matrix format
        >>> matrix = [
        ...     [2.0, 0, 0, 10],
        ...     [0, 1.5, 0, 20],
        ...     [0, 0, 0.5, 5],
        ...     [0, 0, 0, 1]
        ... ]
        >>> homo = homogeneous(matrix)
        >>> homo.matrix_shape
        (4, 4)
        >>> 
        >>> # Flat list format
        >>> flat = [2.0, 0, 0, 10, 0, 1.5, 0, 20, 0, 0, 0.5, 5, 0, 0, 0, 1]
        >>> homo = homogeneous(flat)
        >>> 
        >>> # Works with numpy arrays
        >>> homo = homogeneous(np.array(matrix))
    """
    return Homogeneous(homogeneous=matrix)


def displacement_lookup(path: str, 
                              interpolation: Optional[str] = "nearest",
                              extrapolation: Optional[str] = "nearest") -> DisplacementLookupTable:
    """
    Create a displacement lookup table transform.
    
    Args:
        path: Path to displacement field data file
        interpolation: Interpolation method
        extrapolation: Extrapolation method
        
    Returns:
        DisplacementLookupTable transform object
        
    Example:
        >>> disp = displacement_lookup("path/to/field.zarr", "linear")
        >>> disp.path
        'path/to/field.zarr'
    """
    config = SamplerConfig(interpolation=interpolation, extrapolation=extrapolation)
    return DisplacementLookupTable(path=path, displacements=config)


def coordinate_lookup(path: str,
                           interpolation: Optional[str] = "nearest", 
                           extrapolation: Optional[str] = "nearest") -> CoordinateLookupTable:
    """
    Create a coordinate lookup table transform.
    
    Args:
        path: Path to coordinate lookup table data file
        interpolation: Interpolation method
        extrapolation: Extrapolation method
        
    Returns:
        CoordinateLookupTable transform object
        
    Example:
        >>> lookup = coordinate_lookup("path/to/lut.zarr", "linear")
        >>> lookup.path
        'path/to/lut.zarr'
    """
    config = SamplerConfig(interpolation=interpolation, extrapolation=extrapolation)
    return CoordinateLookupTable(path=path, lookup_table=config)


def from_dict(data: Union[Dict[str, Any], str]) -> Transform:
    """
    Create a transform from a dictionary or string representation.
    
    Args:
        data: Dictionary with transform parameters or "identity" string
        
    Returns:
        Transform object of appropriate type
        
    Raises:
        ValueError: If data format is invalid or unsupported
        
    Example:
        >>> # Identity transform
        >>> identity = from_dict("identity")
        >>> 
        >>> # Translation transform
        >>> trans = from_dict({"translation": [10, 20, 5]})
        >>> 
        >>> # Scale transform
        >>> scale = from_dict({"scale": [2.0, 1.5, 0.5]})
        >>> 
        >>> # Homogeneous transform
        >>> matrix = from_dict({
        ...     "homogeneous": [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
        ... })
    """
    # Handle identity as string
    if data == "identity":
        return identity()
    
    if not isinstance(data, dict):
        raise ValueError(f"Transform data must be a dictionary or 'identity' string, got {type(data)}")
    
    # Check for exactly one key (self-describing parameter)
    if len(data) != 1:
        raise ValueError(f"Transform dictionary must have exactly one key, got {len(data)}")
    
    key, value = next(iter(data.items()))
    
    if key == "translation":
        return translation(value)
    elif key == "scale":
        return scale(value)
    elif key == "mapAxis":
        return mapaxis(value)
    elif key == "homogeneous":
        # Model constructor handles both 2D matrix and flat list formats
        return homogeneous(value)
    elif key == "displacements":
        if isinstance(value, str):
            # Simple path-only format
            return DisplacementLookupTable(path=value)
        elif isinstance(value, dict):
            # Full configuration format
            path = value.get("path")
            if not path:
                raise ValueError("Displacement lookup table must have 'path' field")
            
            interpolation = value.get("interpolation", "nearest")
            extrapolation = value.get("extrapolation", "nearest")
            
            return displacement_lookup(path, interpolation, extrapolation)
        else:
            raise ValueError(f"Invalid displacements format: {type(value)}")
    elif key == "lookup_table":
        if isinstance(value, dict):
            path = value.get("path")
            if not path:
                raise ValueError("Coordinate lookup table must have 'path' field")
            
            interpolation = value.get("interpolation", "nearest")
            extrapolation = value.get("extrapolation", "nearest")
            
            return coordinate_lookup(path, interpolation, extrapolation)
        else:
            raise ValueError(f"Invalid lookup_table format: {type(value)}")
    else:
        raise ValueError(f"Unknown transform type: {key}")


def from_json(json_str: str) -> Transform:
    """
    Create a transform from a JSON string.
    
    Args:
        json_str: JSON string representation of transform
        
    Returns:
        Transform object of appropriate type
        
    Raises:
        ValueError: If JSON is invalid or transform format is unsupported
        
    Example:
        >>> trans = from_json('{"translation": [10, 20, 5]}')
        >>> trans.to_dict()
        {'translation': [10.0, 20.0, 5.0]}
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    
    return from_dict(data)