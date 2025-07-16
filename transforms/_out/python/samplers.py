# Auto generated from samplers.linkml.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-07-16T13:18:19
# Schema: samplers
#
# id: https://github.com/nclack/noid/transforms/samplers.linkml
# description: Interpolation and extrapolation methods for array sampling and coordinate transforms
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

from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"
version = "0.1.0"

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
NOID_SAMPLERS = CurieNamespace('noid_samplers', 'https://github.com/nclack/noid/transforms/samplers/')
DEFAULT_ = NOID_SAMPLERS


# Types

# Class references



@dataclass(repr=False)
class SamplerConfig(YAMLRoot):
    """
    Configuration for sampling transforms (displacements and lookup tables)
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = NOID_SAMPLERS["SamplerConfig"]
    class_class_curie: ClassVar[str] = "noid_samplers:SamplerConfig"
    class_name: ClassVar[str] = "SamplerConfig"
    class_model_uri: ClassVar[URIRef] = NOID_SAMPLERS.SamplerConfig

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

slots.samplerConfig__interpolation = Slot(uri=NOID_SAMPLERS.interpolation, name="samplerConfig__interpolation", curie=NOID_SAMPLERS.curie('interpolation'),
                   model_uri=NOID_SAMPLERS.samplerConfig__interpolation, domain=None, range=Optional[str])

slots.samplerConfig__extrapolation = Slot(uri=NOID_SAMPLERS.extrapolation, name="samplerConfig__extrapolation", curie=NOID_SAMPLERS.curie('extrapolation'),
                   model_uri=NOID_SAMPLERS.samplerConfig__extrapolation, domain=None, range=Optional[str])
