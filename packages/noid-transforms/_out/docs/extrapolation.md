

# Slot: extrapolation 


_Extrapolation method_





URI: [noid_transform:extrapolation](https://github.com/nclack/noid/transforms/transform/extrapolation)
Alias: extrapolation

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SamplerConfig](SamplerConfig.md) | Configuration for sampling transforms (displacements and lookup tables) |  no  |







## Properties

* Range: NONE&nbsp;or&nbsp;<br />[ExtrapolationMethod](ExtrapolationMethod.md)&nbsp;or&nbsp;<br />[String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/transforms/transform.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transform:extrapolation |
| native | noid_transform:extrapolation |




## LinkML Source

<details>
```yaml
name: extrapolation
description: Extrapolation method
from_schema: https://github.com/nclack/noid/transforms/transform.linkml
rank: 1000
ifabsent: string(nearest)
alias: extrapolation
owner: SamplerConfig
domain_of:
- SamplerConfig
any_of:
- range: ExtrapolationMethod
- range: string

```
</details>