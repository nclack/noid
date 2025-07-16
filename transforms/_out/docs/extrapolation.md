

# Slot: extrapolation 


_Extrapolation method_





URI: [noid_transforms:extrapolation](https://github.com/nclack/noid/transforms/extrapolation)
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


* from schema: https://github.com/nclack/noid/transforms/transforms.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transforms:extrapolation |
| native | noid_transforms:extrapolation |




## LinkML Source

<details>
```yaml
name: extrapolation
description: Extrapolation method
from_schema: https://github.com/nclack/noid/transforms/transforms.linkml
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