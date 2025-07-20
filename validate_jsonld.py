#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pyld>=2.0.0",
#     "jsonschema>=4.0.0",
# ]
# ///
"""
Simple JSON-LD validation script for NOID project.

Usage:
    uv run validate_jsonld.py --all-transforms
    uv run validate_jsonld.py transforms/examples/transforms.jsonld -v
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List
import logging

from pyld import jsonld
import jsonschema


def setup_logging(verbose: bool):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def validate_json_syntax(file_path: Path) -> tuple[Dict[str, Any], List[str]]:
    """Validate JSON syntax and return data or errors."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f), []
    except json.JSONDecodeError as e:
        return {}, [f"Invalid JSON syntax: {e}"]
    except Exception as e:
        return {}, [f"Error reading file: {e}"]


def create_document_loader(base_dir: Path):
    """Create a document loader that handles relative paths and naming variations."""

    def document_loader(url: str, options: dict) -> dict:
        logging.debug(f"Document loader called with URL: {url}")

        # Handle relative paths
        if not url.startswith(("http://", "https://", "file://")):
            # Resolve relative path from the JSON-LD file's directory
            local_path = (base_dir / url).resolve()
            logging.debug(f"Resolved path: {local_path}")

            if local_path.exists():
                logging.debug(f"Loading local context: {local_path}")
                with open(local_path, "r", encoding="utf-8") as f:
                    document = json.load(f)
                return {
                    "contextUrl": None,
                    "document": document,
                    "documentUrl": f"file://{local_path.absolute()}",
                }

            # Try common naming variations and path corrections
            variations = []

            # If the URL doesn't start with ".." but we're looking at _out/, try ../_out/
            if url.startswith("_out/") and not url.startswith(".."):
                corrected_url = "../" + url
                corrected_path = (base_dir / corrected_url).resolve()
                variations.append(corrected_url)

            if url.endswith(".context.jsonld"):
                base_name = url[:-15]  # Remove '.context.jsonld'
                # Try versioned names
                variations.append(
                    f"{base_name}_v0.context.jsonld"
                )  # transform -> transform_v0
                variations.append(
                    f"{base_name}_v0.context.jsonld"
                )  # sampler -> sampler_v0

                # Try path-corrected versions too
                if url.startswith("_out/"):
                    filename = url.split("/")[-1]  # Get just the filename
                    base_filename = filename[:-15]  # Remove '.context.jsonld'
                    variations.append(f"../_out/{base_filename}s_v0.context.jsonld")
                    variations.append(f"../_out/{base_filename}_v0.context.jsonld")

            for variation in variations:
                variant_path = (base_dir / variation).resolve()
                logging.debug(f"Trying variation: {variant_path}")
                if variant_path.exists():
                    logging.debug(f"Loading context variation: {variant_path}")
                    with open(variant_path, "r", encoding="utf-8") as f:
                        document = json.load(f)
                    return {
                        "contextUrl": None,
                        "document": document,
                        "documentUrl": f"file://{variant_path.absolute()}",
                    }

            logging.debug(f"Local context file not found: {local_path}")

        # Fall back to default loader for URLs
        logging.debug(f"Falling back to default loader for: {url}")
        return jsonld.requests_document_loader()(url, options)

    return document_loader


def validate_jsonld_processing(data: Dict[str, Any], base_dir: Path) -> List[str]:
    """Validate JSON-LD processing with pyld and check namespace resolution."""
    errors = []

    try:
        # Use custom document loader for relative context resolution
        options = {"documentLoader": create_document_loader(base_dir)}

        # Test basic expansion - this resolves all terms to full IRIs
        expanded = jsonld.expand(data, options)
        if not isinstance(expanded, list):
            errors.append("JSON-LD expansion should produce a list")

        # Check that expansion actually resolved terms (no unresolved terms should remain)
        if expanded:
            errors.extend(_check_namespace_resolution(expanded))

        # Test compaction if context exists
        if isinstance(data, dict) and "@context" in data:
            compacted = jsonld.compact(data, data["@context"], options)
            # Verify compaction worked (should match original structure)
            if not isinstance(compacted, dict):
                errors.append("JSON-LD compaction should produce an object")

        # Test flattening
        flattened = jsonld.flatten(data, None, options)
        if not isinstance(flattened, (dict, list)):
            errors.append("JSON-LD flattening should produce an object or array")

    except Exception as e:
        errors.append(f"JSON-LD processing error: {e}")

    return errors


