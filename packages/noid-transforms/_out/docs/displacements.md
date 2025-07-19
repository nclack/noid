

# Slot: displacements 


_Displacement field configuration_





URI: [noid_transform:displacements](https://github.com/nclack/noid/schemas/transform/displacements)
Alias: displacements

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DisplacementLookupTable](DisplacementLookupTable.md) | Displacement field lookup table transform |  no  |







## Properties

* Range: [SamplerConfig](SamplerConfig.md)





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/transform/v0.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transform:displacements |
| native | noid_transform:displacements |




## LinkML Source

<details>
```yaml
name: displacements
description: Displacement field configuration
from_schema: https://github.com/nclack/noid/schemas/transform/v0.linkml
rank: 1000
alias: displacements
owner: DisplacementLookupTable
domain_of:
- DisplacementLookupTable
range: SamplerConfig

```
</details>