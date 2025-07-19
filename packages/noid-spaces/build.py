#!/usr/bin/env python3
"""
Build script for generating Python models from LinkML schema.

This script generates Python classes and JSON-LD context from the spaces LinkML schema.
"""

from pathlib import Path
import shutil
import subprocess


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
    # Reference schema from common versioned location (go up to noid root)
    noid_root = base_dir.parent.parent
    schemas_dir = noid_root / "schemas" / "space"
    schema_file = schemas_dir / "v0.linkml.yaml"

    # Verify the schema file exists
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    print(f"Using schema file: {schema_file}")
    output_dir = base_dir / "_out"

    # Clean out the _out directory before regenerating everything
    if output_dir.exists():
        print(f"Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)

    # Create output directories
    output_dir.mkdir(exist_ok=True)
    (output_dir / "python").mkdir(exist_ok=True)
    (output_dir / "docs").mkdir(exist_ok=True)

    # Generate Python classes
    print("Generating Python classes...")
    cmd = ["gen-python", "--mergeimports", str(schema_file)]
    python_output = run_command(cmd, cwd=base_dir)

    # Write Python output to file with versioned name
    python_file = output_dir / "python" / "spaces_v0.py"
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

    # Write JSON-LD context to file with versioned name
    context_file = output_dir / "spaces_v0.context.jsonld"
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

    # Write JSON Schema to file with versioned name
    json_schema_file = output_dir / "spaces_v0.schema.json"
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
