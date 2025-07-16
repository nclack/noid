

# Class: LookupTableConfig 


_Configuration for coordinate lookup table_





URI: [noid_transforms:LookupTableConfig](https://github.com/nclack/noid/schemas/transforms/LookupTableConfig)






```mermaid
 classDiagram
    class LookupTableConfig
    click LookupTableConfig href "../LookupTableConfig"
      LookupTableConfig : extrapolation
        
          
    
        
        
        LookupTableConfig --> "0..1" ExtrapolationMethod : extrapolation
        click ExtrapolationMethod href "../ExtrapolationMethod"
    

        
      LookupTableConfig : interpolation
        
          
    
        
        
        LookupTableConfig --> "0..1" InterpolationMethod : interpolation
        click InterpolationMethod href "../InterpolationMethod"
    

        
      LookupTableConfig : path
        
      
```




<!-- no inheritance hierarchy -->


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [path](path.md) | 1 <br/> [String](String.md) | Path to coordinate lookup table | direct |
| [interpolation](interpolation.md) | 0..1 <br/> [InterpolationMethod](InterpolationMethod.md) | Interpolation method | direct |
| [extrapolation](extrapolation.md) | 0..1 <br/> [ExtrapolationMethod](ExtrapolationMethod.md) | Extrapolation method | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [CoordinateLookupTable](CoordinateLookupTable.md) | [lookup_table](lookup_table.md) | any_of[range] | [LookupTableConfig](LookupTableConfig.md) |






## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_transforms:LookupTableConfig |
| native | noid_transforms:LookupTableConfig |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: LookupTableConfig
description: Configuration for coordinate lookup table
from_schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml
attributes:
  path:
    name: path
    description: Path to coordinate lookup table
    from_schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml
    domain_of:
    - DisplacementConfig
    - LookupTableConfig
    range: string
    required: true
  interpolation:
    name: interpolation
    description: Interpolation method
    from_schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml
    domain_of:
    - DisplacementConfig
    - LookupTableConfig
    range: InterpolationMethod
  extrapolation:
    name: extrapolation
    description: Extrapolation method
    from_schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml
    domain_of:
    - DisplacementConfig
    - LookupTableConfig
    range: ExtrapolationMethod

```
</details>

### Induced

<details>
```yaml
name: LookupTableConfig
description: Configuration for coordinate lookup table
from_schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml
attributes:
  path:
    name: path
    description: Path to coordinate lookup table
    from_schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml
    alias: path
    owner: LookupTableConfig
    domain_of:
    - DisplacementConfig
    - LookupTableConfig
    range: string
    required: true
  interpolation:
    name: interpolation
    description: Interpolation method
    from_schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml
    alias: interpolation
    owner: LookupTableConfig
    domain_of:
    - DisplacementConfig
    - LookupTableConfig
    range: InterpolationMethod
  extrapolation:
    name: extrapolation
    description: Extrapolation method
    from_schema: https://github.com/nclack/noid/schemas/transforms/transforms.linkml
    alias: extrapolation
    owner: LookupTableConfig
    domain_of:
    - DisplacementConfig
    - LookupTableConfig
    range: ExtrapolationMethod

```
</details>