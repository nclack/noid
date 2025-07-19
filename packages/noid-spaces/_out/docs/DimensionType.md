# Enum: DimensionType 




_Classification of dimension types_



URI: [DimensionType](DimensionType.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| space | noid_spaces:SpatialDimension | Spatial dimensions |
| time | noid_spaces:TemporalDimension | Temporal dimensions |
| other | noid_spaces:OtherDimension | Channels, indices, categories |
| index | noid_spaces:IndexDimension | Array index dimensions |




## Slots

| Name | Description |
| ---  | --- |
| [type](type.md) | Dimension type classification |






## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml






## LinkML Source

<details>
```yaml
name: DimensionType
description: Classification of dimension types
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
permissible_values:
  space:
    text: space
    description: Spatial dimensions
    meaning: noid_spaces:SpatialDimension
  time:
    text: time
    description: Temporal dimensions
    meaning: noid_spaces:TemporalDimension
  other:
    text: other
    description: Channels, indices, categories
    meaning: noid_spaces:OtherDimension
  index:
    text: index
    description: Array index dimensions
    meaning: noid_spaces:IndexDimension

```
</details>
