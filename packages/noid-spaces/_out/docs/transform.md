

# Slot: transform 


_Transform definition from noid_transform schema_





URI: [noid_spaces:transform](https://github.com/nclack/noid/schemas/space.v0.context.jsonldtransform)
Alias: transform

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CoordinateTransform](CoordinateTransform.md) | Mathematical mapping between input and output coordinate spaces with transfor... |  no  |







## Properties

* Range: [Transform](Transform.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_spaces:transform |
| native | noid_spaces:transform |




## LinkML Source

<details>
```yaml
name: transform
description: Transform definition from noid_transform schema
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
alias: transform
owner: CoordinateTransform
domain_of:
- CoordinateTransform
range: Transform
required: true

```
</details>