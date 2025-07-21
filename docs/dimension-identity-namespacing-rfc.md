# Dimension Identity and Namespacing Specification

## Abstract

This specification defines a system for creating globally unique dimension identifiers within coordinate systems while maintaining local readability. Dimensions are automatically assigned local identifiers and namespaced by their containing coordinate system using IRI fragment syntax.

## 1. Introduction

Scientific coordinate transformations require unambiguous dimension identity to prevent incorrect axis mappings between coordinate systems. This specification addresses the need for:

- Globally unique dimension identifiers
- Automatic dimension naming to eliminate conflicts
- Extraction of coordinate system information from dimension identifiers
- Validation of dimension ownership across coordinate systems

## 2. Terminology

- **Local ID**: The identifier assigned to a dimension within its coordinate system (e.g., `dim_0`)
- **Global ID**: The fully qualified identifier combining coordinate system ID and local ID (e.g., `mouse_123#dim_0`)
- **Coordinate System ID**: The unique identifier for a coordinate system
- **IRI Fragment**: The portion of an IRI following the `#` character

## 3. Dimension Identity Model

### 3.1 Local ID Assignment

Dimensions within a coordinate system are assigned local identifiers based on their label parameter when provided, or sequential identifiers following the pattern `dim_{n}` where `n` is the zero-based index when no label is specified. Auto-labeling occurs during coordinate system construction via the `add_dimension()` method.

```
Dimension(unit="mm", kind="space", label="AP") → "AP"
Dimension(unit="mm", kind="space", label="ML") → "ML"
# Auto-generated via CoordinateSystem.add_dimension():
cs.add_dimension(unit="mm", kind="space") → "dim_0" (auto-labeled)
```

### 3.2 Global ID Construction

Global dimension identifiers are constructed using IRI fragment syntax:

```
global_id = coordinate_system_id + "#" + local_id
```

Example:
```
"mouse_123_native#AP"
"allen_ccf_v3#ML"
```

### 3.3 Dynamic Generation

Global IDs are generated dynamically rather than stored to avoid data redundancy and maintain consistency when coordinate system identifiers change.

## 4. Implementation Requirements

### 4.1 Dimension Class

```python
class Dimension:
    def __init__(self, unit: str | Unit, kind: str | DimensionType = None,
                 label: str = None, coordinate_system: "CoordinateSystem" = None,
                 dimension_id: str = None):
        """Initialize dimension with unit and coordinate system.

        Args:
            unit: Physical unit specification (string or Unit object)
            kind: Dimension type (space, time, other, index) - inferred from unit if None
            label: Human-readable label for local ID (auto-generated if None and coordinate_system provided)
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

        # Handle dimension identity according to coordinate system namespacing rules
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
```

### 4.2 CoordinateSystem Class

```python
class CoordinateSystem:
    def __init__(self, dimensions: list[Dimension], id: str = None,
                 description: str = None):
        """Initialize coordinate system with dimensions.

        Args:
            dimensions: List of Dimension instances
            id: Coordinate system identifier
            description: Optional description

        Raises:
            ValueError: If any dimension already belongs to another coordinate system
        """
        # Validate dimension ownership consistency
        for dim in dimensions:
            if (hasattr(dim, "_coordinate_system_id") and dim._coordinate_system_id
                and dim._coordinate_system_id != id):
                raise ValueError(
                    f"Dimension '{dim.local_id}' belongs to coordinate system '{dim._coordinate_system_id}' "
                    f"but this coordinate system is '{id}'. All dimensions must belong "
                    f"to the same coordinate system."
                )

        self.id = id
        self.dimensions = dimensions
        self.description = description

        # Initialize auto-labeling counter
        self._auto_label_counter = 0
        self._used_labels = {dim.local_id for dim in dimensions if hasattr(dim, "local_id")}

    def add_dimension(self, unit: str | Unit, kind: str | DimensionType = None,
                     label: str = None) -> "Dimension":
        """Add a new dimension to this coordinate system with optional auto-labeling.

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

        # Register the label as used
        if not label:  # Auto-generated label was already registered in constructor
            pass
        else:  # Explicit label needs to be registered
            self._register_dimension_label(dim.label)

        # Add to our dimensions list
        self.dimensions.append(dim)
        return dim

    def _generate_dimension_label(self) -> str:
        """Generate an automatic dimension label (dim_0, dim_1, etc.)."""
        while True:
            label = f"dim_{self._auto_label_counter}"
            if label not in self._used_labels:
                return label
            self._auto_label_counter += 1

    def _register_dimension_label(self, label: str) -> None:
        """Register a dimension label as used."""
        self._used_labels.add(label)
```

