# Auto generated from space.linkml.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-07-18T18:26:50
# Schema: space
#
# id: https://github.com/nclack/noid/schemas/v0/space.linkml.yaml
# description: Schema for defining coordinate systems, dimensions, and coordinate transforms for multidimensional array data.
# license: MIT

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Float, Integer, String

metamodel_version = "1.7.0"
version = "0.1.0"

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
NOID_SAMPLER = CurieNamespace('noid_sampler', 'https://github.com/nclack/noid/schemas/sampler.v0.context.jsonld')
NOID_SPACES = CurieNamespace('noid_spaces', 'https://github.com/nclack/noid/schemas/space.v0.context.jsonld')
NOID_TRANSFORM = CurieNamespace('noid_transform', 'https://github.com/nclack/noid/schemas/transform.v0.context.jsonld')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = NOID_SPACES


# Types

# Class references
class DimensionId(extended_str):
    pass


class CoordinateSystemId(extended_str):
    pass


class CoordinateTransformId(extended_str):
    pass


@dataclass(repr=False)
class Dimension(YAMLRoot):
    """
    A single axis within a coordinate space with its measurement unit and classification.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_SPACES["Dimension"]
    class_class_curie: ClassVar[str] = "noid_spaces:Dimension"
    class_name: ClassVar[str] = "Dimension"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.Dimension

    id: Union[str, DimensionId] = None
    unit: Union[str, "UnitTerm"] = None
    type: Union[str, "DimensionType"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DimensionId):
            self.id = DimensionId(self.id)

        if self._is_empty(self.unit):
            self.MissingRequiredField("unit")
        if not isinstance(self.unit, UnitTerm):
            self.unit = UnitTerm(self.unit)

        if self._is_empty(self.type):
            self.MissingRequiredField("type")
        if not isinstance(self.type, DimensionType):
            self.type = DimensionType(self.type)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class CoordinateSystem(YAMLRoot):
    """
    Collection of dimensions that together define a coordinate space for positioning data elements.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_SPACES["CoordinateSystem"]
    class_class_curie: ClassVar[str] = "noid_spaces:CoordinateSystem"
    class_name: ClassVar[str] = "CoordinateSystem"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.CoordinateSystem

    id: Union[str, CoordinateSystemId] = None
    dimensions: Union[Union[dict, "DimensionSpec"], list[Union[dict, "DimensionSpec"]]] = None
    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, CoordinateSystemId):
            self.id = CoordinateSystemId(self.id)

        if self._is_empty(self.dimensions):
            self.MissingRequiredField("dimensions")
        if not isinstance(self.dimensions, list):
            self.dimensions = [self.dimensions] if self.dimensions is not None else []
        self.dimensions = [v if isinstance(v, DimensionSpec) else DimensionSpec(**as_dict(v)) for v in self.dimensions]

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class CoordinateTransform(YAMLRoot):
    """
    Mathematical mapping between input and output coordinate spaces with transform definition.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_SPACES["CoordinateTransform"]
    class_class_curie: ClassVar[str] = "noid_spaces:CoordinateTransform"
    class_name: ClassVar[str] = "CoordinateTransform"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.CoordinateTransform

    id: Union[str, CoordinateTransformId] = None
    input: Union[dict, "CoordinateSpaceSpec"] = None
    output: Union[dict, "CoordinateSpaceSpec"] = None
    transform: Union[dict, "Transform"] = None
    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, CoordinateTransformId):
            self.id = CoordinateTransformId(self.id)

        if self._is_empty(self.input):
            self.MissingRequiredField("input")
        if not isinstance(self.input, CoordinateSpaceSpec):
            self.input = CoordinateSpaceSpec()

        if self._is_empty(self.output):
            self.MissingRequiredField("output")
        if not isinstance(self.output, CoordinateSpaceSpec):
            self.output = CoordinateSpaceSpec()

        if self._is_empty(self.transform):
            self.MissingRequiredField("transform")
        if not isinstance(self.transform, Transform):
            self.transform = Transform()

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


class DimensionSpec(YAMLRoot):
    """
    Dimension specification that can be either a string reference or inline Dimension object.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_SPACES["DimensionSpec"]
    class_class_curie: ClassVar[str] = "noid_spaces:DimensionSpec"
    class_name: ClassVar[str] = "DimensionSpec"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.DimensionSpec


