

# Slot: unit 


_Unit of measurement from controlled vocabulary_





URI: [noid_spaces:unit](https://github.com/nclack/noid/schemas/space.v0.context.jsonldunit)
Alias: unit

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Dimension](Dimension.md) | A single axis within a coordinate space with its measurement unit and classif... |  no  |







## Properties

* Range: [UnitTerm](UnitTerm.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_spaces:unit |
| native | noid_spaces:unit |




## LinkML Source

<details>
```yaml
name: unit
description: Unit of measurement from controlled vocabulary
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
alias: unit
owner: Dimension
domain_of:
- Dimension
range: UnitTerm
required: true

```
</details>