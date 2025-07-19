

# Slot: translation 


_Translation vector as array of numbers_





URI: [noid_transform:translation](https://github.com/nclack/noid/schemas/transform/translation)
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


* from schema: https://github.com/nclack/noid/schemas/transform/v0.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transform:translation |
| native | noid_transform:translation |




## LinkML Source

<details>
```yaml
name: translation
description: Translation vector as array of numbers
from_schema: https://github.com/nclack/noid/schemas/transform/v0.linkml
rank: 1000
list_elements_ordered: true
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