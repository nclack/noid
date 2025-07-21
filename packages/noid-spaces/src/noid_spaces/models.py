"""
Coordinat space model classes.
"""

from enum import Enum
from pathlib import Path
import sys
from typing import Any, cast

import noid_transforms
from noid_transforms import Transform
import pint

# Add the _out/python directory to sys.path to import generated classes
_python_dir = Path(__file__).parent.parent.parent / "_out" / "python"
sys.path.insert(0, str(_python_dir))

try:
    from spaces_v0 import (
        CoordinateSystem as _CoordinateSystem,
        CoordinateTransform as _CoordinateTransform,
        Dimension as _Dimension,
        DimensionType as _DimensionType,
    )
except ImportError as e:
    raise ImportError(
        f"Could not import LinkML-generated classes from {_python_dir}. "
        f"Please run 'python build.py' to generate the required files. "
        f"Error: {e}"
    ) from e


# Create a shared biomedical unit registry for consistent unit handling
def _create_unit_registry() -> pint.UnitRegistry:
    """
    Create a Pint unit registry with custom units.

    Loads custom unit definitions from units.txt
    following the "schema/vocabulary file as source-of-truth" pattern.

    Returns:
        UnitRegistry with custom units loaded
    """
    ureg = pint.UnitRegistry()

    # Load custom unit definitions
    unit_defs = Path(__file__).parent.parent.parent / "units.txt"
    if unit_defs.exists():
        try:
            ureg.load_definitions(str(unit_defs))
        except Exception as e:
            # Fall back to default registry if custom definitions fail to load
            import warnings

            warnings.warn(
                f"Failed to load unit definitions from {unit_defs}: {e}. "
                f"Using default Pint registry.",
                UserWarning,
                stacklevel=2,
            )
    else:
        import warnings

        warnings.warn(
            f"Unit definitions file not found at {unit_defs}. "
            f"Using default Pint registry.",
            UserWarning,
            stacklevel=2,
        )

    return ureg


_ureg = _create_unit_registry()


