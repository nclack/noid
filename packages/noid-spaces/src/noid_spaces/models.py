"""
Enhanced coordinate space model classes.

This module provides enhanced wrappers around the LinkML-generated space classes,
adding user-friendly methods, validation, and improved documentation.
"""

from collections.abc import Sequence
from pathlib import Path
import sys
from typing import Any

# Add the _out/python directory to sys.path to import generated classes
_python_dir = Path(__file__).parent.parent.parent / "_out" / "python"
sys.path.insert(0, str(_python_dir))

try:
    # Import with the actual filename format from the generated python file
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(
        "spaces_v0", _python_dir / "spaces_v0.py"
    )
    spaces_v0 = importlib.util.module_from_spec(spec)
    sys.modules["spaces_v0"] = spaces_v0
    spec.loader.exec_module(spaces_v0)

    # Now we can import the classes
    from spaces_v0 import (
        CoordinateSystem as _CoordinateSystem,
        CoordinateTransform as _CoordinateTransform,
        Dimension as _Dimension,
        DimensionArray as _DimensionArray,
        DimensionSpec as _DimensionSpec,
        DimensionType as _DimensionType,
        SpecialUnits as _SpecialUnits,
        UnitTerm as _UnitTerm,
    )
except ImportError as e:
    raise ImportError(
        f"Could not import LinkML-generated classes from {_python_dir}. "
        f"Please run 'python build.py' to generate the required files. "
        f"Error: {e}"
    ) from e


class Dimension(_Dimension):
    """
    Enhanced dimension class with validation.

    Invariants:
        - ID must be a non-empty string
        - Unit must be valid (special units or UDUNITS-2 compatible)
        - Type must be one of: space, time, other, index
        - If type is "index", unit must be "index"
    """

    def __init__(self, id: str, unit: str, type: str):
        """
        Create a dimension.

        Args:
            id: Unique identifier for the dimension
            unit: Unit of measurement (special units or UDUNITS-2 compatible)
            type: Dimension type ('space', 'time', 'other', 'index')

        Raises:
            ValueError: If parameters are invalid or violate constraints

        Example:
            >>> Dimension("x", "micrometer", "space")
            >>> Dimension("t", "second", "time")
            >>> Dimension("channel", "arbitrary", "other")
            >>> Dimension("i", "index", "index")
        """
        if not id or not isinstance(id, str):
            raise ValueError("Dimension ID must be a non-empty string")

        if not unit or not isinstance(unit, str):
            raise ValueError("Unit must be a non-empty string")

        if type not in ["space", "time", "other", "index"]:
            raise ValueError("Type must be one of: space, time, other, index")

        # Validate index type constraint
        if type == "index" and unit != "index":
            raise ValueError("Index type dimensions must have 'index' unit")

        super().__init__(id=id, unit=unit, type=type)

    def to_dict(self) -> dict[str, Any]:
        """Convert dimension to dictionary representation."""
        return {
            "id": self.id,
            "unit": self.unit,
            "type": self.type,
        }

    def __str__(self) -> str:
        """String representation of dimension."""
        return f"{self.id} ({self.unit}, {self.type})"

    def __repr__(self) -> str:
        """Developer representation of dimension."""
        return f"Dimension(id='{self.id}', unit='{self.unit}', type='{self.type}')"

    @property
    def is_spatial(self) -> bool:
        """Check if this is a spatial dimension."""
        return self.type == "space"

    @property
    def is_temporal(self) -> bool:
        """Check if this is a temporal dimension."""
        return self.type == "time"

    @property
    def is_index(self) -> bool:
        """Check if this is an index dimension."""
        return self.type == "index"

    @property
    def is_other(self) -> bool:
        """Check if this is an 'other' type dimension."""
        return self.type == "other"


