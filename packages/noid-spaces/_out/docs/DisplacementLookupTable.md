

# Class: DisplacementLookupTable 


_Displacement field lookup table transform_





URI: [noid_spaces:DisplacementLookupTable](https://github.com/nclack/noid/schemas/space.v0.context.jsonldDisplacementLookupTable)






```mermaid
 classDiagram
    class DisplacementLookupTable
    click DisplacementLookupTable href "../DisplacementLookupTable"
      Transform <|-- DisplacementLookupTable
        click Transform href "../Transform"
      
      DisplacementLookupTable : displacements
        
          
    
        
        
        DisplacementLookupTable --> "0..1" SamplerConfig : displacements
        click SamplerConfig href "../SamplerConfig"
    

        
      DisplacementLookupTable : path
        
      
```





## Inheritance
* [Transform](Transform.md)
    * **DisplacementLookupTable**



## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [path](path.md) | 1 <br/> [String](String.md) | Path to displacement field data file | direct |
| [displacements](displacements.md) | 0..1 <br/> [SamplerConfig](SamplerConfig.md) | Displacement field configuration | direct |









## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | noid_spaces:DisplacementLookupTable |
| native | noid_spaces:DisplacementLookupTable |







## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DisplacementLookupTable
description: Displacement field lookup table transform
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
is_a: Transform
attributes:
  path:
    name: path
    description: Path to displacement field data file
    from_schema: https://github.com/nclack/noid/schemas/v0/transform.linkml.yaml
    rank: 1000
    domain_of:
    - DisplacementLookupTable
    - CoordinateLookupTable
    range: string
    required: true
  displacements:
    name: displacements
    description: Displacement field configuration
    from_schema: https://github.com/nclack/noid/schemas/v0/transform.linkml.yaml
    rank: 1000
    domain_of:
    - DisplacementLookupTable
    range: SamplerConfig

```
</details>

### Induced

<details>
```yaml
name: DisplacementLookupTable
description: Displacement field lookup table transform
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
is_a: Transform
attributes:
  path:
    name: path
    description: Path to displacement field data file
    from_schema: https://github.com/nclack/noid/schemas/v0/transform.linkml.yaml
    rank: 1000
    alias: path
    owner: DisplacementLookupTable
    domain_of:
    - DisplacementLookupTable
    - CoordinateLookupTable
    range: string
    required: true
  displacements:
    name: displacements
    description: Displacement field configuration
    from_schema: https://github.com/nclack/noid/schemas/v0/transform.linkml.yaml
    rank: 1000
    alias: displacements
    owner: DisplacementLookupTable
    domain_of:
    - DisplacementLookupTable
    range: SamplerConfig

```
</details>