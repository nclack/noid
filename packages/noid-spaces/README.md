# noid-spaces

Coordinate spaces vocabulary for multidimensional arrays.

This package provides LinkML-based models for defining coordinate systems, dimensions, and coordinate transforms for scientific datasets involving multidimensional arrays.

## Features

- **Dimension**: Define axes with controlled unit vocabularies (UDUNITS-2 compatible)
- **CoordinateSystem**: Collections of dimensions defining coordinate spaces
- **CoordinateTransform**: Mathematical mappings between coordinate spaces
- Integration with noid-transforms for transform definitions
- JSON-LD serialization with controlled vocabularies

## Installation

```bash
pip install noid-spaces
```

## Usage

```python
from noid_spaces import Dimension, CoordinateSystem, CoordinateTransform

# Create dimensions with controlled units
x_dim = Dimension(id="x", unit="micrometers", type="space")
y_dim = Dimension(id="y", unit="micrometers", type="space")
time_dim = Dimension(id="t", unit="seconds", type="time")

# Create coordinate system
physical_space = CoordinateSystem(
    id="physical_space",
    dimensions=[x_dim, y_dim],
    description="2D physical coordinate system"
)

# Create coordinate transform
transform = CoordinateTransform(
    id="physical_to_pixel",
    input="physical_space",
    output="pixel_space",
    transform={"scale": [0.1, 0.1]},
    description="Convert physical to pixel coordinates"
)
```

## Unit Vocabulary

The package includes a controlled vocabulary for measurement units including:

- **Spatial**: meter, millimeter, micrometer, nanometer, pixel
- **Temporal**: second, millisecond, minute, hour
- **Angular**: radian, degree
- **Universal**: index, arbitrary

All units follow UDUNITS-2 conventions where applicable.
