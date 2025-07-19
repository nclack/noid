

# Slot: output 


_Output coordinate space specification_





URI: [noid_spaces:output](https://github.com/nclack/noid/schemas/space.v0.context.jsonldoutput)
Alias: output

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
| self | noid_spaces:output |
| native | noid_spaces:output |




## LinkML Source

<details>
```yaml
name: output
description: Output coordinate space specification
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
alias: output
owner: CoordinateTransform
domain_of:
- CoordinateTransform
range: CoordinateSpaceSpec
required: true

```
</details>