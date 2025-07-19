

# Slot: interpolation 


_Interpolation method_





URI: [noid_spaces:interpolation](https://github.com/nclack/noid/schemas/space.v0.context.jsonldinterpolation)
Alias: interpolation

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SamplerConfig](SamplerConfig.md) | Configuration for sampling transforms (displacements and lookup tables) |  no  |







## Properties

* Range: [String](String.md)&nbsp;or&nbsp;<br />[InterpolationMethod](InterpolationMethod.md)&nbsp;or&nbsp;<br />[String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_spaces:interpolation |
| native | noid_spaces:interpolation |




## LinkML Source

<details>
```yaml
name: interpolation
description: Interpolation method
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
ifabsent: string(nearest)
alias: interpolation
owner: SamplerConfig
domain_of:
- SamplerConfig
range: string
any_of:
- range: InterpolationMethod
- range: string

```
</details>