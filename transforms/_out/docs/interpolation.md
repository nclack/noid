

# Slot: interpolation 


_Interpolation method_





URI: [noid_transforms:interpolation](https://github.com/nclack/noid/transforms/interpolation)
Alias: interpolation

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SamplerConfig](SamplerConfig.md) | Configuration for sampling transforms (displacements and lookup tables) |  no  |







## Properties

* Range: NONE&nbsp;or&nbsp;<br />[InterpolationMethod](InterpolationMethod.md)&nbsp;or&nbsp;<br />[String](String.md)





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/transforms/transforms.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transforms:interpolation |
| native | noid_transforms:interpolation |




## LinkML Source

<details>
```yaml
name: interpolation
description: Interpolation method
from_schema: https://github.com/nclack/noid/transforms/transforms.linkml
rank: 1000
ifabsent: string(nearest)
alias: interpolation
owner: SamplerConfig
domain_of:
- SamplerConfig
any_of:
- range: InterpolationMethod
- range: string

```
</details>