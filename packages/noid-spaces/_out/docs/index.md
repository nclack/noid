# Coordinate Spaces and Dimensions Schema

Schema for defining coordinate systems, dimensions, and coordinate transforms for multidimensional array data.

URI: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml

Name: space



## Classes

| Class | Description |
| --- | --- |
| [CoordinateSpaceSpec](CoordinateSpaceSpec.md) | Coordinate space specification that can be a string reference, dimension arra... |
| [CoordinateSystem](CoordinateSystem.md) | Collection of dimensions that together define a coordinate space for position... |
| [CoordinateTransform](CoordinateTransform.md) | Mathematical mapping between input and output coordinate spaces with transfor... |
| [Dimension](Dimension.md) | A single axis within a coordinate space with its measurement unit and classif... |
| [DimensionArray](DimensionArray.md) | Array of dimension specifications |
| [DimensionSpec](DimensionSpec.md) | Dimension specification that can be either a string reference or inline Dimen... |
| [SamplerConfig](SamplerConfig.md) | Configuration for sampling transforms (displacements and lookup tables) |
| [Transform](Transform.md) | A coordinate transformation with self-describing parameters |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CoordinateLookupTable](CoordinateLookupTable.md) | Coordinate lookup table transform |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[DisplacementLookupTable](DisplacementLookupTable.md) | Displacement field lookup table transform |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Homogeneous](Homogeneous.md) | Homogeneous transformation matrix (affine/projective) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Identity](Identity.md) | Identity transform |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[MapAxis](MapAxis.md) | Axis permutation transform |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Scale](Scale.md) | Scale transform |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Translation](Translation.md) | Translation transform |



## Slots

| Slot | Description |
| --- | --- |
| [description](description.md) | Optional description of the coordinate system |
| [dimensions](dimensions.md) | List of dimension specifications |
| [displacements](displacements.md) | Displacement field configuration |
| [extrapolation](extrapolation.md) | Extrapolation method |
| [homogeneous](homogeneous.md) | Homogeneous transformation matrix as 2D array |
| [id](id.md) | Unique identifier for the dimension |
| [input](input.md) | Input coordinate space specification |
| [interpolation](interpolation.md) | Interpolation method |
| [lookup_table](lookup_table.md) | Coordinate lookup table configuration |
| [map_axis](map_axis.md) | Permutation vector of 0-based input dimension indices |
| [output](output.md) | Output coordinate space specification |
| [path](path.md) | Path to displacement field data file |
| [scale](scale.md) | Scale factors as array of numbers |
| [transform](transform.md) | Transform definition from noid_transform schema |
| [translation](translation.md) | Translation vector as array of numbers |
| [type](type.md) | Dimension type classification |
| [unit](unit.md) | Unit of measurement from controlled vocabulary |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [DimensionType](DimensionType.md) | Classification of dimension types |
| [ExtrapolationMethod](ExtrapolationMethod.md) |  |
| [InterpolationMethod](InterpolationMethod.md) |  |
| [UnitTerm](UnitTerm.md) | Controlled vocabulary for measurement units |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [Integer](Integer.md) | An integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |


## Subsets

| Subset | Description |
| --- | --- |
