"""
noid-registry: Generic JSON-LD registry system.

This package provides a generic registry pattern for mapping JSON-LD IRIs to factory functions,
with support for namespace abbreviations and JSON-LD processing utilities.
"""

from .registry import Registry, RegistryError, UnknownIRIError, FactoryValidationError, set_namespace, register, registry
from .abbreviation import NamespaceAbbreviator, create_abbreviator_for_namespaces, extract_namespaces_from_objects
from .jsonld_processing import from_jsonld, to_jsonld
from .adapter import PyLDDataAdapter
from .schema_utils import (
    get_namespace_from_linkml_schema,
    get_schema_namespace,
    find_workspace_schema_file,
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