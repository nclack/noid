

# Slot: homogeneous 


_Homogeneous transformation matrix as 2D array_





URI: [noid_spaces:homogeneous](https://github.com/nclack/noid/schemas/space.v0.context.jsonldhomogeneous)
Alias: homogeneous

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Homogeneous](Homogeneous.md) | Homogeneous transformation matrix (affine/projective) |  no  |







## Properties

* Range: [Float](Float.md)

* Multivalued: True

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_spaces:homogeneous |
| native | noid_spaces:homogeneous |




## LinkML Source

<details>
```yaml
name: homogeneous
description: Homogeneous transformation matrix as 2D array
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
list_elements_ordered: true
alias: homogeneous
owner: Homogeneous
domain_of:
- Homogeneous
range: float
required: true
multivalued: true

```
</details>