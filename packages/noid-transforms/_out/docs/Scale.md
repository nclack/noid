

# Slot: scale 


_Scale factors as array of numbers_





URI: [noid_transform:scale](https://github.com/nclack/noid/schemas/transform/scale)
Alias: scale

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Scale](Scale.md) | Scale transform |  no  |







## Properties

* Range: [Float](Float.md)

* Multivalued: True

* Required: True

* Minimum Value: 1





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/transform/v0.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transform:scale |
| native | noid_transform:scale |




## LinkML Source

<details>
```yaml
name: scale
description: Scale factors as array of numbers
from_schema: https://github.com/nclack/noid/schemas/transform/v0.linkml
rank: 1000
list_elements_ordered: true
alias: scale
owner: Scale
domain_of:
- Scale
range: float
required: true
multivalued: true
minimum_value: 1

```
</details>