# Transform Data Model

## Transform Types Overview

| Transform Type | Property Name | Parameter Type | Description |
|---|---|---|---|
| Identity | `identity` | Array (empty) | No transformation applied |
| Translation | `translation` | Array of numbers | Shift coordinates by offset vector |
| Scale | `scale` | Array of positive numbers | Scale coordinates by factor(s) |
| Axis Mapping | `mapAxis` | Array of integers | Permutation vector specifying input dimension indices |
| Homogeneous | `homogeneous` | 2D Array of numbers | Apply homogeneous transformation matrix (affine/projective) |
| DisplacementLookupTable | `displacements` | String or Object | Apply displacement field from file |
| CoordinateLookupTable | `lookup_table` | String or Object | Apply coordinate lookup table from file |

## Example Value Formats

| Transform Type | Example Value |
|---|---|
| Identity | `"identity"` |
| Translation | `{"translation": [10, 20, 5]}` |
| Scale | `{"scale": [2.0, 1.5, 0.5]}` |
| Axis Mapping | `{"mapAxis": [1, 0, 2]}` |
| Homogeneous | `{"homogeneous": [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]}` |
| Displacements (string) | `{"displacements": "path/to/displacement_field.zarr"}` |
| Displacements (object) | `{"displacements": {"path": "field.zarr", "interpolation": "linear"}}` |
| Coordinates | `{"lookup_table": {"path": "path/to/lut.zarr", "interpolation": "linear"}}` |

## Parameter Specifications

### Identity Transform

**Example:** `"identity"`

Applies no transformation - coordinates remain unchanged.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| Identity string | String | Yes | Must be `"identity"` | Identity transformation |

### Translation Transform

**Example:** `{"translation": [10, 20, 5]}`

Shifts coordinates by adding the translation vector. A 3D point at (0, 0, 0) becomes (10, 20, 5).

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `translation` | Array | Yes | ≥1 numeric elements | Translation vector |

### Scale Transform

**Example:** `{"scale": [2.0, 1.5, 0.5]}`

Multiplies coordinates by scale factors. A 3D point at (1, 2, 4) becomes (2, 3, 2).

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `scale` | Array | Yes | ≥1 positive numeric elements | Scale factors (must be > 0) |

### Axis Mapping Transform

**Example:** `{"mapAxis": [1, 0, 2]}`

Reorders dimensions - swaps first two dimensions while keeping third unchanged. A 3D point at (x, y, z) becomes (y, x, z).

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `mapAxis` | Array | Yes | ≥1 non-negative integer elements | Permutation vector of 0-based input dimension indices |

**mapAxis Array Constraints:**
- Elements: Non-negative integers (≥ 0)
- Length: Determines number of output dimensions
- Values: 0-based indices of input dimensions

### Homogeneous Transform

**Example:** `{"homogeneous": [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]}`

Applies matrix transformation in homogeneous coordinates. This example scales by (2, 1.5, 0.5) and translates by (10, 20, 5).

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `homogeneous` | 2D Array | Yes | ≥2 rows of numeric arrays | Homogeneous transformation matrix (affine/projective) |

### DisplacementLookupTable Transform

**Example:** `{"displacements": "path/to/displacement_field.zarr"}` or `{"displacements": {"path": "field.zarr", "interpolation": "linear"}}`

Applies spatially-varying displacement vectors from a lookup table. Used for non-linear deformations like image warping.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `displacements` | String or Object | Yes | See displacement object spec | Path or configuration for displacement field |

**Displacement Object (when object form is used):**
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `path` | String | Yes | Valid file path | Path to displacement field file |
| `interpolation` | String | No | `"linear"`, `"nearest"`, `"cubic"` | Interpolation method |
| `extrapolation` | String | No | `"nearest"`, `"zero"`, `"constant"` | Extrapolation method |

### CoordinateLookupTable Transform

**Example:** `{"lookup_table": {"path": "path/to/lut.zarr", "interpolation": "linear"}}`

Maps coordinates through a lookup table that directly specifies output coordinates for each input position.

| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `lookup_table` | String or Object | Yes | See lookup table object spec | Path or configuration for coordinate lookup table |

**Lookup Table Object (when object form is used):**
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `path` | String | Yes | Valid file path | Path to coordinate lookup table file |
| `interpolation` | String | No | `"linear"`, `"nearest"`, `"cubic"` | Interpolation method |
| `extrapolation` | String | No | `"nearest"`, `"zero"`, `"constant"` | Extrapolation method |

## Schema Rules

### General Constraints

| Rule | Description |
|---|---|
| Single Property | Each transform object must contain exactly one transform property |
| No Additional Properties | Transform objects cannot contain properties other than the specified transform property |
| Finite Numbers | All numeric values must be finite (not NaN or infinity) |
| Self-Describing | Transform type is inferred from property name, not explicit type field |

### Array Constraints

| Transform | Minimum Items | Item Type | Additional Constraints |
|---|---|---|---|
| `identity` | 0 (empty) | N/A | Must be exactly empty |
| `translation` | 1 | Number | None |
| `scale` | 1 | Number | Must be > 0 |
| `homogeneous` | 2 | Array of numbers | 2D matrix structure |

### Integer Constraints

| Context | Constraint | Description |
|---|---|---|
| `mapAxis` elements | `≥ 0` | Non-negative integers representing 0-based dimension indices |

### Enumerated Values

| Property | Valid Values |
|---|---|
| `interpolation` | `"linear"`, `"nearest"`, `"cubic"` |
| `extrapolation` | `"nearest"`, `"zero"`, `"constant"` |