class CoordinateSystem(_CoordinateSystem):
    """
    Enhanced coordinate system class with validation.

    Invariants:
        - ID must be a non-empty string
        - Must have at least one dimension
        - All dimensions must be valid Dimension objects or references
    """

    def __init__(
        self,
        id: str,
        dimensions: Sequence[Dimension | str],
        description: str | None = None,
    ):
        """
        Create a coordinate system.

        Args:
            id: Unique identifier for the coordinate system
            dimensions: List of dimensions (Dimension objects or string references)
            description: Optional description

        Raises:
            ValueError: If parameters are invalid

        Example:
            >>> dims = [Dimension("x", "micrometer", "space"), Dimension("y", "micrometer", "space")]
            >>> CoordinateSystem("physical", dims, "Physical coordinate system")
            >>> CoordinateSystem("array", ["i", "j", "k"], "Array index system")
        """
        if not id or not isinstance(id, str):
            raise ValueError("CoordinateSystem ID must be a non-empty string")

        if not dimensions or len(dimensions) == 0:
            raise ValueError("CoordinateSystem must have at least one dimension")

        # Convert dimensions to the proper format for LinkML
        dim_specs = []
        for dim in dimensions:
            if isinstance(dim, Dimension):
                dim_specs.append(dim)
            elif isinstance(dim, str):
                dim_specs.append(dim)
            else:
                raise ValueError("Dimensions must be Dimension objects or strings")

        super().__init__(id=id, dimensions=dim_specs, description=description)

    def to_dict(self) -> dict[str, Any]:
        """Convert coordinate system to dictionary representation."""
        result = {
            "id": self.id,
            "dimensions": [],
        }

        for dim in self.dimensions:
            if isinstance(dim, Dimension):
                result["dimensions"].append(dim.to_dict())
            else:
                result["dimensions"].append(dim)

        if self.description:
            result["description"] = self.description

        return result

    def __str__(self) -> str:
        """String representation of coordinate system."""
        dim_strs = []
        for dim in self.dimensions:
            if isinstance(dim, Dimension):
                dim_strs.append(str(dim))
            else:
                dim_strs.append(str(dim))
        return f"{self.id}: [{', '.join(dim_strs)}]"

    def __repr__(self) -> str:
        """Developer representation of coordinate system."""
        return f"CoordinateSystem(id='{self.id}', dimensions={self.dimensions!r})"

    @property
    def dimension_count(self) -> int:
        """Number of dimensions in this coordinate system."""
        return len(self.dimensions)

    def get_dimension_by_id(self, dimension_id: str) -> Dimension | None:
        """
        Get a dimension by its ID.

        Args:
            dimension_id: ID of the dimension to find

        Returns:
            The dimension if found, None otherwise
        """
        for dim in self.dimensions:
            if isinstance(dim, Dimension) and dim.id == dimension_id:
                return dim
        return None

    @property
    def spatial_dimensions(self) -> list[Dimension]:
        """Get all spatial dimensions."""
        return [
            dim
            for dim in self.dimensions
            if isinstance(dim, Dimension) and dim.is_spatial
        ]

    @property
    def temporal_dimensions(self) -> list[Dimension]:
        """Get all temporal dimensions."""
        return [
            dim
            for dim in self.dimensions
            if isinstance(dim, Dimension) and dim.is_temporal
        ]

    @property
    def index_dimensions(self) -> list[Dimension]:
        """Get all index dimensions."""
        return [
            dim
            for dim in self.dimensions
            if isinstance(dim, Dimension) and dim.is_index
        ]


class CoordinateTransform(_CoordinateTransform):
    """
    Enhanced coordinate transform class.

    Invariants:
        - ID must be a non-empty string
        - Must have valid input and output coordinate space specifications
        - Must have a valid transform definition
    """

    def __init__(
        self,
        id: str,
        input: str | CoordinateSystem | list[str | Dimension],
        output: str | CoordinateSystem | list[str | Dimension],
        transform: dict,
        description: str | None = None,
    ):
        """
        Create a coordinate transform.

        Args:
            id: Unique identifier for the transform
            input: Input coordinate space specification
            output: Output coordinate space specification
            transform: Transform definition
            description: Optional description

        Raises:
            ValueError: If parameters are invalid

        Example:
            >>> CoordinateTransform(
            ...     "physical_to_array",
            ...     "physical_space",
            ...     "array_space",
            ...     {"scale": [0.5, 0.5, 1.0]}
            ... )
        """
        if not id or not isinstance(id, str):
            raise ValueError("CoordinateTransform ID must be a non-empty string")

        # Convert input/output to proper format
        if isinstance(input, list):
            input = {"dimensions": input}
        if isinstance(output, list):
            output = {"dimensions": output}

        super().__init__(
            id=id,
            input=input,
            output=output,
            transform=transform,
            description=description,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert coordinate transform to dictionary representation."""
        result = {
            "id": self.id,
            "input": self.input,
            "output": self.output,
            "transform": self.transform,
        }

        if self.description:
            result["description"] = self.description

        return result

    def __str__(self) -> str:
        """String representation of coordinate transform."""
        return f"{self.id}: {self.input} -> {self.output}"

    def __repr__(self) -> str:
        """Developer representation of coordinate transform."""
        return f"CoordinateTransform(id='{self.id}', input={self.input!r}, output={self.output!r})"


# Re-export enums from generated code
DimensionType = _DimensionType
SpecialUnits = _SpecialUnits
UnitTerm = _UnitTerm
