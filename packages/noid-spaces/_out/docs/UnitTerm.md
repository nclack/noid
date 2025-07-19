# Enum: UnitTerm 




_Controlled vocabulary for measurement units_



URI: [UnitTerm](UnitTerm.md)

## Permissible Values

| Value | Meaning | Description |
| --- | --- | --- |
| index | noid_spaces:IndexUnit | Array index unit |
| arbitrary | noid_spaces:ArbitraryUnit | Arbitrary or dimensionless unit |
| meter | noid_spaces:MeterUnit | SI base unit of length |
| meters | noid_spaces:MeterUnit | SI base unit of length (plural) |
| millimeter | noid_spaces:MillimeterUnit | Millimeter (10^-3 meter) |
| millimeters | noid_spaces:MillimeterUnit | Millimeter (10^-3 meter, plural) |
| micrometer | noid_spaces:MicrometerUnit | Micrometer (10^-6 meter) |
| micrometers | noid_spaces:MicrometerUnit | Micrometer (10^-6 meter, plural) |
| nanometer | noid_spaces:NanometerUnit | Nanometer (10^-9 meter) |
| nanometers | noid_spaces:NanometerUnit | Nanometer (10^-9 meter, plural) |
| pixel | noid_spaces:PixelUnit | Pixel unit for digital images |
| pixels | noid_spaces:PixelUnit | Pixel unit for digital images (plural) |
| second | noid_spaces:SecondUnit | SI base unit of time |
| seconds | noid_spaces:SecondUnit | SI base unit of time (plural) |
| millisecond | noid_spaces:MillisecondUnit | Millisecond (10^-3 second) |
| milliseconds | noid_spaces:MillisecondUnit | Millisecond (10^-3 second, plural) |
| minute | noid_spaces:MinuteUnit | Minute (60 seconds) |
| minutes | noid_spaces:MinuteUnit | Minute (60 seconds, plural) |
| hour | noid_spaces:HourUnit | Hour (3600 seconds) |
| hours | noid_spaces:HourUnit | Hour (3600 seconds, plural) |
| radian | noid_spaces:RadianUnit | SI unit of angle |
| radians | noid_spaces:RadianUnit | SI unit of angle (plural) |
| degree | noid_spaces:DegreeUnit | Degree of arc (π/180 radians) |
| degrees | noid_spaces:DegreeUnit | Degree of arc (π/180 radians, plural) |
| wavelength | noid_spaces:WavelengthUnit | Wavelength measurement |
| intensity | noid_spaces:IntensityUnit | Intensity measurement |




## Slots

| Name | Description |
| ---  | --- |
| [unit](unit.md) | Unit of measurement from controlled vocabulary |






## Identifier and Mapping Information







### Schema Source


* from schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml






## LinkML Source

<details>
```yaml
name: UnitTerm
description: Controlled vocabulary for measurement units
from_schema: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
rank: 1000
permissible_values:
  index:
    text: index
    description: Array index unit
    meaning: noid_spaces:IndexUnit
  arbitrary:
    text: arbitrary
    description: Arbitrary or dimensionless unit
    meaning: noid_spaces:ArbitraryUnit
  meter:
    text: meter
    description: SI base unit of length
    meaning: noid_spaces:MeterUnit
  meters:
    text: meters
    description: SI base unit of length (plural)
    meaning: noid_spaces:MeterUnit
  millimeter:
    text: millimeter
    description: Millimeter (10^-3 meter)
    meaning: noid_spaces:MillimeterUnit
  millimeters:
    text: millimeters
    description: Millimeter (10^-3 meter, plural)
    meaning: noid_spaces:MillimeterUnit
  micrometer:
    text: micrometer
    description: Micrometer (10^-6 meter)
    meaning: noid_spaces:MicrometerUnit
  micrometers:
    text: micrometers
    description: Micrometer (10^-6 meter, plural)
    meaning: noid_spaces:MicrometerUnit
  nanometer:
    text: nanometer
    description: Nanometer (10^-9 meter)
    meaning: noid_spaces:NanometerUnit
  nanometers:
    text: nanometers
    description: Nanometer (10^-9 meter, plural)
    meaning: noid_spaces:NanometerUnit
  pixel:
    text: pixel
    description: Pixel unit for digital images
    meaning: noid_spaces:PixelUnit
  pixels:
    text: pixels
    description: Pixel unit for digital images (plural)
    meaning: noid_spaces:PixelUnit
  second:
    text: second
    description: SI base unit of time
    meaning: noid_spaces:SecondUnit
  seconds:
    text: seconds
    description: SI base unit of time (plural)
    meaning: noid_spaces:SecondUnit
  millisecond:
    text: millisecond
    description: Millisecond (10^-3 second)
    meaning: noid_spaces:MillisecondUnit
  milliseconds:
    text: milliseconds
    description: Millisecond (10^-3 second, plural)
    meaning: noid_spaces:MillisecondUnit
  minute:
    text: minute
    description: Minute (60 seconds)
    meaning: noid_spaces:MinuteUnit
  minutes:
    text: minutes
    description: Minute (60 seconds, plural)
    meaning: noid_spaces:MinuteUnit
  hour:
    text: hour
    description: Hour (3600 seconds)
    meaning: noid_spaces:HourUnit
  hours:
    text: hours
    description: Hour (3600 seconds, plural)
    meaning: noid_spaces:HourUnit
  radian:
    text: radian
    description: SI unit of angle
    meaning: noid_spaces:RadianUnit
  radians:
    text: radians
    description: SI unit of angle (plural)
    meaning: noid_spaces:RadianUnit
  degree:
    text: degree
    description: Degree of arc (π/180 radians)
    meaning: noid_spaces:DegreeUnit
  degrees:
    text: degrees
    description: Degree of arc (π/180 radians, plural)
    meaning: noid_spaces:DegreeUnit
  wavelength:
    text: wavelength
    description: Wavelength measurement
    meaning: noid_spaces:WavelengthUnit
  intensity:
    text: intensity
    description: Intensity measurement
    meaning: noid_spaces:IntensityUnit

```
</details>
