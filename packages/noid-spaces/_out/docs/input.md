

# Slot: input 


_Input coordinate space specification_





URI: [noid_spaces:input](https://github.com/nclack/noid/schemas/space.v0.context.jsonldinput)
Alias: input

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CoordinateTransform](CoordinateTransform.md) | Mathematical mapping between input and output coordinate spaces with transfor... |  no  |







## Properties

* Range: [CoordinateSpaceSpec](CoordinateSpaceSpec.md)

* Required: True





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_spaces:input |
| native | noid_spaces:input |




## LinkML Source

<details>
```yaml
name: input
description: Input coordinate space specification
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
alias: input
owner: CoordinateTransform
domain_of:
- CoordinateTransform
range: CoordinateSpaceSpec
required: true

```
</details>