def _check_namespace_resolution(expanded: List[Dict[str, Any]]) -> List[str]:
    """Check that all terms in expanded JSON-LD are properly resolved to IRIs."""
    errors = []

    def check_object(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key

                # Keys should be IRIs (start with http/https) or JSON-LD keywords (start with @)
                if not (key.startswith(("http://", "https://")) or key.startswith("@")):
                    errors.append(f"Unresolved term '{key}' at {current_path}")

                check_object(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_object(item, f"{path}[{i}]")

    for i, item in enumerate(expanded):
        check_object(item, f"[{i}]")

    return errors


def find_schema_file(file_path: Path) -> Path | None:
    """Find appropriate schema file for validation."""
    # Find project root
    current = file_path.parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            break
        current = current.parent

    # Simple schema detection based on path
    if "transforms" in str(file_path):
        schema_candidates = [
            current / "transforms" / "_out" / "json-schema" / "transforms.schema.json",
            current
            / "packages"
            / "noid-transforms"
            / "_out"
            / "transform_v0.schema.json",
        ]
    elif "spaces" in str(file_path):
        schema_candidates = [
            current / "packages" / "noid-spaces" / "_out" / "spaces_v0.schema.json"
        ]
    else:
        return None

    for schema_path in schema_candidates:
        if schema_path.exists():
            return schema_path

    return None


def validate_against_schema(data: Dict[str, Any], file_path: Path) -> List[str]:
    """Validate against JSON Schema if available."""
    schema_file = find_schema_file(file_path)
    if not schema_file:
        return []  # No schema found, skip validation

    try:
        with open(schema_file, "r") as f:
            schema = json.load(f)
        jsonschema.validate(data, schema)
        return []
    except jsonschema.ValidationError as e:
        return [f"Schema validation error: {e.message}"]
    except Exception as e:
        logging.warning(f"Could not validate against schema: {e}")
        return []


def validate_file(file_path: Path, verbose: bool = False) -> bool:
    """Validate a single JSON-LD file. Returns True if valid."""
    if not file_path.exists():
        print(f"❌ {file_path}: File not found")
        return False

    # Load and validate JSON syntax
    data, syntax_errors = validate_json_syntax(file_path)
    if syntax_errors:
        print(f"❌ {file_path}: INVALID")
        for error in syntax_errors:
            print(f"   ERROR: {error}")
        return False

    # Collect all validation errors
    all_errors = []
    all_errors.extend(validate_jsonld_processing(data, file_path.parent))
    all_errors.extend(validate_against_schema(data, file_path))

    # Report results
    if all_errors:
        print(f"❌ {file_path}: INVALID")
        for error in all_errors:
            print(f"   ERROR: {error}")
        return False
    else:
        print(f"✅ {file_path}: VALID")
        return True


def find_all_example_files() -> List[Path]:
    """Find all JSON-LD example files in the project."""
    cwd = Path.cwd()
    example_files = []

    # Search common example locations
    search_paths = [
        cwd / "transforms" / "examples",
        cwd / "spaces" / "examples",
        cwd / "packages" / "noid-transforms" / "examples",
        cwd / "packages" / "noid-spaces" / "examples",
        cwd / "examples",
    ]

    for path in search_paths:
        if path.exists():
            example_files.extend(path.glob("*.jsonld"))

    return example_files


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate JSON-LD files")
    parser.add_argument("files", nargs="*", type=Path, help="JSON-LD files to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    setup_logging(args.verbose)

    # Collect files to validate
    files_to_validate = list(args.files)

    # If no specific files provided, find all example files
    if not files_to_validate:
        files_to_validate = find_all_example_files()
        if not files_to_validate:
            print("ERROR: No JSON-LD files found to validate")
            return 1
        print(f"Found {len(files_to_validate)} example files to validate")

    # Validate all files
    all_valid = True
    for file_path in files_to_validate:
        valid = validate_file(file_path, args.verbose)
        all_valid &= valid

    # Final summary
    if all_valid:
        print(f"\n🎉 All {len(files_to_validate)} files are valid JSON-LD!")
        return 0
    else:
        print("\n💥 Some files failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
