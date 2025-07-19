#!/usr/bin/env python3
"""
Build script for generating Python models from LinkML schema.

This script generates Python classes and JSON-LD context from the spaces LinkML schema.
"""

import os
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result.stdout


def main():
    """Generate Python models and other artifacts from LinkML schema."""
    # Get the directory containing this script
    base_dir = Path(__file__).parent
    # Reference schema from common versioned location
    schemas_dir = base_dir.parent.parent / "schemas" / "v0"
    schema_file = schemas_dir / "space.linkml.yaml"
    output_dir = base_dir / "_out"

    # Create output directories
    output_dir.mkdir(exist_ok=True)
    (output_dir / "python").mkdir(exist_ok=True)
    (output_dir / "docs").mkdir(exist_ok=True)

    # Generate Python classes
    print("Generating Python classes...")
    cmd = ["gen-python", "--mergeimports", str(schema_file)]
    python_output = run_command(cmd, cwd=base_dir)
    
    # Write Python output to file
    python_file = output_dir / "python" / "space.v0.py"
    python_file.write_text(python_output)

    # Generate JSON-LD context
    print("Generating JSON-LD context...")
    context_output = run_command(
        [
            "gen-jsonld-context",
            "--mergeimports",
            str(schema_file),
        ],
        cwd=base_dir,
    )
    
    # Write JSON-LD context to file
    context_file = output_dir / "space.v0.context.jsonld"
    context_file.write_text(context_output)

    # Generate JSON Schema
    print("Generating JSON Schema...")
    json_schema_output = run_command(
        [
            "gen-json-schema",
            "--mergeimports",
            str(schema_file),
        ],
        cwd=base_dir,
    )
    
    # Write JSON Schema to file
    json_schema_file = output_dir / "space.v0.schema.json"
    json_schema_file.write_text(json_schema_output)

    # Generate documentation
    print("Generating documentation...")
    run_command(
        [
            "gen-doc",
            "--mergeimports",
            "--directory",
            str(output_dir / "docs"),
            str(schema_file),
        ],
        cwd=base_dir,
    )

    print("Build completed successfully!")


if __name__ == "__main__":
    main()
