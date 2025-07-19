# Enum: ExtrapolationMethod 



URI: [ExtrapolationMethod](ExtrapolationMethod.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| nearest | None | Nearest neighbor extrapolation |
| zero | None | Zero extrapolation |
| constant | None | Constant extrapolation |
| reflect | None | Reflect about boundary edge |
| wrap | None | Wrap around periodically |









## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml






## LinkML Source

<details>
```yaml
name: ExtrapolationMethod
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
permissible_values:
  nearest:
    text: nearest
    description: Nearest neighbor extrapolation
  zero:
    text: zero
    description: Zero extrapolation
  constant:
    text: constant
    description: Constant extrapolation
  reflect:
    text: reflect
    description: Reflect about boundary edge
  wrap:
    text: wrap
    description: Wrap around periodically

```
</details>