class CoordinateSpaceSpec(YAMLRoot):
    """
    Coordinate space specification that can be a string reference, dimension array, or inline CoordinateSystem.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_SPACES["CoordinateSpaceSpec"]
    class_class_curie: ClassVar[str] = "noid_spaces:CoordinateSpaceSpec"
    class_name: ClassVar[str] = "CoordinateSpaceSpec"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.CoordinateSpaceSpec


@dataclass(repr=False)
class DimensionArray(YAMLRoot):
    """
    Array of dimension specifications
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_SPACES["DimensionArray"]
    class_class_curie: ClassVar[str] = "noid_spaces:DimensionArray"
    class_name: ClassVar[str] = "DimensionArray"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.DimensionArray

    dimensions: Optional[Union[Union[dict, DimensionSpec], list[Union[dict, DimensionSpec]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if not isinstance(self.dimensions, list):
            self.dimensions = [self.dimensions] if self.dimensions is not None else []
        self.dimensions = [v if isinstance(v, DimensionSpec) else DimensionSpec(**as_dict(v)) for v in self.dimensions]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SamplerConfig(YAMLRoot):
    """
    Configuration for sampling transforms (displacements and lookup tables)
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_SAMPLER["SamplerConfig"]
    class_class_curie: ClassVar[str] = "noid_sampler:SamplerConfig"
    class_name: ClassVar[str] = "SamplerConfig"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.SamplerConfig

    interpolation: Optional[str] = "nearest"
    extrapolation: Optional[str] = "nearest"

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.interpolation is not None and not isinstance(self.interpolation, str):
            self.interpolation = str(self.interpolation)

        if self.extrapolation is not None and not isinstance(self.extrapolation, str):
            self.extrapolation = str(self.extrapolation)

        super().__post_init__(**kwargs)


class Transform(YAMLRoot):
    """
    A coordinate transformation with self-describing parameters
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["Transform"]
    class_class_curie: ClassVar[str] = "noid_transform:Transform"
    class_name: ClassVar[str] = "Transform"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.Transform


class Identity(Transform):
    """
    Identity transform
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["Identity"]
    class_class_curie: ClassVar[str] = "noid_transform:Identity"
    class_name: ClassVar[str] = "Identity"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.Identity


@dataclass(repr=False)
class Translation(Transform):
    """
    Translation transform
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["Translation"]
    class_class_curie: ClassVar[str] = "noid_transform:Translation"
    class_name: ClassVar[str] = "Translation"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.Translation

    translation: Union[float, list[float]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.translation):
            self.MissingRequiredField("translation")
        if not isinstance(self.translation, list):
            self.translation = [self.translation] if self.translation is not None else []
        self.translation = [v if isinstance(v, float) else float(v) for v in self.translation]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Scale(Transform):
    """
    Scale transform
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["Scale"]
    class_class_curie: ClassVar[str] = "noid_transform:Scale"
    class_name: ClassVar[str] = "Scale"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.Scale

    scale: Union[float, list[float]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.scale):
            self.MissingRequiredField("scale")
        if not isinstance(self.scale, list):
            self.scale = [self.scale] if self.scale is not None else []
        self.scale = [v if isinstance(v, float) else float(v) for v in self.scale]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MapAxis(Transform):
    """
    Axis permutation transform
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["MapAxis"]
    class_class_curie: ClassVar[str] = "noid_transform:MapAxis"
    class_name: ClassVar[str] = "MapAxis"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.MapAxis

    map_axis: Union[int, list[int]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.map_axis):
            self.MissingRequiredField("map_axis")
        if not isinstance(self.map_axis, list):
            self.map_axis = [self.map_axis] if self.map_axis is not None else []
        self.map_axis = [v if isinstance(v, int) else int(v) for v in self.map_axis]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Homogeneous(Transform):
    """
    Homogeneous transformation matrix (affine/projective)
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["Homogeneous"]
    class_class_curie: ClassVar[str] = "noid_transform:Homogeneous"
    class_name: ClassVar[str] = "Homogeneous"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.Homogeneous

    homogeneous: Union[float, list[float]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.homogeneous):
            self.MissingRequiredField("homogeneous")
        if not isinstance(self.homogeneous, list):
            self.homogeneous = [self.homogeneous] if self.homogeneous is not None else []
        self.homogeneous = [v if isinstance(v, float) else float(v) for v in self.homogeneous]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DisplacementLookupTable(Transform):
    """
    Displacement field lookup table transform
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["DisplacementLookupTable"]
    class_class_curie: ClassVar[str] = "noid_transform:DisplacementLookupTable"
    class_name: ClassVar[str] = "DisplacementLookupTable"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.DisplacementLookupTable

    path: str = None
    displacements: Optional[Union[dict, SamplerConfig]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.path):
            self.MissingRequiredField("path")
        if not isinstance(self.path, str):
            self.path = str(self.path)

        if self.displacements is not None and not isinstance(self.displacements, SamplerConfig):
            self.displacements = SamplerConfig(**as_dict(self.displacements))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class CoordinateLookupTable(Transform):
    """
    Coordinate lookup table transform
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["CoordinateLookupTable"]
    class_class_curie: ClassVar[str] = "noid_transform:CoordinateLookupTable"
    class_name: ClassVar[str] = "CoordinateLookupTable"
    class_model_uri: ClassVar[URIRef] = NOID_SPACES.CoordinateLookupTable

    path: str = None
    lookup_table: Optional[Union[dict, SamplerConfig]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.path):
            self.MissingRequiredField("path")
        if not isinstance(self.path, str):
            self.path = str(self.path)

        if self.lookup_table is not None and not isinstance(self.lookup_table, SamplerConfig):
            self.lookup_table = SamplerConfig(**as_dict(self.lookup_table))

        super().__post_init__(**kwargs)


# Enumerations
class DimensionType(EnumDefinitionImpl):
    """
    Classification of dimension types
    """
    space = PermissibleValue(
        text="space",
        description="Spatial dimensions",
        meaning=NOID_SPACES["SpatialDimension"])
    time = PermissibleValue(
        text="time",
        description="Temporal dimensions",
        meaning=NOID_SPACES["TemporalDimension"])
    other = PermissibleValue(
        text="other",
        description="Channels, indices, categories",
        meaning=NOID_SPACES["OtherDimension"])
    index = PermissibleValue(
        text="index",
        description="Array index dimensions",
        meaning=NOID_SPACES["IndexDimension"])

    _defn = EnumDefinition(
        name="DimensionType",
        description="Classification of dimension types",
    )

class UnitTerm(EnumDefinitionImpl):
    """
    Controlled vocabulary for measurement units
    """
    index = PermissibleValue(
        text="index",
        description="Array index unit",
        meaning=NOID_SPACES["IndexUnit"])
    arbitrary = PermissibleValue(
        text="arbitrary",
        description="Arbitrary or dimensionless unit",
        meaning=NOID_SPACES["ArbitraryUnit"])
    meter = PermissibleValue(
        text="meter",
        description="SI base unit of length",
        meaning=NOID_SPACES["MeterUnit"])
    meters = PermissibleValue(
        text="meters",
        description="SI base unit of length (plural)",
        meaning=NOID_SPACES["MeterUnit"])
    millimeter = PermissibleValue(
        text="millimeter",
        description="Millimeter (10^-3 meter)",
        meaning=NOID_SPACES["MillimeterUnit"])
    millimeters = PermissibleValue(
        text="millimeters",
        description="Millimeter (10^-3 meter, plural)",
        meaning=NOID_SPACES["MillimeterUnit"])
    micrometer = PermissibleValue(
        text="micrometer",
        description="Micrometer (10^-6 meter)",
        meaning=NOID_SPACES["MicrometerUnit"])
    micrometers = PermissibleValue(
        text="micrometers",
        description="Micrometer (10^-6 meter, plural)",
        meaning=NOID_SPACES["MicrometerUnit"])
    nanometer = PermissibleValue(
        text="nanometer",
        description="Nanometer (10^-9 meter)",
        meaning=NOID_SPACES["NanometerUnit"])
    nanometers = PermissibleValue(
        text="nanometers",
        description="Nanometer (10^-9 meter, plural)",
        meaning=NOID_SPACES["NanometerUnit"])
    pixel = PermissibleValue(
        text="pixel",
        description="Pixel unit for digital images",
        meaning=NOID_SPACES["PixelUnit"])
    pixels = PermissibleValue(
        text="pixels",
        description="Pixel unit for digital images (plural)",
        meaning=NOID_SPACES["PixelUnit"])
    second = PermissibleValue(
        text="second",
        description="SI base unit of time",
        meaning=NOID_SPACES["SecondUnit"])
    seconds = PermissibleValue(
        text="seconds",
        description="SI base unit of time (plural)",
        meaning=NOID_SPACES["SecondUnit"])
    millisecond = PermissibleValue(
        text="millisecond",
        description="Millisecond (10^-3 second)",
        meaning=NOID_SPACES["MillisecondUnit"])
    milliseconds = PermissibleValue(
        text="milliseconds",
        description="Millisecond (10^-3 second, plural)",
        meaning=NOID_SPACES["MillisecondUnit"])
    minute = PermissibleValue(
        text="minute",
        description="Minute (60 seconds)",
        meaning=NOID_SPACES["MinuteUnit"])
    minutes = PermissibleValue(
        text="minutes",
        description="Minute (60 seconds, plural)",
        meaning=NOID_SPACES["MinuteUnit"])
    hour = PermissibleValue(
        text="hour",
        description="Hour (3600 seconds)",
        meaning=NOID_SPACES["HourUnit"])
    hours = PermissibleValue(
        text="hours",
        description="Hour (3600 seconds, plural)",
        meaning=NOID_SPACES["HourUnit"])
    radian = PermissibleValue(
        text="radian",
        description="SI unit of angle",
        meaning=NOID_SPACES["RadianUnit"])
    radians = PermissibleValue(
        text="radians",
        description="SI unit of angle (plural)",
        meaning=NOID_SPACES["RadianUnit"])
    degree = PermissibleValue(
        text="degree",
        description="Degree of arc (π/180 radians)",
        meaning=NOID_SPACES["DegreeUnit"])
    degrees = PermissibleValue(
        text="degrees",
        description="Degree of arc (π/180 radians, plural)",
        meaning=NOID_SPACES["DegreeUnit"])
    wavelength = PermissibleValue(
        text="wavelength",
        description="Wavelength measurement",
        meaning=NOID_SPACES["WavelengthUnit"])
    intensity = PermissibleValue(
        text="intensity",
        description="Intensity measurement",
        meaning=NOID_SPACES["IntensityUnit"])

    _defn = EnumDefinition(
        name="UnitTerm",
        description="Controlled vocabulary for measurement units",
    )

class InterpolationMethod(EnumDefinitionImpl):

    linear = PermissibleValue(
        text="linear",
        description="Linear interpolation")
    nearest = PermissibleValue(
        text="nearest",
        description="Nearest neighbor interpolation")
    cubic = PermissibleValue(
        text="cubic",
        description="Cubic interpolation")

    _defn = EnumDefinition(
        name="InterpolationMethod",
    )

class ExtrapolationMethod(EnumDefinitionImpl):

    nearest = PermissibleValue(
        text="nearest",
        description="Nearest neighbor extrapolation")
    zero = PermissibleValue(
        text="zero",
        description="Zero extrapolation")
    constant = PermissibleValue(
        text="constant",
        description="Constant extrapolation")
    reflect = PermissibleValue(
        text="reflect",
        description="Reflect about boundary edge")
    wrap = PermissibleValue(
        text="wrap",
        description="Wrap around periodically")

    _defn = EnumDefinition(
        name="ExtrapolationMethod",
    )

# Slots
class slots:
    pass

slots.dimension__id = Slot(uri=NOID_SPACES.id, name="dimension__id", curie=NOID_SPACES.curie('id'),
                   model_uri=NOID_SPACES.dimension__id, domain=None, range=URIRef,
                   pattern=re.compile(r'^.+$'))

slots.dimension__unit = Slot(uri=NOID_SPACES.unit, name="dimension__unit", curie=NOID_SPACES.curie('unit'),
                   model_uri=NOID_SPACES.dimension__unit, domain=None, range=Union[str, "UnitTerm"])

slots.dimension__type = Slot(uri=NOID_SPACES.type, name="dimension__type", curie=NOID_SPACES.curie('type'),
                   model_uri=NOID_SPACES.dimension__type, domain=None, range=Union[str, "DimensionType"])

slots.coordinateSystem__id = Slot(uri=NOID_SPACES.id, name="coordinateSystem__id", curie=NOID_SPACES.curie('id'),
                   model_uri=NOID_SPACES.coordinateSystem__id, domain=None, range=URIRef,
                   pattern=re.compile(r'^.+$'))

slots.coordinateSystem__dimensions = Slot(uri=NOID_SPACES.dimensions, name="coordinateSystem__dimensions", curie=NOID_SPACES.curie('dimensions'),
                   model_uri=NOID_SPACES.coordinateSystem__dimensions, domain=None, range=Union[Union[dict, DimensionSpec], list[Union[dict, DimensionSpec]]])

slots.coordinateSystem__description = Slot(uri=NOID_SPACES.description, name="coordinateSystem__description", curie=NOID_SPACES.curie('description'),
                   model_uri=NOID_SPACES.coordinateSystem__description, domain=None, range=Optional[str],
                   pattern=re.compile(r'^.+$'))

slots.coordinateTransform__id = Slot(uri=NOID_SPACES.id, name="coordinateTransform__id", curie=NOID_SPACES.curie('id'),
                   model_uri=NOID_SPACES.coordinateTransform__id, domain=None, range=URIRef,
                   pattern=re.compile(r'^.+$'))

slots.coordinateTransform__input = Slot(uri=NOID_SPACES.input, name="coordinateTransform__input", curie=NOID_SPACES.curie('input'),
                   model_uri=NOID_SPACES.coordinateTransform__input, domain=None, range=Union[dict, CoordinateSpaceSpec])

slots.coordinateTransform__output = Slot(uri=NOID_SPACES.output, name="coordinateTransform__output", curie=NOID_SPACES.curie('output'),
                   model_uri=NOID_SPACES.coordinateTransform__output, domain=None, range=Union[dict, CoordinateSpaceSpec])

slots.coordinateTransform__transform = Slot(uri=NOID_SPACES.transform, name="coordinateTransform__transform", curie=NOID_SPACES.curie('transform'),
                   model_uri=NOID_SPACES.coordinateTransform__transform, domain=None, range=Union[dict, Transform])

slots.coordinateTransform__description = Slot(uri=NOID_SPACES.description, name="coordinateTransform__description", curie=NOID_SPACES.curie('description'),
                   model_uri=NOID_SPACES.coordinateTransform__description, domain=None, range=Optional[str],
                   pattern=re.compile(r'^.+$'))

slots.dimensionArray__dimensions = Slot(uri=NOID_SPACES.dimensions, name="dimensionArray__dimensions", curie=NOID_SPACES.curie('dimensions'),
                   model_uri=NOID_SPACES.dimensionArray__dimensions, domain=None, range=Optional[Union[Union[dict, DimensionSpec], list[Union[dict, DimensionSpec]]]])

slots.samplerConfig__interpolation = Slot(uri=NOID_SAMPLER.interpolation, name="samplerConfig__interpolation", curie=NOID_SAMPLER.curie('interpolation'),
                   model_uri=NOID_SPACES.samplerConfig__interpolation, domain=None, range=Optional[str])

slots.samplerConfig__extrapolation = Slot(uri=NOID_SAMPLER.extrapolation, name="samplerConfig__extrapolation", curie=NOID_SAMPLER.curie('extrapolation'),
                   model_uri=NOID_SPACES.samplerConfig__extrapolation, domain=None, range=Optional[str])

slots.translation__translation = Slot(uri=NOID_TRANSFORM.translation, name="translation__translation", curie=NOID_TRANSFORM.curie('translation'),
                   model_uri=NOID_SPACES.translation__translation, domain=None, range=Union[float, list[float]])

slots.scale__scale = Slot(uri=NOID_TRANSFORM.scale, name="scale__scale", curie=NOID_TRANSFORM.curie('scale'),
                   model_uri=NOID_SPACES.scale__scale, domain=None, range=Union[float, list[float]])

slots.mapAxis__map_axis = Slot(uri=NOID_TRANSFORM.map_axis, name="mapAxis__map_axis", curie=NOID_TRANSFORM.curie('map_axis'),
                   model_uri=NOID_SPACES.mapAxis__map_axis, domain=None, range=Union[int, list[int]])

slots.homogeneous__homogeneous = Slot(uri=NOID_TRANSFORM.homogeneous, name="homogeneous__homogeneous", curie=NOID_TRANSFORM.curie('homogeneous'),
                   model_uri=NOID_SPACES.homogeneous__homogeneous, domain=None, range=Union[float, list[float]])

slots.displacementLookupTable__path = Slot(uri=NOID_TRANSFORM.path, name="displacementLookupTable__path", curie=NOID_TRANSFORM.curie('path'),
                   model_uri=NOID_SPACES.displacementLookupTable__path, domain=None, range=str)

slots.displacementLookupTable__displacements = Slot(uri=NOID_TRANSFORM.displacements, name="displacementLookupTable__displacements", curie=NOID_TRANSFORM.curie('displacements'),
                   model_uri=NOID_SPACES.displacementLookupTable__displacements, domain=None, range=Optional[Union[dict, SamplerConfig]])

slots.coordinateLookupTable__path = Slot(uri=NOID_TRANSFORM.path, name="coordinateLookupTable__path", curie=NOID_TRANSFORM.curie('path'),
                   model_uri=NOID_SPACES.coordinateLookupTable__path, domain=None, range=str)

slots.coordinateLookupTable__lookup_table = Slot(uri=NOID_TRANSFORM.lookup_table, name="coordinateLookupTable__lookup_table", curie=NOID_TRANSFORM.curie('lookup_table'),
                   model_uri=NOID_SPACES.coordinateLookupTable__lookup_table, domain=None, range=Optional[Union[dict, SamplerConfig]])
