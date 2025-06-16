# Transform Data Model - Tabular Reference

## Transform Types Overview

| Transform Type | Property Name | Parameter Type | Description |
|---|---|---|---|
| Identity | `identity` | Array (empty) | No transformation applied |
| Translation | `translation` | Array of numbers | Shift coordinates by offset vector |
| Scale | `scale` | Array of positive numbers | Scale coordinates by factor(s) |
| Axis Mapping | `mapAxis` | Object (string → string) | Remap axis names between coordinate spaces |
| Homogeneous | `homogeneous` | 2D Array of numbers | Apply homogeneous transformation matrix (affine/projective) |
| Displacements | `displacements` | String or Object | Apply displacement field from file |
| Coordinates | `coordinates` | Object | Apply coordinate lookup table from file |

## Parameter Specifications

### Identity Transform
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `identity` | Array | Yes | Must be empty array `[]` | Identity transformation |

### Translation Transform
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `translation` | Array | Yes | ≥1 numeric elements | Translation vector |

### Scale Transform
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `scale` | Array | Yes | ≥1 positive numeric elements | Scale factors (must be > 0) |

### Axis Mapping Transform
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `mapAxis` | Object | Yes | ≥1 string key-value pairs | Input axis → output axis mapping |

**mapAxis Object Constraints:**
- Keys: Valid identifier pattern (`^[a-zA-Z_][a-zA-Z0-9_]*$`)
- Values: Valid identifier pattern (`^[a-zA-Z_][a-zA-Z0-9_]*$`)

### Homogeneous Transform
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `homogeneous` | 2D Array | Yes | ≥2 rows of numeric arrays | Homogeneous transformation matrix (affine/projective) |

### Displacements Transform
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `displacements` | String or Object | Yes | See displacement object spec | Path or configuration for displacement field |

**Displacement Object (when object form is used):**
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `path` | String | Yes | Valid file path | Path to displacement field file |
| `interpolation` | String | No | `"linear"`, `"nearest"`, `"cubic"` | Interpolation method |
| `extrapolation` | String | No | `"nearest"`, `"zero"`, `"constant"` | Extrapolation method |

### Coordinates Transform
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `coordinates` | Object | Yes | See coordinates object spec | Configuration for coordinate lookup |

**Coordinates Object:**
| Property | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `lookup_table` | String | Yes | Valid file path | Path to coordinate lookup table file |
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
| `sequence` | 1 | Transform object | Must be valid transforms |

### String Pattern Constraints
| Context | Pattern | Description |
|---|---|---|
| `mapAxis` keys | `^[a-zA-Z_][a-zA-Z0-9_]*$` | Valid identifier starting with letter or underscore |
| `mapAxis` values | `^[a-zA-Z_][a-zA-Z0-9_]*$` | Valid identifier starting with letter or underscore |

### Enumerated Values
| Property | Valid Values |
|---|---|
| `interpolation` | `"linear"`, `"nearest"`, `"cubic"` |
| `extrapolation` | `"nearest"`, `"zero"`, `"constant"` |

## Example Value Formats

| Transform Type | Example Value |
|---|---|
| Identity | `{"identity": []}` |
| Translation | `{"translation": [10, 20, 5]}` |
| Scale | `{"scale": [2.0, 1.5, 0.5]}` |
| Axis Mapping | `{"mapAxis": {"x": "y", "y": "x", "z": "z"}}` |
| Homogeneous | `{"homogeneous": [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]}` |
| Displacements (string) | `{"displacements": "path/to/displacement_field.zarr"}` |
| Displacements (object) | `{"displacements": {"path": "field.zarr", "interpolation": "linear"}}` |
| Coordinates | `{"coordinates": {"lookup_table": "path/to/lut.zarr", "interpolation": "linear"}}` |
