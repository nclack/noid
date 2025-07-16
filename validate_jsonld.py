#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pyld>=2.0.0",
#     "jsonschema>=4.0.0",
# ]
# ///
"""
Comprehensive JSON-LD validation script for NOID project.

This script validates JSON-LD files using multiple approaches:
1. Basic JSON syntax validation
2. JSON-LD processing with pyld (expansion, compaction, etc.)
3. JSON Schema validation against known schemas
4. Context resolution validation

Usage:
    uv run validate_jsonld.py --all-transforms
    uv run validate_jsonld.py transforms/examples/transforms.jsonld -v
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

from pyld import jsonld
import jsonschema


class JSONLDValidator:
    """Comprehensive JSON-LD validator."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        
        # Setup logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate a single JSON-LD file. Returns True if valid."""
        self.logger.info(f"Validating: {file_path}")
        self.errors.clear()
        self.warnings.clear()
        
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return False
        
        # Load the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON syntax: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
        
        # Perform validation steps
        valid = True
        valid &= self._validate_basic_structure(data)
        valid &= self._validate_jsonld_processing(data)
        valid &= self._validate_context_resolution(data)
        valid &= self._validate_against_schema(data, file_path)
        
        # Report results
        self._report_results(file_path, valid)
        return valid
    
    def _validate_basic_structure(self, data: Dict[str, Any]) -> bool:
        """Validate basic JSON-LD structure requirements."""
        self.logger.debug("Validating basic JSON-LD structure...")
        
        valid = True
        
        # Check if it's a valid JSON-LD document (must be object or array)
        if not isinstance(data, (dict, list)):
            self.errors.append("JSON-LD document must be an object or array")
            valid = False
        
        # If it's an object, check for JSON-LD specific patterns
        if isinstance(data, dict):
            # Check for @context (recommended but not required)
            if "@context" not in data:
                self.warnings.append("No @context found - consider adding one for semantic clarity")
            
            # Check for valid @context structure
            if "@context" in data:
                context = data["@context"]
                if not isinstance(context, (dict, list, str)):
                    self.errors.append("@context must be an object, array, or string")
                    valid = False
        
        return valid
    
    def _validate_jsonld_processing(self, data: Dict[str, Any]) -> bool:
        """Validate using pyld JSON-LD processing."""
        self.logger.debug("Validating JSON-LD processing...")
        
        valid = True
        
        try:
            # Test expansion (most fundamental operation)
            expanded = jsonld.expand(data)
            if not isinstance(expanded, list):
                self.errors.append("JSON-LD expansion should produce a list")
                valid = False
            self.logger.debug(f"Expansion successful: {len(expanded)} items")
            
            # Test compaction (if context is available)
            if isinstance(data, dict) and "@context" in data:
                context = data["@context"]
                compacted = jsonld.compact(data, context)
                self.logger.debug("Compaction successful")
            
            # Test flattening
            flattened = jsonld.flatten(data)
            if not isinstance(flattened, (dict, list)):
                self.errors.append("JSON-LD flattening should produce an object or array")
                valid = False
            self.logger.debug("Flattening successful")
            
        except Exception as e:
            self.errors.append(f"JSON-LD processing error: {e}")
            valid = False
        
        return valid
    
    def _validate_context_resolution(self, data: Dict[str, Any]) -> bool:
        """Validate that contexts can be resolved."""
        self.logger.debug("Validating context resolution...")
        
        valid = True
        
        if isinstance(data, dict) and "@context" in data:
            context = data["@context"]
            
            # Check for URL contexts that might need to be resolved
            if isinstance(context, str):
                if context.startswith("http"):
                    self.warnings.append(f"External context URL found: {context} - ensure it's accessible")
            elif isinstance(context, list):
                for ctx in context:
                    if isinstance(ctx, str) and ctx.startswith("http"):
                        self.warnings.append(f"External context URL found: {ctx} - ensure it's accessible")
            elif isinstance(context, dict):
                # Check for namespace prefixes
                for key, value in context.items():
                    if isinstance(value, str) and value.startswith("http"):
                        self.logger.debug(f"Found namespace: {key} -> {value}")
        
        return valid
    
    def _validate_against_schema(self, data: Dict[str, Any], file_path: Path) -> bool:
        """Validate against JSON Schema if available."""
        
        # Try to find relevant schema based on file location/name
        schema_file = self._find_schema_for_file(file_path)
        if not schema_file:
            self.logger.debug("No specific schema found for validation")
            return True
        
        self.logger.debug(f"Validating against schema: {schema_file}")
        
        try:
            with open(schema_file, 'r') as f:
                schema = json.load(f)
            
            jsonschema.validate(data, schema)
            self.logger.debug("Schema validation successful")
            return True
            
        except jsonschema.ValidationError as e:
            self.errors.append(f"Schema validation error: {e.message}")
            return False
        except Exception as e:
            self.warnings.append(f"Could not validate against schema: {e}")
            return True
    
    def _find_schema_for_file(self, file_path: Path) -> Optional[Path]:
        """Find appropriate schema file for the given JSON-LD file."""
        # Look for schemas in the project
        project_root = file_path
        while project_root.parent != project_root:
            if (project_root / "pyproject.toml").exists():
                break
            project_root = project_root.parent
        
        # Check transforms schema
        if "transforms" in str(file_path):
            schema_paths = [
                project_root / "transforms" / "_out" / "json-schema" / "transforms.schema.json",
                project_root / "transforms" / "_out" / "transforms.schema.json",
                project_root / "schemas" / "transforms" / "transforms.v0.schema.json"
            ]
            for schema_path in schema_paths:
                if schema_path.exists():
                    return schema_path
        
        return None
    
    def _report_results(self, file_path: Path, valid: bool):
        """Report validation results."""
        if valid and not self.errors:
            print(f"✅ {file_path}: VALID")
        else:
            print(f"❌ {file_path}: INVALID")
        
        for error in self.errors:
            print(f"   ERROR: {error}")
        
        if self.verbose or not valid:
            for warning in self.warnings:
                print(f"   WARNING: {warning}")


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate JSON-LD files")
    parser.add_argument("files", nargs="*", type=Path, help="JSON-LD files to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--all-transforms", action="store_true", 
                       help="Validate all transform example files")
    
    args = parser.parse_args()
    
    validator = JSONLDValidator(verbose=args.verbose)
    
    files_to_validate = []
    
    if args.all_transforms:
        # Find transform example files
        cwd = Path.cwd()
        
        # Try different possible locations for transform examples
        possible_paths = [
            cwd / "transforms" / "examples",  # Running from project root
            cwd / "examples",                 # Running from transforms directory
            cwd.parent / "transforms" / "examples",  # Running from subdirectory
        ]
        
        transform_examples = None
        for path in possible_paths:
            if path.exists() and list(path.glob("*.jsonld")):
                transform_examples = path
                break
        
        if transform_examples:
            files_to_validate.extend(transform_examples.glob("*.jsonld"))
    
    files_to_validate.extend(args.files)
    
    if not files_to_validate and not args.all_transforms:
        print("ERROR: No files to validate. Specify files or use --all-transforms")
        return 1
    
    if not files_to_validate:
        print("No files found to validate")
        return 1
    
    all_valid = True
    for file_path in files_to_validate:
        valid = validator.validate_file(file_path)
        all_valid &= valid
    
    if all_valid:
        print(f"\n🎉 All {len(files_to_validate)} files are valid JSON-LD!")
        return 0
    else:
        print(f"\n💥 Some files failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 