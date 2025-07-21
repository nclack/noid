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

Dimensions within a coordinate system are assigned local identifiers based on their label parameter when provided, or sequential identifiers following the pattern `dim_{n}` where `n` is the zero-based index when no label is specified.

```
Dimension("mm", "space", label="AP") → "AP"
Dimension("mm", "space", label="ML") → "ML"
Dimension("mm", "space") → "dim_0" (fallback)
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
    def __init__(self, unit: str, type: str = None, label: str = None,
                 coordinate_system_id: str = None, id: str = None):
        """Initialize dimension with unit and coordinate system.

        Args:
            unit: Physical unit specification
            type: Dimension type (space, time, other, index)
            label: Human-readable label for local ID
            coordinate_system_id: Coordinate system this dimension belongs to
            id: Fully qualified dimension ID (alternative to coordinate_system_id + label)

        Raises:
            ValueError: If neither coordinate_system_id nor fully qualified id provided
        """
        self.unit = unit
        self.type = type

        if id:
            # Parse fully qualified ID
            cs_id, local_id = self.parse_dimension_id(id)
            if not cs_id:
                raise ValueError("Fully qualified dimension ID must include coordinate system")
            self._coordinate_system_id = cs_id
            self._local_id = local_id
            self.label = label or local_id
        elif coordinate_system_id and label:
            # Use provided coordinate system and label
            self._coordinate_system_id = coordinate_system_id
            self._local_id = label
            self.label = label
        else:
            raise ValueError(
                "Must provide either fully qualified 'id' or both 'coordinate_system_id' and 'label'"
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
            if dim._coordinate_system_id != id:
                raise ValueError(
                    f"Dimension belongs to coordinate system '{dim._coordinate_system_id}' "
                    f"but this coordinate system is '{id}'. All dimensions must belong "
                    f"to the same coordinate system."
                )

        self.id = id
        self.dimensions = dimensions
        self.description = description
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

```json
{
  "coordinate-system": {
    "@id": "mouse_123_native",
    "dimensions": [
      {
        "@id": "mouse_123_native#AP",
        "unit": "mm",
        "type": "space"
      },
      {
        "@id": "mouse_123_native#ML",
        "unit": "mm",
        "type": "space"
      }
    ]
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
  "dimension": {
    "@id": "mouse_123_native#AP",
    "unit": "mm",
    "type": "space"
  }
}
```

## 6. Validation Rules

### 6.1 Dimension Ownership

Each dimension instance can belong to at most one coordinate system. Attempting to add a dimension that already belongs to another coordinate system results in a ValueError.

### 6.2 Transform Chain Validation

Transform validation compares global dimension IDs to ensure proper axis mapping:

```python
def validate_dimension_compatibility(output_dim: Dimension, input_dim: Dimension) -> bool:
    """Validate dimension compatibility for transform chains."""
    return output_dim.id == input_dim.id
```

### 6.3 ID Consistency

Coordinate system ID changes require updating all associated dimension references. Implementations should either forbid coordinate system ID mutation or provide mechanisms to maintain consistency.

## 7. Usage Examples

### 7.1 Basic Usage

```python
# Method 1: Create dimensions with coordinate system ID
mouse_cs = CoordinateSystem(
    id="mouse_123_native",
    dimensions=[
        Dimension("mm", "space", label="AP", coordinate_system_id="mouse_123_native"),
        Dimension("mm", "space", label="ML", coordinate_system_id="mouse_123_native"),
        Dimension("mm", "space", label="DV", coordinate_system_id="mouse_123_native"),
    ]
)

# Method 2: Create dimensions with fully qualified IDs
atlas_cs = CoordinateSystem(
    id="allen_ccf_v3",
    dimensions=[
        Dimension("mm", "space", id="allen_ccf_v3#AP"),
        Dimension("mm", "space", id="allen_ccf_v3#ML"),
        Dimension("mm", "space", id="allen_ccf_v3#DV"),
    ]
)

# Access dimensions
AP, ML, DV = mouse_cs.dimensions
print(AP.id)        # "mouse_123_native#AP"
print(AP.local_id)  # "AP"
print(AP.label)     # "AP"
```

### 7.2 Dimension Reuse Prevention

```python
atlas_cs = CoordinateSystem(
    id="allen_ccf_v3",
    dimensions=[
        Dimension("mm", "space"),
        Dimension("mm", "space"),
        Dimension("mm", "space"),
    ]
)

# This raises ValueError
try:
    mixed_cs = CoordinateSystem(
        id="mixed",
        dimensions=[mouse_cs.dimensions[0], atlas_cs.dimensions[1]]
    )
except ValueError as e:
    # "Dimension already belongs to coordinate system 'mouse_123_native'"
    pass
```

### 7.3 Coordinate System Extraction

```python
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