class Unit:
    """
    Unit specification that supports non-physical terms or physical units.
    """

    def __init__(self, unit: str) -> None:
        """
        Create a unit term.

        Args:
            unit: Unit string (non-physical like "index"/"arbitrary" or physical like "m"/"s")

        Raises:
            ValueError: If unit is invalid or empty
            pint.UndefinedUnitError: If physical unit is not recognized by Pint

        Example:
            >>> UnitTerm("index")     # Non-physical unit
            >>> UnitTerm("arbitrary") # Non-physical unit
            >>> UnitTerm("m")         # Physical unit (length)
            >>> UnitTerm("s")         # Physical unit (time)
            >>> UnitTerm("kg/m^3")    # Complex physical unit (density)
        """
        if not unit or not isinstance(unit, str):
            raise ValueError("Unit must be a non-empty string")

        # Always store as string
        self._unit = unit

        # All units go through Pint validation now (including index/arbitrary)
        self._pint_unit = self._validate_unit(unit)

        # Determine if unit is non-physical based on semantic meaning
        self._is_non_physical = unit in ["index", "arbitrary"]

        # Unit validation happens via Pint in constructor, so no additional validation needed

    @staticmethod
    def _validate_unit(unit_str: str) -> pint.Unit:
        """
        Validate unit using Pint (includes both physical and non-physical units).

        Args:
            unit_str: Unit string to validate

        Returns:
            Pint Unit object if valid

        Raises:
            pint.UndefinedUnitError: If unit is not recognized
            ValueError: If unit string is malformed
        """
        if not unit_str.strip():
            raise ValueError("Unit string cannot be empty or whitespace")

        try:
            # Parse the unit using Pint
            parsed = _ureg.parse_expression(unit_str)

            # Handle different return types from parse_expression
            if isinstance(parsed, pint.Unit):
                return parsed
            elif isinstance(parsed, pint.Quantity):
                # This happens for units defined with magnitudes (e.g., percent = 0.01)
                # We extract just the unit part, ignoring the magnitude
                # Note: parse_expression always returns Quantity for unit strings
                if parsed.magnitude != 1:
                    raise ValueError(
                        f"Unit string '{unit_str}' contains a magnitude. Only pure unit strings are allowed."
                    )
                # Cast to Unit to satisfy type checker - PlainUnit is a subtype of Unit
                return cast(pint.Unit, parsed.units)
            else:
                # Handle other cases (like integers for dimensionless units)
                return _ureg.dimensionless

        except pint.UndefinedUnitError as e:
            # Re-raise with clearer message
            raise pint.UndefinedUnitError(f"Unrecognized unit: '{unit_str}'") from e
        except Exception as e:
            raise ValueError(f"Invalid unit format '{unit_str}': {e}") from e

    @property
    def is_non_physical(self) -> bool:
        """True if this is a non-physical unit (index, arbitrary)."""
        return self._is_non_physical

    def to_dimension_type(self) -> "DimensionType":
        """
        Project unit to its corresponding dimension type.

        Returns:
            DimensionType based on unit's physical meaning

        Example:
            >>> UnitTerm("m").to_dimension_type()
            DimensionType.SPACE
            >>> UnitTerm("s").to_dimension_type()
            DimensionType.TIME
            >>> UnitTerm("index").to_dimension_type()
            DimensionType.INDEX
        """
        # Handle special case first
        if self._unit == "index":
            return DimensionType.INDEX

        # Non-physical units (arbitrary) map to OTHER
        if self._is_non_physical:
            return DimensionType.OTHER

        # Physical units based on dimensionality
        if self._pint_unit.dimensionality == _ureg.meter.dimensionality:
            return DimensionType.SPACE
        elif self._pint_unit.dimensionality == _ureg.second.dimensionality:
            return DimensionType.TIME
        else:
            return DimensionType.OTHER

    @property
    def dimensionality(self) -> str | pint.util.UnitsContainer:
        """
        Get the dimensionality of the unit.

        Returns:
            String for non-physical units, UnitsContainer for physical units
        """
        if self._is_non_physical:
            return self._unit
        return self._pint_unit.dimensionality

    @property
    def pint_unit(self) -> pint.Unit:
        """Get the underlying Pint unit (dimensionless for non-physical units)."""
        return self._pint_unit

    def to_quantity(self, magnitude: float = 1.0) -> pint.Quantity:
        """
        Convert to Pint quantity for calculations.

        Args:
            magnitude: Numerical value to attach to the unit

        Returns:
            Pint Quantity object

        Note:
            Non-physical units (index, arbitrary) are mapped to dimensionless

        Example:
            >>> unit = UnitTerm("m")
            >>> quantity = unit.to_quantity(5.0)  # 5.0 meter
            >>>
            >>> unit = UnitTerm("index")
            >>> quantity = unit.to_quantity(3)    # 3 dimensionless
        """
        return magnitude * self._pint_unit

    @classmethod
    def list_units(cls, category: str | None = None) -> list[str]:
        """
        List available units, optionally filtered by category.

        Args:
            category: Optional category filter ("spatial", "temporal", "chemistry", etc.)

        Returns:
            List of unit names/symbols

        Note:
            Categories are inferred from dimensionality and common usage patterns.
        """
        units = []

        # Get all defined units from registry
        for unit_name in _ureg._units:
            try:
                parsed = _ureg.parse_expression(unit_name)

                # Handle both Unit and Quantity objects
                if isinstance(parsed, pint.Unit):
                    unit_obj = parsed
                elif isinstance(parsed, pint.Quantity):
                    unit_obj = parsed.units
                else:
                    continue

                if category is None:
                    units.append(unit_name)
                elif (
                    category == "spatial"
                    and unit_obj.dimensionality == _ureg.meter.dimensionality
                ):
                    units.append(unit_name)
                elif (
                    category == "temporal"
                    and unit_obj.dimensionality == _ureg.second.dimensionality
                ):
                    units.append(unit_name)
                elif category == "chemistry" and (
                    "mole" in str(unit_obj.dimensionality)
                    or "substance" in str(unit_obj.dimensionality)
                ):
                    units.append(unit_name)
                elif category == "dimensionless" and unit_obj.dimensionless:
                    units.append(unit_name)
            except Exception:
                continue

        return sorted(units)

    @property
    def value(self) -> str:
        """The underlying unit value."""
        return self._unit

    def to_data(self) -> str:
        """Convert to data representation for serialization."""
        return self._unit

    def __str__(self) -> str:
        """String representation."""
        return self.to_data()

    def __repr__(self) -> str:
        """Developer representation."""
        return f"UnitTerm({self.to_data()!r})"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, Unit):
            return False
        return self.to_data() == other.to_data()

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.to_data())

    @classmethod
    def __get_validators__(cls):
        """Pydantic validators."""
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Pydantic validation."""
        if isinstance(v, cls):
            return v
        return cls(v)


class DimensionType(Enum):
    """
    Dimension type enumeration.

    Available types:
    - SPACE: Spatial dimensions (length-based)
    - TIME: Temporal dimensions (time-based)
    - OTHER: General dimensions (channels, indices, categories)
    - INDEX: Array index dimensions (uses "index" unit)
    """

    SPACE = "space"
    TIME = "time"
    OTHER = "other"
    INDEX = "index"

    def to_data(self) -> str:
        """Convert to data representation for serialization."""
        return self.value


# Re-export original enum from generated code for LinkML compatibility
_DimensionType = _DimensionType


class Dimension:
    """
    A single axis within a coordinate space with its measurement unit and classification.

    Example:
        >>> # Create coordinate system first
        >>> cs = CoordinateSystem(id="mouse_123", dimensions=[])
        >>>
        >>> # Add dimensions with auto-labeling
        >>> ap_dim = cs.add_dimension(unit="mm", kind="space")  # Auto-labeled as "dim_0"
        >>> ml_dim = cs.add_dimension(unit="mm", kind="space", label="ML")  # Explicit label
        >>>
        >>> # Create with fully qualified ID: <coordinate system>#<label>
        >>> dv_dim = Dimension(unit="mm", dimension_id="mouse_123#DV")
        >>>
        >>> # Standalone dimension
        >>> temp_dim = Dimension(unit="arbitrary", dimension_id="temp")
    """

    def __init__(
        self,
        unit: str | Unit,
        kind: str | DimensionType | None = None,
        label: str | None = None,
        coordinate_system: "CoordinateSystem | None" = None,
        dimension_id: str | None = None,
    ) -> None:
        """
        Create a dimension with validation.

        Args:
            unit: Unit specification (string or UnitTerm)
            kind: Dimension type (string or DimensionType enum). If None, inferred from unit.
            label: Human-readable label for local ID (if None, auto-generated when coordinate_system provided)
            coordinate_system: CoordinateSystem object this dimension belongs to (enables auto-labeling)
            dimension_id: Fully qualified dimension ID (alternative to coordinate_system + label)

        Raises:
            ValueError: If parameters are invalid or inconsistent
        """
        # Handle coordinate_system object with auto-labeling
        if coordinate_system is not None:
            coordinate_system_id = coordinate_system.id
            # Auto-generate label if not provided
            if not label and not dimension_id:
                label = coordinate_system._generate_dimension_label()
                coordinate_system._register_dimension_label(label)
        else:
            coordinate_system_id = None
        unit = unit if isinstance(unit, Unit) else Unit(unit)

        # Infer kind from unit if not provided
        if kind is None:
            kind = unit.to_dimension_type()
        else:
            kind = kind if isinstance(kind, DimensionType) else DimensionType(kind)

        self._validate_unit_type_consistency(unit, kind)

        # Handle dimension identity according to coordinate system namespacing rules
        # see docs/dimension-identity-namespacing-rfc.md
        if dimension_id is not None and dimension_id.strip():
            # Parse fully qualified ID
            cs_id, local_id = self.parse_dimension_id(dimension_id)
            if not cs_id:
                # Standalone dimension with simple ID
                self._coordinate_system_id = None
                self._local_id = dimension_id
                self.label = label or dimension_id
            else:
                # Namespaced dimension ID
                self._coordinate_system_id = cs_id
                self._local_id = local_id
                self.label = label or local_id
        elif label:
            # Use provided coordinate system (can be None) and label
            self._coordinate_system_id = coordinate_system_id
            self._local_id = label
            self.label = label
        else:
            raise ValueError(
                "Must provide either 'dimension_id' or 'coordinate_system' (with optional 'label')"
            )

        # Create internal representation using LinkML-generated model
        # Build the full dimension ID for the LinkML model
        if self._coordinate_system_id and self._local_id:
            inner_dimension_id = f"{self._coordinate_system_id}#{self._local_id}"
        elif self._local_id:
            inner_dimension_id = self._local_id
        else:
            inner_dimension_id = dimension_id or label

        self._inner = _Dimension(
            id=inner_dimension_id, unit=unit.value, type=kind.value
        )

        # Validate the dimension (non-strict during construction )
        from .validation import validate_dimension

        validate_dimension(self, strict=False)

    @staticmethod
    def parse_dimension_id(dim_id: str) -> tuple[str | None, str]:
        """
        Parse dimension ID into coordinate system and local components.

        Args:
            dim_id: Dimension identifier to parse

        Returns:
            Tuple of (coordinate_system_id, local_id)

        Examples:
            "mouse_123#AP" → ("mouse_123", "AP")
            "AP" → (None, "AP")
        """
        if "#" in dim_id:
            cs_id, local_id = dim_id.split("#", 1)
            return cs_id, local_id
        else:
            return None, dim_id

    @staticmethod
    def _validate_unit_type_consistency(unit: Unit, kind: DimensionType) -> None:
        """Validate that unit and kind are consistent."""
        # Rule: If kind is "index", then unit MUST be "index"
        if kind == DimensionType.INDEX and unit.value != "index":
            raise ValueError(
                f"Dimension type 'index' requires unit 'index', got '{unit.value}'"
            )

    @property
    def id(self) -> str:
        """Return global dimension identifier."""
        if self._coordinate_system_id and self._local_id:
            return f"{self._coordinate_system_id}#{self._local_id}"
        elif self._local_id:
            return self._local_id
        else:
            raise ValueError("Dimension not properly initialized")

    @property
    def local_id(self) -> str:
        """Return local dimension identifier."""
        return self._local_id

    @property
    def coordinate_system_id(self) -> str | None:
        """Return coordinate system identifier."""
        return self._coordinate_system_id

    @property
    def unit(self) -> Unit:
        """Unit of measurement."""
        return Unit(self._inner.unit)

    @property
    def type(self) -> DimensionType:
        """Dimension type classification."""
        # LinkML returns the string value, not the enum
        return DimensionType(str(self._inner.type))

    def to_data(self) -> dict[str, str]:
        """
        Convert to dictionary representation for serialization.

        Returns:
            Dictionary with id, unit, and type fields
        """
        return {
            "id": self.id,
            "unit": self._inner.unit,
            "type": str(self._inner.type),
        }

    @classmethod
    def from_data(cls, data: dict[str, str]) -> "Dimension":
        """
        Create from dictionary representation.

        Args:
            data: Dictionary with id and unit fields. Type is optional.

        Returns:
            Dimension instance

        Raises:
            ValueError: If required fields are missing
        """
        try:
            dimension_id = data["id"]
            unit = data["unit"]
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}") from e

        # Type is optional - will be inferred from unit if not provided
        kind_value = data.get("type", None)

        return cls(unit=unit, kind=kind_value, dimension_id=dimension_id)

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"Dimension(id={self.id!r}, "
            f"unit={self._inner.unit!r}, "
            f"type={str(self._inner.type)!r})"
        )

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"{self.id} [{self._inner.unit}] ({self._inner.type})"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, Dimension):
            return False
        return (
            self.id == other.id
            and self._inner.unit == other._inner.unit
            and self._inner.type == other._inner.type
        )


class CoordinateSystem:
    """
    Collection of dimensions that together define a coordinate space for positioning data elements.

    Example:
        >>> # Create a 2D spatial coordinate system
        >>> x_dim = Dimension(id="x", unit="m")
        >>> y_dim = Dimension(id="y", unit="m")
        >>> coord_sys = CoordinateSystem(dimensions=[x_dim, y_dim])
        >>>
        >>> # Create with identification
        >>> coord_sys = CoordinateSystem(
        ...     id="image_coords",
        ...     dimensions=[x_dim, y_dim],
        ...     description="2D image coordinate system"
        ... )
    """

    def __init__(
        self,
        dimensions: list[Dimension],
        id: str | None = None,
        description: str | None = None,
    ) -> None:
        """
        Create a coordinate system with validation.

        Args:
            dimensions: List of dimension specifications (minimum 1)
            id: Optional identifier for the coordinate system
            description: Optional description of the coordinate system

        Raises:
            ValueError: If parameters are invalid or dimensions belong to different coordinate systems
        """
        # Allow empty coordinate systems for dynamic dimension addition
        # if not dimensions:
        #     raise ValueError("CoordinateSystem must have at least one dimension")

        if not all(isinstance(dim, Dimension) for dim in dimensions):
            raise ValueError("All dimensions must be Dimension instances")

        if id is not None and (not isinstance(id, str) or not id.strip()):
            raise ValueError(
                "CoordinateSystem id must be a non-empty string if provided"
            )

        if description is not None and (
            not isinstance(description, str) or not description.strip()
        ):
            raise ValueError(
                "CoordinateSystem description must be a non-empty string if provided"
            )

        # Validate dimension ownership consistency according to RFC
        for dim in dimensions:
            if (
                hasattr(dim, "_coordinate_system_id")
                and dim._coordinate_system_id
                and dim._coordinate_system_id != id
            ):
                raise ValueError(
                    f"Dimension '{dim.local_id}' belongs to coordinate system '{dim._coordinate_system_id}' "
                    f"but this coordinate system is '{id}'. All dimensions must belong "
                    f"to the same coordinate system."
                )

        # Convert Dimension objects to their internal representations for LinkML
        dimension_data = [dim._inner for dim in dimensions]

        # Create internal representation (handle empty dimensions for LinkML)
        if dimension_data:
            self._inner = _CoordinateSystem(
                dimensions=dimension_data,
                id=id,
                description=description,
            )
        else:
            # Create a minimal valid LinkML object that we can modify later
            dummy_dim = _Dimension(id="_placeholder", unit="arbitrary", type="other")
            self._inner = _CoordinateSystem(
                dimensions=[dummy_dim],
                id=id,
                description=description,
            )
            # Clear the dimensions list since we'll manage it ourselves
            self._inner.dimensions = []

        # Store original Dimension objects for property access
        self._dimensions = dimensions

        # Initialize auto-labeling counter
        self._auto_label_counter = 0
        self._used_labels = {
            dim.local_id for dim in dimensions if hasattr(dim, "local_id")
        }

        # Validate the coordinate system (non-strict to avoid breaking existing functionality)
        from .validation import validate_coordinate_system

        validate_coordinate_system(self, strict=False)

    @property
    def id(self) -> str | None:
        """Optional identifier for the coordinate system."""
        return self._inner.id

    @property
    def dimensions(self) -> list[Dimension]:
        """List of dimension specifications."""
        return self._dimensions

    @property
    def description(self) -> str | None:
        """Optional description of the coordinate system."""
        return self._inner.description

    def to_data(self) -> dict[str, str | list[dict[str, str]]]:
        """
        Convert to dictionary representation for serialization.

        Returns:
            Dictionary with dimensions and optional id/description fields
        """
        data: dict[str, Any] = {
            "dimensions": [dim.to_data() for dim in self.dimensions]
        }

        if self.id is not None:
            data["id"] = self.id

        if self.description is not None:
            data["description"] = self.description

        return data

    @classmethod
    def from_data(cls, data: dict) -> "CoordinateSystem":
        """
        Create from dictionary representation.

        Args:
            data: Dictionary with dimensions field and optional id/description

        Returns:
            CoordinateSystem instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            dimensions_data = data["dimensions"]
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}") from e

        if not isinstance(dimensions_data, list) or not dimensions_data:
            raise ValueError("Dimensions must be a non-empty list")

        # Convert dimension data to Dimension objects
        dimensions = [Dimension.from_data(dim_data) for dim_data in dimensions_data]

        return cls(
            dimensions=dimensions,
            id=data.get("id"),
            description=data.get("description"),
        )

    def __repr__(self) -> str:
        """Developer representation."""
        parts = [f"dimensions={len(self.dimensions)} dims"]
        if self.id:
            parts.insert(0, f"id={self.id!r}")
        if self.description:
            parts.append(f"description={self.description!r}")
        return f"CoordinateSystem({', '.join(parts)})"

    def __str__(self) -> str:
        """User-friendly representation."""
        dim_summary = ", ".join(
            f"{dim.id}[{dim.unit.value}]" for dim in self.dimensions
        )
        base = f"CoordinateSystem({dim_summary})"
        if self.id:
            base = f"{self.id}: {base}"
        return base

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, CoordinateSystem):
            return False
        return (
            self.id == other.id
            and self.dimensions == other.dimensions
            and self.description == other.description
        )

    def _generate_dimension_label(self) -> str:
        """
        Generate an automatic dimension label (dim_0, dim_1, etc.).

        Returns:
            Unique dimension label following the dim_N pattern
        """
        while True:
            label = f"dim_{self._auto_label_counter}"
            if label not in self._used_labels:
                return label
            self._auto_label_counter += 1

    def _register_dimension_label(self, label: str) -> None:
        """
        Register a dimension label as used.

        Args:
            label: Label to register as used
        """
        self._used_labels.add(label)

    def add_dimension(
        self,
        unit: str | Unit,
        kind: str | DimensionType | None = None,
        label: str | None = None,
    ) -> "Dimension":
        """
        Add a new dimension to this coordinate system with optional auto-labeling.

        Args:
            unit: Unit specification
            kind: Dimension type (inferred from unit if None)
            label: Dimension label (auto-generated if None)

        Returns:
            The created Dimension object

        Raises:
            ValueError: If label already exists in this coordinate system
        """
        if label and label in self._used_labels:
            raise ValueError(
                f"Dimension label '{label}' already exists in coordinate system '{self.id}'"
            )

        # Create dimension with this coordinate system
        dim = Dimension(unit=unit, kind=kind, label=label, coordinate_system=self)

        # Register the label as used (for both explicit and auto-generated labels)
        if not label:  # Auto-generated label was already registered in constructor
            pass
        else:  # Explicit label needs to be registered
            self._register_dimension_label(dim.label)

        # Add to our dimensions list
        self._dimensions.append(dim)

        # Update internal representation
        self._inner.dimensions.append(dim._inner)

        return dim


