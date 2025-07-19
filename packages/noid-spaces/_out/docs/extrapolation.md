

# Slot: extrapolation 


_Extrapolation method_





URI: [noid_spaces:extrapolation](https://github.com/nclack/noid/schemas/space.v0.context.jsonldextrapolation)
Alias: extrapolation

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SamplerConfig](SamplerConfig.md) | Configuration for sampling transforms (displacements and lookup tables) |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[ExtrapolationMethod](ExtrapolationMethod.md)&nbsp;or&nbsp;<br />[String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_spaces:extrapolation |
| native | noid_spaces:extrapolation |




## LinkML Source

<details>
```yaml
name: extrapolation
description: Extrapolation method
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
ifabsent: string(nearest)
alias: extrapolation
owner: SamplerConfig
domain_of:
- SamplerConfig
range: string
any_of:
- range: ExtrapolationMethod
- range: string

```
</details>