# Auto generated from v0.linkml.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-07-18T18:56:09
# Schema: transform
#
# id: https://github.com/nclack/noid/schemas/transform/v0.linkml
# description: Schema for validating transform parameters using self-describing format
# license: https://creativecommons.org/publicdomain/zero/1.0/

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
NOID_SAMPLER = CurieNamespace('noid_sampler', 'https://github.com/nclack/noid/schemas/sampler/')
NOID_TRANSFORM = CurieNamespace('noid_transform', 'https://github.com/nclack/noid/schemas/transform/')
DEFAULT_ = NOID_TRANSFORM


# Types

# Class references



class Transform(YAMLRoot):
    """
    A coordinate transformation with self-describing parameters
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["Transform"]
    class_class_curie: ClassVar[str] = "noid_transform:Transform"
    class_name: ClassVar[str] = "Transform"
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.Transform


class Identity(Transform):
    """
    Identity transform
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["Identity"]
    class_class_curie: ClassVar[str] = "noid_transform:Identity"
    class_name: ClassVar[str] = "Identity"
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.Identity


@dataclass(repr=False)
class Translation(Transform):
    """
    Translation transform
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_TRANSFORM["Translation"]
    class_class_curie: ClassVar[str] = "noid_transform:Translation"
    class_name: ClassVar[str] = "Translation"
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.Translation

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
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.Scale

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
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.MapAxis

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
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.Homogeneous

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
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.DisplacementLookupTable

    path: str = None
    displacements: Optional[Union[dict, "SamplerConfig"]] = None

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
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.CoordinateLookupTable

    path: str = None
    lookup_table: Optional[Union[dict, "SamplerConfig"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.path):
            self.MissingRequiredField("path")
        if not isinstance(self.path, str):
            self.path = str(self.path)

        if self.lookup_table is not None and not isinstance(self.lookup_table, SamplerConfig):
            self.lookup_table = SamplerConfig(**as_dict(self.lookup_table))

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
    class_model_uri: ClassVar[URIRef] = NOID_TRANSFORM.SamplerConfig

    interpolation: Optional[str] = "nearest"
    extrapolation: Optional[str] = "nearest"

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.interpolation is not None and not isinstance(self.interpolation, str):
            self.interpolation = str(self.interpolation)

        if self.extrapolation is not None and not isinstance(self.extrapolation, str):
            self.extrapolation = str(self.extrapolation)

        super().__post_init__(**kwargs)


# Enumerations
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

slots.translation__translation = Slot(uri=NOID_TRANSFORM.translation, name="translation__translation", curie=NOID_TRANSFORM.curie('translation'),
                   model_uri=NOID_TRANSFORM.translation__translation, domain=None, range=Union[float, list[float]])

slots.scale__scale = Slot(uri=NOID_TRANSFORM.scale, name="scale__scale", curie=NOID_TRANSFORM.curie('scale'),
                   model_uri=NOID_TRANSFORM.scale__scale, domain=None, range=Union[float, list[float]])

slots.mapAxis__map_axis = Slot(uri=NOID_TRANSFORM.map_axis, name="mapAxis__map_axis", curie=NOID_TRANSFORM.curie('map_axis'),
                   model_uri=NOID_TRANSFORM.mapAxis__map_axis, domain=None, range=Union[int, list[int]])

slots.homogeneous__homogeneous = Slot(uri=NOID_TRANSFORM.homogeneous, name="homogeneous__homogeneous", curie=NOID_TRANSFORM.curie('homogeneous'),
                   model_uri=NOID_TRANSFORM.homogeneous__homogeneous, domain=None, range=Union[float, list[float]])

slots.displacementLookupTable__path = Slot(uri=NOID_TRANSFORM.path, name="displacementLookupTable__path", curie=NOID_TRANSFORM.curie('path'),
                   model_uri=NOID_TRANSFORM.displacementLookupTable__path, domain=None, range=str)

slots.displacementLookupTable__displacements = Slot(uri=NOID_TRANSFORM.displacements, name="displacementLookupTable__displacements", curie=NOID_TRANSFORM.curie('displacements'),
                   model_uri=NOID_TRANSFORM.displacementLookupTable__displacements, domain=None, range=Optional[Union[dict, SamplerConfig]])

slots.coordinateLookupTable__path = Slot(uri=NOID_TRANSFORM.path, name="coordinateLookupTable__path", curie=NOID_TRANSFORM.curie('path'),
                   model_uri=NOID_TRANSFORM.coordinateLookupTable__path, domain=None, range=str)

slots.coordinateLookupTable__lookup_table = Slot(uri=NOID_TRANSFORM.lookup_table, name="coordinateLookupTable__lookup_table", curie=NOID_TRANSFORM.curie('lookup_table'),
                   model_uri=NOID_TRANSFORM.coordinateLookupTable__lookup_table, domain=None, range=Optional[Union[dict, SamplerConfig]])

slots.samplerConfig__interpolation = Slot(uri=NOID_SAMPLER.interpolation, name="samplerConfig__interpolation", curie=NOID_SAMPLER.curie('interpolation'),
                   model_uri=NOID_TRANSFORM.samplerConfig__interpolation, domain=None, range=Optional[str])

slots.samplerConfig__extrapolation = Slot(uri=NOID_SAMPLER.extrapolation, name="samplerConfig__extrapolation", curie=NOID_SAMPLER.curie('extrapolation'),
                   model_uri=NOID_TRANSFORM.samplerConfig__extrapolation, domain=None, range=Optional[str])
