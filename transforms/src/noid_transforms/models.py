"""
Enhanced transform model classes.

This module provides enhanced wrappers around the LinkML-generated transform classes,
adding user-friendly methods, better validation, and improved documentation.
"""

import sys
import math
from pathlib import Path
from typing import Dict, List, Union, Any, Optional, Sequence

# Add the _out/python directory to sys.path to import generated classes
_python_dir = Path(__file__).parent.parent.parent / "_out" / "python"
sys.path.insert(0, str(_python_dir))

try:
    from transforms import (
        Transform as _Transform,
        Identity as _Identity,
        Translation as _Translation,
        Scale as _Scale,
        MapAxis as _MapAxis,
        Homogeneous as _Homogeneous,
        DisplacementLookupTable as _DisplacementLookupTable,
        CoordinateLookupTable as _CoordinateLookupTable,
        SamplerConfig as _SamplerConfig,
        InterpolationMethod as _InterpolationMethod,
        ExtrapolationMethod as _ExtrapolationMethod,
    )
except ImportError as e:
    raise ImportError(
        f"Could not import LinkML-generated classes from {_python_dir}. "
        f"Please run 'python build.py' to generate the required files. "
        f"Error: {e}"
    )


class Transform(_Transform):
    """Enhanced base transform class with additional methods."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transform to dictionary representation."""
        # For Identity transforms, return just the string
        if isinstance(self, Identity):
            return "identity"
        
        # For other transforms, create dict with self-describing parameters
        result = {}
        
        if isinstance(self, Translation):
            result["translation"] = self.translation
        elif isinstance(self, Scale):
            result["scale"] = self.scale
        elif isinstance(self, MapAxis):
            result["mapAxis"] = self.mapAxis
        elif isinstance(self, Homogeneous):
            result["homogeneous"] = self.homogeneous
        elif isinstance(self, DisplacementLookupTable):
            if self.displacements:
                result["displacements"] = {
                    "path": self.path,
                    **self.displacements.to_dict()
                }
            else:
                result["displacements"] = self.path
        elif isinstance(self, CoordinateLookupTable):
            lookup_data = {"path": self.path}
            if self.lookup_table:
                lookup_data.update(self.lookup_table.to_dict())
            result["lookup_table"] = lookup_data
        
        return result
    
    def __str__(self) -> str:
        """String representation of transform."""
        return str(self.to_dict())
    
    def __repr__(self) -> str:
        """Developer representation of transform."""
        return f"{self.__class__.__name__}({self.to_dict()})"


class Identity(_Identity, Transform):
    """
    Identity transform - no transformation applied.
    
    Invariants:
        - Always represents the identity operation
        - No parameters required
    """
    
    def __init__(self):
        """Create an identity transform."""
        super().__init__()
    
    def to_dict(self) -> str:
        """Return identity transform as string."""
        return "identity"


class Translation(_Translation, Transform):
    """
    Translation transform with enhanced validation.
    
    Invariants:
        - Translation vector must not be empty
        - All elements must be finite numbers
        - Vector length determines dimensionality
    """
    
    def __init__(self, translation: Union[Sequence[float], Sequence[int]]):
        """
        Create a translation transform.
        
        Args:
            translation: Translation vector as sequence of numbers (supports lists, tuples, numpy arrays)
            
        Raises:
            ValueError: If translation vector is empty
            
        Example:
            >>> Translation([10, 20, 5])
            >>> Translation((10, 20, 5))  # tuples work
            >>> Translation(np.array([10, 20, 5]))  # numpy arrays work
        """
        if len(translation) == 0:
            raise ValueError("Translation vector cannot be empty")
        
        # Convert to float list
        translation_floats = [float(x) for x in translation]
        super().__init__(translation=translation_floats)
    
    @property
    def dimensions(self) -> int:
        """Number of dimensions in the translation."""
        return len(self.translation)


class Scale(_Scale, Transform):
    """
    Scale transform with enhanced validation.
    
    Invariants:
        - Scale vector must not be empty
        - All scale factors must be non-zero finite numbers
        - Vector length determines dimensionality
    """
    
    def __init__(self, scale: Union[Sequence[float], Sequence[int]]):
        """
        Create a scale transform.
        
        Args:
            scale: Scale factors as sequence of numbers (supports lists, tuples, numpy arrays)
            
        Raises:
            ValueError: If scale vector is empty or contains zeros
            
        Example:
            >>> Scale([2.0, 1.5, 0.5])
            >>> Scale((2.0, 1.5, 0.5))  # tuples work
            >>> Scale(np.array([2.0, 1.5, 0.5]))  # numpy arrays work
        """
        if len(scale) == 0:
            raise ValueError("Scale vector cannot be empty")
        
        # Convert to float list and check for zeros
        scale_floats = [float(x) for x in scale]
        if any(s == 0 for s in scale_floats):
            raise ValueError("Scale factors cannot be zero")
        
        super().__init__(scale=scale_floats)
    
    @property
    def dimensions(self) -> int:
        """Number of dimensions in the scale."""
        return len(self.scale)


