# NOID Spaces Examples

This directory contains examples demonstrating the NOID Spaces coordinate system and dimension identity features.

## Coordinate System Construction Patterns

### Using Factory Function (Recommended)
```python
from noid_spaces import coordinate_system

cs = coordinate_system(
    dimensions=[
        {"id": "x", "unit": "mm", "type": "space"},  # Explicit
        {"unit": "mm", "type": "space"},             # Auto-labeled
        {"id": "time", "unit": "ms"}                 # Type inferred
    ],
    id="my_system"
)
```

### Using add_dimension Method
```python
from noid_spaces.models import CoordinateSystem

cs = CoordinateSystem(id="my_system", dimensions=[])
cs.add_dimension(unit="mm", kind="space", label="x")    # Explicit label
cs.add_dimension(unit="mm", kind="space")               # Auto-labeled
```

### Direct Construction
```python
from noid_spaces.models import CoordinateSystem, Dimension

cs = CoordinateSystem(
    id="my_system",
    dimensions=[
        Dimension(unit="mm", kind="space", dimension_id="my_system#x"),
        Dimension(unit="mm", kind="space", dimension_id="my_system#y"),
    ]
)
```

## Running Examples

All examples can be run from the repository root:

```bash
# Run the Python example
uv run python packages/noid-spaces/examples/dimension_identity_usage.py

# View JSON-LD examples
cat packages/noid-spaces/examples/dimension_sequence.jsonld
cat packages/noid-spaces/examples/transforms_and_spaces.jsonld
```
