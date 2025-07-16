

# Slot: mapAxis 


_Permutation vector of 0-based input dimension indices. Array length equals number of output dimensions. Each value specifies which input dimension maps to the corresponding output dimension._





URI: [noid_transforms:mapAxis](https://github.com/nclack/noid/transforms/mapAxis)
Alias: mapAxis

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


* from schema: https://github.com/nclack/noid/transforms/transforms.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transforms:mapAxis |
| native | noid_transforms:mapAxis |




## LinkML Source

<details>
```yaml
name: mapAxis
description: Permutation vector of 0-based input dimension indices. Array length equals
  number of output dimensions. Each value specifies which input dimension maps to
  the corresponding output dimension.
from_schema: https://github.com/nclack/noid/transforms/transforms.linkml
rank: 1000
alias: mapAxis
owner: MapAxis
domain_of:
- MapAxis
range: integer
required: true
multivalued: true
minimum_value: 0

```
</details>