class MapAxis(_MapAxis, Transform):
    """
    Axis permutation transform with enhanced validation.
    
    Invariants:
        - MapAxis vector must not be empty
        - All indices must be non-negative integers
        - Indices represent 0-based input dimension mapping
        - Vector length determines output dimensionality
    """
    
    def __init__(self, mapAxis: Union[Sequence[int], Sequence[int]]):
        """
        Create an axis mapping transform.
        
        Args:
            mapAxis: Permutation vector of 0-based input dimension indices (supports lists, tuples, numpy arrays)
            
        Raises:
            ValueError: If mapAxis is empty or contains invalid indices
            
        Example:
            >>> MapAxis([1, 0, 2])  # swap first two dimensions
            >>> MapAxis((1, 0, 2))  # tuples work
            >>> MapAxis(np.array([1, 0, 2]))  # numpy arrays work
        """
        if len(mapAxis) == 0:
            raise ValueError("MapAxis vector cannot be empty")
        
        # Convert to int list and validate that all indices are non-negative
        mapAxis_ints = [int(idx) for idx in mapAxis]
        if any(idx < 0 for idx in mapAxis_ints):
            raise ValueError("MapAxis indices must be non-negative")
        
        super().__init__(mapAxis=mapAxis_ints)
    
    @property
    def output_dimensions(self) -> int:
        """Number of output dimensions."""
        return len(self.mapAxis)
    
    @property
    def input_dimensions(self) -> int:
        """Number of input dimensions (inferred from max index)."""
        return max(self.mapAxis) + 1 if self.mapAxis else 0


class Homogeneous(_Homogeneous, Transform):
    """
    Homogeneous transformation matrix with enhanced validation.
    
    Invariants:
        - Matrix must not be empty
        - Matrix must be rectangular (all rows same length)
        - All elements must be finite numbers
        - Accepts both 2D matrix format and flat list format
        - Flat lists must be perfect squares (for square matrices)
    """
    
    def __init__(self, homogeneous: Union[Sequence[Sequence[float]], Sequence[Sequence[int]], Sequence[float], Sequence[int]]):
        """
        Create a homogeneous transformation matrix.
        
        Args:
            homogeneous: 2D transformation matrix or flat list of matrix elements
                        Supports lists, tuples, numpy arrays
            
        Raises:
            ValueError: If matrix is empty, not rectangular, or invalid format
            
        Example:
            >>> # 2D matrix format
            >>> Homogeneous([[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]])
            >>> 
            >>> # Flat list format (perfect square)
            >>> Homogeneous([2.0, 0, 0, 10, 0, 1.5, 0, 20, 0, 0, 0.5, 5, 0, 0, 0, 1])
            >>> 
            >>> # Works with numpy arrays
            >>> Homogeneous(np.array([[2.0, 0, 0, 10], [0, 1.5, 0, 20]]))
        """
        if len(homogeneous) == 0:
            raise ValueError("Homogeneous matrix cannot be empty")
        
        # Handle both 2D matrix format and flat list format
        if len(homogeneous) > 0 and hasattr(homogeneous[0], '__len__') and not isinstance(homogeneous[0], (int, float)):
            # It's a 2D matrix format
            rows = len(homogeneous)
            cols = len(homogeneous[0]) if len(homogeneous) > 0 else 0
            
            # Validate rectangular matrix
            flat_matrix = []
            for row in homogeneous:
                if len(row) != cols:
                    raise ValueError("Homogeneous matrix must be rectangular")
                flat_matrix.extend(float(x) for x in row)
                
            self._rows = rows
            self._cols = cols
            
        else:
            # It's a flat list format - convert to 2D matrix
            flat_list = [float(x) for x in homogeneous]
            length = len(flat_list)
            sqrt_length = int(math.sqrt(length))
            
            if sqrt_length * sqrt_length == length:
                # Perfect square - assume square matrix
                self._rows = sqrt_length
                self._cols = sqrt_length
                flat_matrix = flat_list
            else:
                raise ValueError(f"Flat homogeneous matrix must be a perfect square, got {length} elements")
        
        super().__init__(homogeneous=flat_matrix)
    
    @property
    def matrix_shape(self) -> tuple:
        """Shape of the matrix as (rows, cols)."""
        return (self._rows, self._cols)
    
    def get_matrix(self) -> List[List[float]]:
        """Get the matrix in 2D format."""
        rows, cols = self.matrix_shape
        matrix = []
        for i in range(rows):
            row = self.homogeneous[i * cols:(i + 1) * cols]
            matrix.append(row)
        return matrix


class DisplacementLookupTable(_DisplacementLookupTable, Transform):
    """Displacement field lookup table transform."""
    
    def __init__(self, path: str, displacements: Optional[Union[Dict, _SamplerConfig]] = None):
        """
        Create a displacement lookup table transform.
        
        Args:
            path: Path to displacement field data file
            displacements: Optional sampler configuration
        """
        if displacements and not isinstance(displacements, _SamplerConfig):
            displacements = SamplerConfig(**displacements)
        
        super().__init__(path=path, displacements=displacements)


class CoordinateLookupTable(_CoordinateLookupTable, Transform):
    """Coordinate lookup table transform."""
    
    def __init__(self, path: str, lookup_table: Optional[Union[Dict, _SamplerConfig]] = None):
        """
        Create a coordinate lookup table transform.
        
        Args:
            path: Path to coordinate lookup table data file
            lookup_table: Optional sampler configuration
        """
        if lookup_table and not isinstance(lookup_table, _SamplerConfig):
            lookup_table = SamplerConfig(**lookup_table)
        
        super().__init__(path=path, lookup_table=lookup_table)


class SamplerConfig(_SamplerConfig):
    """Enhanced sampler configuration with validation."""
    
    def __init__(self, 
                 interpolation: Optional[str] = "nearest",
                 extrapolation: Optional[str] = "nearest"):
        """
        Create a sampler configuration.
        
        Args:
            interpolation: Interpolation method
            extrapolation: Extrapolation method
        """
        super().__init__(interpolation=interpolation, extrapolation=extrapolation)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary representation."""
        return {
            "interpolation": self.interpolation,
            "extrapolation": self.extrapolation
        }


# Re-export enums from generated code
InterpolationMethod = _InterpolationMethod
ExtrapolationMethod = _ExtrapolationMethod