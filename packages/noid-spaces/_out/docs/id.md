

# Slot: id 



URI: [noid_spaces:id](https://github.com/nclack/noid/schemas/space.v0.context.jsonldid)
Alias: id

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CoordinateSystem](CoordinateSystem.md) | Collection of dimensions that together define a coordinate space for position... |  no  |
| [Dimension](Dimension.md) | A single axis within a coordinate space with its measurement unit and classif... |  no  |
| [CoordinateTransform](CoordinateTransform.md) | Mathematical mapping between input and output coordinate spaces with transfor... |  no  |







## Properties

* Range: [String](String.md)





## Identifier and Mapping Information








## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_spaces:id |
| native | noid_spaces:id |




## LinkML Source

<details>
```yaml
name: id
alias: id
domain_of:
- Dimension
- CoordinateSystem
- CoordinateTransform
range: string

```
</details>