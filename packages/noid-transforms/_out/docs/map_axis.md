

# Slot: map_axis 


_Permutation vector of 0-based input dimension indices. Array length equals number of output dimensions. Each value specifies which input dimension maps to the corresponding output dimension._





URI: [noid_transform:map_axis](https://github.com/nclack/noid/schemas/transform/map_axis)
Alias: map_axis

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MapAxis](MapAxis.md) | Axis permutation transform |  no  |







## Properties

* Range: [Integer](Integer.md)

* Multivalued: True

* Required: True

* Minimum Value: 0





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/transform/v0.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transform:map_axis |
| native | noid_transform:map_axis |




## LinkML Source

<details>
```yaml
name: map-axis
description: Permutation vector of 0-based input dimension indices. Array length equals
  number of output dimensions. Each value specifies which input dimension maps to
  the corresponding output dimension.
from_schema: https://github.com/nclack/noid/schemas/transform/v0.linkml
rank: 1000
list_elements_ordered: true
alias: map_axis
owner: MapAxis
domain_of:
- MapAxis
range: integer
required: true
multivalued: true
minimum_value: 0

```
</details>