### 4.3 Dimension ID Parsing

```python
@staticmethod
def parse_dimension_id(dim_id: str) -> tuple[str | None, str]:
    """Parse dimension ID into coordinate system and local components.

    Args:
        dim_id: Dimension identifier to parse

    Returns:
        Tuple of (coordinate_system_id, local_id)

    Examples:
        "mouse_123#AP" → ("mouse_123", "AP")
        "AP" → (None, "AP")
    """
    if '#' in dim_id:
        cs_id, local_id = dim_id.split('#', 1)
        return cs_id, local_id
    else:
        return None, dim_id
```

### 4.4 Coordinate System Extraction

```python
def extract_coordinate_system_id(dimensions: list[Dimension]) -> str | None:
    """Extract coordinate system ID from a set of dimensions.

    Args:
        dimensions: List of dimensions to analyze

    Returns:
        Coordinate system ID if all dimensions belong to same system, None otherwise

    Raises:
        ValueError: If dimensions belong to multiple coordinate systems
    """
    cs_ids = set()
    for dim in dimensions:
        if dim.coordinate_system_id:
            cs_ids.add(dim.coordinate_system_id)

    if len(cs_ids) == 0:
        return None
    elif len(cs_ids) == 1:
        return cs_ids.pop()
    else:
        raise ValueError(
            f"Dimensions belong to multiple coordinate systems: {cs_ids}"
        )
```

## 5. JSON-LD Representation

### 5.1 Coordinate System Serialization

The actual JSON-LD output from the noid-spaces implementation:

```json
{
  "@context": {
    "spac": "https://github.com/nclack/noid/schemas/space/"
  },
  "spac:coordinate-system": {
    "dimensions": [
      {
        "id": "mouse_123_native#AP",
        "unit": "mm",
        "type": "space"
      },
      {
        "id": "mouse_123_native#ML",
        "unit": "mm",
        "type": "space"
      }
    ],
    "id": "mouse_123_native",
    "description": "Mouse coordinate system"
  }
}
```

### 5.1.1 Compact Form with JSON-LD Context

JSON-LD context can enable short dimension names that expand to full IRIs:

```json
{
  "@context": {
    "coordinate-system": "https://github.com/nclack/noid/schemas/space/coordinate-system",
    "dimensions": {
      "@container": "@id",
      "@context": {
        "@base": "mouse_123_native#"
      }
    }
  },
  "coordinate-system": {
    "@id": "mouse_123_native",
    "dimensions": [
      {
        "@id": "AP",
        "unit": "mm",
        "type": "space"
      },
      {
        "@id": "ML",
        "unit": "mm",
        "type": "space"
      }
    ]
  }
}
```

### 5.1.2 Alternative JSON-LD Constructions

**Array-based dimensions with relative IRIs:**
```json
{
  "@context": {
    "@base": "https://lab.example.com/",
    "coordinate-system": "space/coordinate-system"
  },
  "coordinate-system": {
    "@id": "mouse_123_native",
    "dimensions": [
      "mouse_123_native#AP",
      "mouse_123_native#ML",
      "mouse_123_native#DV"
    ]
  }
}
```

**Nested context for dimension properties:**
```json
{
  "@context": {
    "cs": "https://github.com/nclack/noid/schemas/space/",
    "dims": {
      "@id": "cs:dimensions",
      "@container": "@list",
      "@context": {
        "@base": "mouse_123_native#",
        "unit": "cs:unit",
        "type": "cs:type"
      }
    }
  },
  "@id": "mouse_123_native",
  "@type": "cs:CoordinateSystem",
  "dims": [
    {
      "@id": "AP",
      "unit": "mm",
      "type": "space"
    },
    {
      "@id": "ML",
      "unit": "mm",
      "type": "space"
    }
  ]
}
```

**Graph-based representation:**
```json
{
  "@context": {
    "cs": "https://github.com/nclack/noid/schemas/space/"
  },
  "@graph": [
    {
      "@id": "mouse_123_native",
      "@type": "cs:CoordinateSystem",
      "cs:dimensions": [
        {"@id": "mouse_123_native#AP"},
        {"@id": "mouse_123_native#ML"},
        {"@id": "mouse_123_native#DV"}
      ]
    },
    {
      "@id": "mouse_123_native#AP",
      "@type": "cs:Dimension",
      "cs:unit": "mm",
      "cs:type": "space"
    },
    {
      "@id": "mouse_123_native#ML",
      "@type": "cs:Dimension",
      "cs:unit": "mm",
      "cs:type": "space"
    },
    {
      "@id": "mouse_123_native#DV",
      "@type": "cs:Dimension",
      "cs:unit": "mm",
      "cs:type": "space"
    }
  ]
}
```