class CoordinateTransform:
    """
    Mathematical mapping between input and output coordinate spaces with transform definition.

    This class provides a bridge between coordinate spaces using transformations from the
    noid_transforms package. It handles both referenced and inline coordinate systems.

    Example:
        >>> from noid_transforms import translation
        >>> from noid_spaces import coordinate_system
        >>>
        >>> # Create coordinate systems
        >>> input_cs = coordinate_system([{"id": "x", "unit": "pixel"}, {"id": "y", "unit": "pixel"}])
        >>> output_cs = coordinate_system([{"id": "x", "unit": "mm"}, {"id": "y", "unit": "mm"}])
        >>>
        >>> # Create transform with objects
        >>> transform = CoordinateTransform(
        ...     input=input_cs,
        ...     output=output_cs,
        ...     transform=translation([0.1, 0.1])  # 0.1mm per pixel
        ... )
    """

    def __init__(
        self,
        input: CoordinateSystem,
        output: CoordinateSystem,
        transform: Transform,
        id: str | None = None,
        description: str | None = None,
    ) -> None:
        """
        Create a coordinate transform with validation.

        Args:
            input: Input coordinate system
            output: Output coordinate system
            transform: Transform definition from noid_transforms
            id: Optional identifier for the coordinate transform
            description: Optional description of the coordinate transform

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate inputs

        if id is not None and (not isinstance(id, str) or not id.strip()):
            raise ValueError(
                "CoordinateTransform id must be a non-empty string if provided"
            )

        if description is not None and (
            not isinstance(description, str) or not description.strip()
        ):
            raise ValueError(
                "CoordinateTransform description must be a non-empty string if provided"
            )

        # Create internal representation for LinkML compatibility
        # Note: For now, we store the transform data as a dict since the generated
        # LinkML classes expect dict format for cross-schema references
        self._inner = _CoordinateTransform(
            input=input._inner,
            output=output._inner,
            transform=transform.to_data(),  # Convert to dict for LinkML
            id=id,
            description=description,
        )

        # Store the enhanced objects for property access (similar to CoordinateSystem._dimensions)
        self._input = input
        self._output = output
        self._transform = transform

        # Validate the coordinate transform (non-strict to avoid breaking existing functionality)
        from .validation import validate_coordinate_transform

        validate_coordinate_transform(self, strict=False)

    @property
    def id(self) -> str | None:
        """Optional identifier for the coordinate transform."""
        return self._inner.id

    @property
    def input(self) -> CoordinateSystem:
        """Input coordinate space."""
        return self._input

    @property
    def output(self) -> CoordinateSystem:
        """Output coordinate space."""
        return self._output

    @property
    def transform(self) -> Transform:
        """Transform definition from noid_transforms."""
        return self._transform

    @property
    def description(self) -> str | None:
        """Optional description of the coordinate transform."""
        return self._inner.description

    def to_data(self) -> dict[str, Any]:
        """
        Convert to dictionary representation for serialization.

        Returns:
            Dictionary with input, output, transform and optional id/description fields
        """
        data: dict[str, Any] = {
            "input": self.input.to_data(),
            "output": self.output.to_data(),
            "transform": self.transform.to_data(),  # Get dict from stored transform object
        }

        if self._inner.id is not None:
            data["id"] = self._inner.id

        if self._inner.description is not None:
            data["description"] = self._inner.description

        return data

    @classmethod
    def from_data(cls, data: dict) -> "CoordinateTransform":
        """
        Create from dictionary representation.

        Args:
            data: Dictionary with input, output, transform fields and optional id/description

        Returns:
            CoordinateTransform instance

        Raises:
            ValueError: If required fields are missing or invalid
            ImportError: If noid_transforms is not available for transform creation
        """
        try:
            input_data = data["input"]
            output_data = data["output"]
            transform_data = data["transform"]
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}") from e

        # Convert coordinate system data
        input_cs = CoordinateSystem.from_data(input_data)
        output_cs = CoordinateSystem.from_data(output_data)

        try:
            transform_obj = noid_transforms.from_data(transform_data)
        except Exception as e:
            raise ValueError(f"Failed to create transform from data: {e}") from e

        return cls(
            input=input_cs,
            output=output_cs,
            transform=transform_obj,
            id=data.get("id"),
            description=data.get("description"),
        )

    def __repr__(self) -> str:
        """Developer representation."""
        parts = []
        if self.id:
            parts.append(f"id={self.id!r}")

        # Show input/output dimensions summary
        input_dims = f"{len(self.input.dimensions)} dims"
        output_dims = f"{len(self.output.dimensions)} dims"
        parts.append(f"input={input_dims}")
        parts.append(f"output={output_dims}")
        parts.append(f"transform={type(self.transform).__name__}")

        if self.description:
            parts.append(f"description={self.description!r}")

        return f"CoordinateTransform({', '.join(parts)})"

    def __str__(self) -> str:
        """User-friendly representation."""
        input_summary = " → ".join(
            f"{dim.id}[{dim.unit.value}]" for dim in self.input.dimensions
        )
        output_summary = " → ".join(
            f"{dim.id}[{dim.unit.value}]" for dim in self.output.dimensions
        )

        base = f"({input_summary}) → ({output_summary}) via {type(self.transform).__name__}"
        if self.id:
            base = f"{self.id}: {base}"
        return base

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, CoordinateTransform):
            return False
        return (
            self._inner.id == other._inner.id
            and self._input == other._input
            and self._output == other._output
            and self._transform.to_data()
            == other._transform.to_data()  # Compare transform data
            and self._inner.description == other._inner.description
        )


def extract_coordinate_system_id(dimensions: list[Dimension]) -> str | None:
    """
    Extract coordinate system ID from a set of dimensions.

    Args:
        dimensions: List of dimensions to analyze

    Returns:
        Coordinate system ID if all dimensions belong to same system, None otherwise

    Raises:
        ValueError: If dimensions belong to multiple coordinate systems
    """
    cs_ids = set()
    for dim in dimensions:
        if hasattr(dim, "coordinate_system_id") and dim.coordinate_system_id:
            cs_ids.add(dim.coordinate_system_id)

    if len(cs_ids) == 0:
        return None
    elif len(cs_ids) == 1:
        return cs_ids.pop()
    else:
        raise ValueError(f"Dimensions belong to multiple coordinate systems: {cs_ids}")
