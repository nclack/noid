"""
Coordinat space model classes.
"""

from enum import Enum
from pathlib import Path
import sys
from typing import cast

import pint

# Add the _out/python directory to sys.path to import generated classes
_python_dir = Path(__file__).parent.parent.parent / "_out" / "python"
sys.path.insert(0, str(_python_dir))

try:
    from spaces_v0 import Dimension as _Dimension, DimensionType as _DimensionType
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


class UnitTerm:
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
        if not isinstance(other, UnitTerm):
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

    This class provides:
    - Automatic validation of unit-type consistency (e.g., index type must have index unit)
    - Integration with UnitTerm for unit validation via Pint
    - Convenient factory methods for common dimension types
    - Dictionary serialization support

    Example:
        >>> # Create a spatial dimension with explicit type
        >>> x_dim = Dimension(id="x", unit="m", type=DimensionType.SPACE)
        >>>
        >>> # Create with type inferred from unit
        >>> y_dim = Dimension(id="y", unit="mm")  # Infers SPACE from "mm"
        >>> time_dim = Dimension(id="time", unit="s")  # Infers TIME from "s"
        >>> idx_dim = Dimension(id="idx", unit="index")  # Infers INDEX from "index"
        >>>
        >>> # Override inferred type (e.g., wavelength channel using nm)
        >>> wavelength = Dimension(id="wavelength", unit="nm", kind=DimensionType.OTHER)
    """

    def __init__(
        self, id: str, unit: str | UnitTerm, kind: str | DimensionType | None = None
    ) -> None:
        """
        Create a dimension with validation.

        Args:
            id: Unique identifier for the dimension
            unit: Unit specification (string or UnitTerm)
            kind: Dimension type (string or DimensionType enum). If None, inferred from unit.

        Raises:
            ValueError: If parameters are invalid or inconsistent
        """
        # Validate inputs first
        if not id or not isinstance(id, str):
            raise ValueError("Dimension id must be a non-empty string")

        unit = unit if isinstance(unit, UnitTerm) else UnitTerm(unit)

        # Infer type from unit if not provided
        if kind is None:
            kind = unit.to_dimension_type()
        else:
            kind = kind if isinstance(kind, DimensionType) else DimensionType(kind)

        self._validate_unit_type_consistency(unit, kind)

        # Create internal representation
        self._inner = _Dimension(id=id, unit=unit.value, type=kind.value)

    @staticmethod
    def _validate_unit_type_consistency(unit: UnitTerm, type: DimensionType) -> None:
        """Validate that unit and type are consistent."""
        # Rule: If type is "index", then unit MUST be "index"
        if type == DimensionType.INDEX and unit.value != "index":
            raise ValueError(
                f"Dimension type 'index' requires unit 'index', got '{unit.value}'"
            )

    @property
    def id(self) -> str:
        """Unique identifier for the dimension."""
        return self._inner.id

    @property
    def unit(self) -> UnitTerm:
        """Unit of measurement."""
        return UnitTerm(self._inner.unit)

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
            id = data["id"]
            unit = data["unit"]
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}") from e

        # Type is optional - will be inferred from unit if not provided
        kind = data.get("type", None)

        return cls(id=id, unit=unit, kind=kind)

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