### 5.2 Dimension Serialization

When serializing dimensions outside of coordinate system context, the global ID preserves namespace information:

```json
{
  "@context": {
    "spac": "https://github.com/nclack/noid/schemas/space/"
  },
  "spac:dimension": {
    "id": "mouse_123_native#AP",
    "unit": "mm",
    "type": "space"
  }
}
```

## 6. Validation Rules

### 6.1 Dimension Ownership

Each dimension instance can belong to at most one coordinate system. Attempting to add a dimension that already belongs to another coordinate system results in a ValueError.

### 6.2 Transform Chain Validation

Transform validation uses a sophisticated 4-tier compatibility system to validate dimension mappings in transform chains:

```python
def validate_dimension_id_compatibility(output_dim: Dimension, input_dim: Dimension,
                                      strict: bool = True) -> None:
    """Validate dimension compatibility for transform chains with 4-tier logic."""
    # 1. IDEAL: Same global dimension ID - perfect match
    if output_dim.id == input_dim.id:
        return  # Perfect match - no issues

    # 2. COMPATIBLE: Same local ID with compatible coordinate systems
    if output_dim.local_id == input_dim.local_id:
        if (output_dim.coordinate_system_id is not None and
            input_dim.coordinate_system_id is not None):
            return  # Compatible - same local meaning, different coordinate systems

    # 3. COMPATIBLE: Different local IDs but same semantic meaning
    if (output_dim.type == input_dim.type and
        output_dim.unit.value == input_dim.unit.value):
        # Same semantic meaning - this is compatible, no warning needed
        return

    # 4. INCOMPATIBLE: Completely different dimensions
    if (output_dim.type != input_dim.type or
        output_dim.unit.value != input_dim.unit.value):
        message = (
            f"Incompatible dimensions at transform {transform_index}, dimension {dimension_index}: "
            f"output dimension '{output_dim.id}' ({output_dim.type}, {output_dim.unit.value}) "
            f"vs input dimension '{input_dim.id}' ({input_dim.type}, {input_dim.unit.value})"
        )
        if strict:
            raise ValidationError(message)
        else:
            warnings.warn(message, ValidationWarning, stacklevel=3)
```

### 6.3 ID Consistency

Coordinate system ID changes require updating all associated dimension references. Implementations should either forbid coordinate system ID mutation or provide mechanisms to maintain consistency.

## 7. Usage Examples

### 7.1 Basic Usage

```python
from noid_spaces import coordinate_system
from noid_spaces.models import CoordinateSystem, Dimension

# Method 1: Using the factory function (recommended)
mouse_cs = coordinate_system(
    dimensions=[
        {"id": "AP", "unit": "mm", "type": "space"},
        {"id": "ML", "unit": "mm", "type": "space"},
        {"id": "DV", "unit": "mm", "type": "space"},
    ],
    id="mouse_123_native",
    description="Mouse native coordinate system"
)

# Method 2: Using add_dimension with auto-labeling
atlas_cs = CoordinateSystem(id="allen_ccf_v3", dimensions=[])
ap_dim = atlas_cs.add_dimension(unit="mm", kind="space", label="AP")
ml_dim = atlas_cs.add_dimension(unit="mm", kind="space", label="ML")
dv_dim = atlas_cs.add_dimension(unit="mm", kind="space")  # Auto-labeled as "dim_2"

# Method 3: Direct dimension creation with fully qualified IDs
pixel_cs = CoordinateSystem(
    id="raw_data",
    dimensions=[
        Dimension(unit="pixel", dimension_id="raw_data#x"),
        Dimension(unit="pixel", dimension_id="raw_data#y"),
        Dimension(unit="ms", dimension_id="raw_data#time"),
    ]
)

# Access dimensions
AP, ML, DV = mouse_cs.dimensions
print(AP.id)        # "mouse_123_native#AP"
print(AP.local_id)  # "AP"
print(AP.label)     # "AP"
print(DV.type)      # DimensionType.SPACE (inferred from unit)
```

### 7.2 Dimension Reuse Prevention

