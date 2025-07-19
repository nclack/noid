# Coordinate System and Transform Data Model

## Schema Components Overview

| Component | Description | Key Properties |
|---|---|---|
| Dimension | A single axis within a coordinate space | `id`, `unit`, `type` |
| Coordinate System | Collection of dimensions defining a coordinate space | `id`, `dimensions`, `description` |
| Coordinate Transform | Mapping between input and output coordinate spaces | `id`, `input`, `output`, `transform`, `description` |

## Example Value Formats

| Component | Example Value |
|---|---|
| Dimension | `{"id": "x", "unit": "micrometers", "type": "space"}` |
| Coordinate System | `{"id": "physical_space", "dimensions": ["x", "y", "z"]}` |
| Coordinate Transform | `{"id": "physical_to_pixel", "input": "physical_space", "output": "image_coordinates", "transform": {"scale": [0.1, 0.1, 0.2]}}` |

## Component Specifications

### Dimension

**Example:** `{"id": "x", "unit": "micrometers", "type": "space"}`

Defines a single axis within a coordinate space with its measurement unit and classification.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `id` | String | Yes | Non-empty, unique across dataset | Unique identifier for the dimension |
| `unit` | String | Yes | Non-empty | Unit of measurement |
| `type` | String | Yes | `"space"`, `"time"`, `"other"`, `"index"` | Dimension type classification |

**Unit Constraints:**
| Dimension Type | Unit Requirements |
|---|---|
| `"space"`, `"time"` | SHOULD use UDUNITS-2 terms (e.g., "micrometers", "seconds", "radians") |
| All types | "index" and "arbitrary" are valid |
| `"index"` type | MUST use "index" unit |

**Type Constraints:**
- Dimensions with unit "index" MAY have any type
- Dimensions with type "index" MUST have unit "index"

### Coordinate System

**Example:** `{"id": "physical_space", "dimensions": ["x", "y", "z"], "description": "3D physical coordinate system"}`

Collection of dimensions that together define a coordinate space for positioning data elements.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `id` | String | Yes | Non-empty, unique across dataset | Unique identifier for the coordinate system |
| `dimensions` | Array | Yes | ≥1 element | List of dimension specifications |
| `description` | String | No | Non-empty if present | Optional description of the coordinate system |

**Dimensions Array:**
Each element must be either:
- String: Reference to a dimension by its ID
- Object: Complete Dimension object (see Dimension specification above)

**Examples of dimension specifications:**
- By reference: `["x", "y", "z"]`
- Inline objects: `[{"id": "row", "unit": "index", "type": "index"}, {"id": "col", "unit": "index", "type": "index"}]`
- Mixed: `["x", "y", {"id": "channel", "unit": "arbitrary", "type": "other"}]`

### Coordinate Transform

**Example:** `{"id": "physical_to_pixel", "input": "physical_space", "output": "image_coordinates", "transform": {"scale": [0.1, 0.1, 0.2]}}`

Mathematical mapping between input and output coordinate spaces with transform definition.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `id` | String | Yes | Non-empty, unique across dataset | Unique identifier for the coordinate transform |
| `input` | String, Array, or Object | Yes | See input/output specification | Input coordinate space specification |
| `output` | String, Array, or Object | Yes | See input/output specification | Output coordinate space specification |
| `transform` | Object | Yes | Valid transform from transforms schema | Transform definition |
| `description` | String | No | Non-empty if present | Optional description of the coordinate transform |

**Input/Output Specifications:**
Each must be one of:
- String: Reference to a coordinate system by its ID
- Array: List of dimension specifications (strings or Dimension objects)
- Object: Complete Coordinate System object

**Transform Property:**
Must reference a valid transform definition from the transforms vocabulary as specified in `../transforms/transforms.v0.schema.json#/definitions/Transform`.

## Dimension Type Reference

| Type | Description | Typical Units | Examples |
|---|---|---|---|
| `"space"` | Spatial dimensions | UDUNITS-2 spatial terms | "micrometers", "millimeters", "meters" |
| `"time"` | Temporal dimensions | UDUNITS-2 time terms | "seconds", "milliseconds", "hours" |
| `"other"` | Channels, indices, categories | "arbitrary", "index", custom | "arbitrary", "wavelength", "intensity" |
| `"index"` | Array index dimensions | "index" (required) | "index" |

## Common Unit Examples

| Category | Valid Units |
|---|---|
| Spatial | "micrometers", "millimeters", "meters", "pixels", "nanometers" |
| Temporal | "seconds", "milliseconds", "hours", "minutes" |
| Angular | "radians", "degrees" |
| Universal | "index", "arbitrary" |
| Index Type | "index" (only valid unit for type "index") |

## Schema Rules

### General Constraints

| Rule | Description |
|---|---|
| Unique IDs | All IDs must be unique within their scope (dimensions, coordinate systems, transforms) |
| Non-empty Strings | All string properties must be non-empty |
| No Additional Properties | Objects cannot contain properties other than those specified |
| Reference Validation | ID references should exist within the dataset scope |

### Array Constraints

| Component | Property | Minimum Items | Item Types |
|---|---|---|---|
| Coordinate System | `dimensions` | 1 | String (ID reference) or Dimension object |
| Dimension (in arrays) | N/A | N/A | Complete Dimension object or string ID |

### Type Validation Rules

| Validation | Rule | Example |
|---|---|---|
| Index Type Constraint | If `type` is "index", then `unit` MUST be "index" | `{"id": "i", "unit": "index", "type": "index"}` ✓ |
| Index Unit Flexibility | If `unit` is "index", `type` can be any valid type | `{"id": "spatial_idx", "unit": "index", "type": "space"}` ✓ |
| UDUNITS-2 Recommendation | Space/time types SHOULD use UDUNITS-2 terms | `{"id": "x", "unit": "micrometers", "type": "space"}` ✓ |

### Invalid Examples

| Invalid Case | Example | Reason |
|---|---|---|
| Index type with non-index unit | `{"id": "bad", "unit": "micrometers", "type": "index"}` | Index type requires "index" unit |
| Empty dimensions array | `{"id": "sys", "dimensions": []}` | Must have at least one dimension |
| Missing required property | `{"id": "dim", "type": "space"}` | Missing required "unit" property |
| Empty string ID | `{"id": "", "unit": "index", "type": "index"}` | ID cannot be empty |

## Coordinate Transform Examples

### Simple System Reference
```json
{
  "id": "transform_1",
  "input": "world_coordinates",
  "output": "pixel_coordinates",
  "transform": {"scale": [0.1, 0.1]}
}
```

### Inline Dimension Arrays
```json
{
  "id": "transform_2",
  "input": [
    {"id": "x_world", "unit": "micrometers", "type": "space"},
    {"id": "y_world", "unit": "micrometers", "type": "space"}
  ],
  "output": [
    {"id": "row", "unit": "index", "type": "index"},
    {"id": "col", "unit": "index", "type": "index"}
  ],
  "transform": {"homogeneous": [[0.1, 0, 100], [0, 0.1, 200], [0, 0, 1]]}
}
```

### Mixed References
```json
{
  "id": "transform_3",
  "input": ["x", "y", "z"],
  "output": "image_space",
  "transform": {"translation": [10, 20, 5]},
  "description": "Convert 3D coordinates to image space with offset"
}
```
