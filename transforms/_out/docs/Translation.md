

# Slot: translation 


_Translation vector as array of numbers_





URI: [noid_transforms:translation](https://github.com/nclack/noid/transforms/translation)
Alias: translation

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Translation](Translation.md) | Translation transform |  no  |







## Properties

* Range: [Float](Float.md)

* Multivalued: True

* Required: True

* Minimum Value: 1





## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/transforms/transforms.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transforms:translation |
| native | noid_transforms:translation |




## LinkML Source

<details>
```yaml
name: translation
description: Translation vector as array of numbers
from_schema: https://github.com/nclack/noid/transforms/transforms.linkml
rank: 1000
alias: translation
owner: Translation
domain_of:
- Translation
range: float
required: true
multivalued: true
minimum_value: 1

```
</details>