```python
from noid_spaces.models import CoordinateSystem, Dimension

# Create coordinate systems with auto-labeling
atlas_cs = CoordinateSystem(id="allen_ccf_v3", dimensions=[])
atlas_cs.add_dimension(unit="mm", kind="space")  # Auto-labeled as "dim_0"
atlas_cs.add_dimension(unit="mm", kind="space")  # Auto-labeled as "dim_1"
atlas_cs.add_dimension(unit="mm", kind="space")  # Auto-labeled as "dim_2"

# This raises ValueError - dimension objects cannot be shared between coordinate systems
try:
    mixed_cs = CoordinateSystem(
        id="mixed",
        dimensions=[mouse_cs.dimensions[0], atlas_cs.dimensions[1]]  # Reusing dimension objects
    )
except ValueError as e:
    # "Dimension 'AP' belongs to coordinate system 'mouse_123_native' but this coordinate system is 'mixed'"
    pass

# Correct approach: Create new dimension objects with same properties
mixed_cs = CoordinateSystem(
    id="mixed",
    dimensions=[
        Dimension(unit="mm", kind="space", dimension_id="mixed#AP"),  # New dimension object
        Dimension(unit="mm", kind="space", dimension_id="mixed#ML"),  # New dimension object
    ]
)
```

### 7.3 Factory Function with Auto-labeling

```python
from noid_spaces import coordinate_system

# Auto-labeling when IDs not provided
cs = coordinate_system(
    dimensions=[
        {"unit": "pixel", "type": "space"},    # Auto-labeled as "dim_0"
        {"unit": "pixel", "type": "space"},    # Auto-labeled as "dim_1"
        {"id": "time", "unit": "ms", "type": "time"},  # Explicit ID
    ],
    id="image-coords"
)
print(cs.dimensions[0].id)  # "image-coords#dim_0"
print(cs.dimensions[1].id)  # "image-coords#dim_1"
print(cs.dimensions[2].id)  # "image-coords#time"

# Mixed explicit and auto-generated IDs with type inference
cs2 = coordinate_system(
    dimensions=[
        {"id": "x", "unit": "mm"},        # Explicit ID, inferred type
        {"unit": "mm"},                   # Auto ID, inferred type
        {"id": "time", "unit": "ms"}      # Explicit ID, inferred type
    ],
    id="mixed-system"
)
print(cs2.dimensions[0].type)  # DimensionType.SPACE (inferred)
print(cs2.dimensions[1].id)    # "mixed-system#dim_0"
print(cs2.dimensions[2].type)  # DimensionType.TIME (inferred)
```

### 7.4 JSON-LD Serialization

```python
from noid_spaces import coordinate_system, to_jsonld, from_jsonld

# Create coordinate system with namespaced dimensions
cs = coordinate_system(
    dimensions=[
        {"id": "x", "unit": "mm", "type": "space"},
        {"unit": "mm", "type": "space"},  # Auto-labeled
    ],
    id="test-system"
)

# Serialize to JSON-LD
jsonld_data = to_jsonld(cs)
print(jsonld_data)
# Output:
# {
#   "@context": {"spac": "https://github.com/nclack/noid/schemas/space/"},
#   "spac:coordinate-system": {
#     "dimensions": [
#       {"id": "test-system#x", "unit": "mm", "type": "space"},
#       {"id": "test-system#dim_0", "unit": "mm", "type": "space"}
#     ],
#     "id": "test-system"
#   }
# }

# Deserialize from JSON-LD
jsonld_result = from_jsonld(jsonld_data)
cs_key = [k for k in jsonld_result.keys() if "coordinate-system" in k][0]
reconstructed_cs = jsonld_result[cs_key]
print(reconstructed_cs.dimensions[0].id)  # "test-system#x"
print(reconstructed_cs.dimensions[1].id)  # "test-system#dim_0"
```

### 7.5 Coordinate System Extraction

```python
from noid_spaces.models import extract_coordinate_system_id

dimensions = [some_dimension_list]
cs_id = extract_coordinate_system_id(dimensions)
if cs_id:
    print(f"All dimensions belong to: {cs_id}")
```

## 8. Security Considerations

This specification does not introduce security vulnerabilities. Standard precautions for identifier validation and input sanitization apply when processing coordinate system and dimension identifiers from external sources.

## 9. References

- RFC 3986: Uniform Resource Identifier (URI): Generic Syntax
- JSON-LD 1.1: A JSON-based Serialization for Linked Data
