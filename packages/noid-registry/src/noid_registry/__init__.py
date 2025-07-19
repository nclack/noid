"""
noid-registry: Generic JSON-LD registry system.

This package provides a generic registry pattern for mapping JSON-LD IRIs to factory functions,
with support for namespace abbreviations and JSON-LD processing utilities.
"""

from .abbreviation import (
    NamespaceAbbreviator,
    create_abbreviator_for_namespaces,
    extract_namespaces_from_objects,
)
from .adapter import PyLDDataAdapter
from .jsonld_processing import from_jsonld, to_jsonld
from .registry import (
    FactoryValidationError,
    Registry,
    RegistryError,
    UnknownIRIError,
    register,
    registry,
    set_namespace,
)
from .schema_utils import (
    find_workspace_schema_file,
    get_namespace_from_linkml_schema,
    get_schema_namespace,
)

__all__ = [
    "Registry",
    "RegistryError",
    "UnknownIRIError",
    "FactoryValidationError",
    "set_namespace",
    "register",
    "registry",
    "NamespaceAbbreviator",
    "create_abbreviator_for_namespaces",
    "extract_namespaces_from_objects",
    "from_jsonld",
    "to_jsonld",
    "PyLDDataAdapter",
    "get_namespace_from_linkml_schema",
    "get_schema_namespace",
    "find_workspace_schema_file",
]
