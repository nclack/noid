"""
Utilities for extracting configuration from LinkML schemas.

This module provides functions to extract namespace URLs and other configuration
from LinkML schema files, ensuring the schema remains the single source of truth.
"""

from pathlib import Path

import yaml


def get_namespace_from_linkml_schema(schema_file_path: str | Path) -> str:
    """
    Extract the default namespace URL from a LinkML schema file.

    Args:
        schema_file_path: Path to the LinkML YAML schema file

    Returns:
        The namespace URL defined by the default_prefix in the schema

    Raises:
        FileNotFoundError: If the schema file doesn't exist
        KeyError: If the schema doesn't have the expected structure

    Example:
        >>> get_namespace_from_linkml_schema("transform.linkml.yaml")
        "https://github.com/nclack/noid/schemas/transform.v0.context.jsonld"
    """
    schema_path = Path(schema_file_path)

    if not schema_path.exists():
        raise FileNotFoundError(f"LinkML schema file not found: {schema_path}")

    with open(schema_path) as f:
        schema = yaml.safe_load(f)

    if "default_prefix" not in schema:
        raise KeyError(f"No 'default_prefix' found in schema: {schema_path}")

    default_prefix = schema["default_prefix"]

    if "prefixes" not in schema or default_prefix not in schema["prefixes"]:
        raise KeyError(
            f"Default prefix '{default_prefix}' not found in prefixes: {schema_path}"
        )

    namespace_url = schema["prefixes"][default_prefix]
    return namespace_url


def find_workspace_schema_file(schema_name: str, version: str = "v0") -> Path:
    """
    Find a schema file in the workspace schemas directory.

    Args:
        schema_name: Name of the schema (e.g., "transform", "sampler", "space")
        version: Schema version (default: "v0")

    Returns:
        Path to the schema file

    Raises:
        FileNotFoundError: If the schema file cannot be found
    """
    # Start from this module and work up to find the workspace root
    current_dir = Path(__file__).parent

    # Navigate up to find the workspace root (contains schemas/ directory)
    workspace_root = None
    for parent in [current_dir] + list(current_dir.parents):
        schemas_dir = parent / "schemas"
        if schemas_dir.exists():
            workspace_root = parent
            break

    if workspace_root is None:
        raise FileNotFoundError("Could not find workspace root with schemas/ directory")

    schema_file = workspace_root / "schemas" / schema_name / f"{version}.linkml.yaml"

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    return schema_file


def get_schema_namespace(schema_name: str, version: str = "v0") -> str:
    """
    Get the namespace URL for a specific schema.

    Args:
        schema_name: Name of the schema (e.g., "transform", "sampler", "space")
        version: Schema version (default: "v0")

    Returns:
        The namespace URL for the schema

    Example:
        >>> get_schema_namespace("transform")
        "https://github.com/nclack/noid/schemas/transform.v0.context.jsonld"
    """
    schema_file = find_workspace_schema_file(schema_name, version)
    return get_namespace_from_linkml_schema(schema_file)
