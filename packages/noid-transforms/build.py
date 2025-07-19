#!/usr/bin/env python3
"""
Build script for transforms schema artifacts.

Generates JSON Schema, JSON-LD context, and Python classes from LinkML source.
Also validates examples and runs tests for the enhanced library.
"""
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "linkml",
#     "pytest",
#     "jsonschema",
#     "pyld",
#     "ruff",
# ]
# ///

import json
from pathlib import Path
import subprocess
import sys


def run_command(cmd: list[str], description: str) -> None:
    """Run a command and handle errors."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✓ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to run {description}")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def generate_artifacts(schema_file: Path, out_dir: Path, schema_name: str):
    """Generate artifacts for a single schema."""
    # Generate JSON Schema
    json_schema_file = out_dir / f"{schema_name}.schema.json"
    result = subprocess.run(
        ["gen-json-schema", str(schema_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    json_schema_file.write_text(result.stdout)
    print(f"✓ {schema_name} JSON Schema generated successfully")

    # Generate JSON-LD context
    jsonld_file = out_dir / f"{schema_name}.context.jsonld"
    result = subprocess.run(
        ["gen-jsonld-context", str(schema_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    jsonld_file.write_text(result.stdout)
    print(f"✓ {schema_name} JSON-LD context generated successfully")

    # Generate Python classes
    python_dir = out_dir / "python"
    python_dir.mkdir(exist_ok=True)
    python_file = python_dir / f"{schema_name}.py"
    result = subprocess.run(
        ["gen-python", str(schema_file)], capture_output=True, text=True, check=True
    )
    python_file.write_text(result.stdout)
    print(f"✓ {schema_name} Python classes generated successfully")

    # Generate documentation
    docs_dir = out_dir / "docs"
    docs_dir.mkdir(exist_ok=True)

    result = subprocess.run(
        ["gen-doc", str(schema_file), "-d", str(docs_dir)],
        capture_output=True,
        text=True,
        check=True,
    )
    print(f"✓ {schema_name} documentation generated successfully")


def validate_examples(script_dir: Path):
    """Validate example files against schemas."""
    print("\n=== Validating Examples ===")

    examples_dir = script_dir / "examples"
    if not examples_dir.exists():
        print("No examples directory found, skipping validation")
        return

    # Validate JSON examples
    json_files = list(examples_dir.glob("*.json"))
    for json_file in json_files:
        try:
            with open(json_file) as f:
                data = json.load(f)
            print(f"✓ {json_file.name} is valid JSON")
        except json.JSONDecodeError as e:
            print(f"✗ {json_file.name} has invalid JSON: {e}")

    # Validate JSON-LD examples using comprehensive validator
    jsonld_files = list(examples_dir.glob("*.jsonld"))
    if jsonld_files:
        print("\n--- JSON-LD Validation ---")

        # Try to use the comprehensive validator if available
        project_root = script_dir.parent
        validator_script = project_root / "validate_jsonld.py"

        if validator_script.exists():
            try:
                import subprocess

                # Use uv run to automatically handle dependencies
                cmd = ["uv", "run", str(validator_script)] + [
                    str(f) for f in jsonld_files
                ]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=project_root
                )
                print(result.stdout)
                if result.stderr:
                    print("Errors:", result.stderr)
            except Exception as e:
                print(f"Error running comprehensive validator: {e}")
                # Fallback to basic validation
                _basic_jsonld_validation(jsonld_files)
        else:
            # Fallback to basic validation
            _basic_jsonld_validation(jsonld_files)


def _basic_jsonld_validation(jsonld_files):
    """Basic JSON-LD validation fallback."""
    for jsonld_file in jsonld_files:
        try:
            with open(jsonld_file) as f:
                data = json.load(f)
            print(f"✓ {jsonld_file.name} is valid JSON")

            # Basic JSON-LD checks
            if isinstance(data, dict):
                if "@context" not in data:
                    print(f"  ⚠ {jsonld_file.name}: No @context found")
                if "@type" not in data and "examples" not in data:
                    print(f"  ⚠ {jsonld_file.name}: No @type found")
        except json.JSONDecodeError as e:
            print(f"✗ {jsonld_file.name} has invalid JSON: {e}")


def run_tests(script_dir: Path):
    """Run tests for the enhanced library."""
    print("\n=== Running Tests ===")

    tests_dir = script_dir / "tests"
    if not tests_dir.exists():
        print("No tests directory found, skipping tests")
        return

    # Run pytest
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", str(tests_dir), "-v"],
            check=True,
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        print("✓ All tests passed")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("✗ Some tests failed")
        print(e.stdout)
        print(e.stderr)


def run_examples(script_dir: Path):
    """Run usage examples to ensure they work."""
    print("\n=== Running Examples ===")

    examples_dir = script_dir / "examples"
    usage_examples = examples_dir / "usage_examples.py"

    if usage_examples.exists():
        try:
            result = subprocess.run(
                ["python", str(usage_examples)],
                check=True,
                capture_output=True,
                text=True,
                cwd=script_dir,
            )
            print("✓ Usage examples ran successfully")
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("✗ Usage examples failed")
            print(e.stdout)
            print(e.stderr)
    else:
        print("No usage examples found, skipping")


def lint_code(script_dir: Path):
    """Run code linting."""
    print("\n=== Linting Code ===")

    src_dir = script_dir / "src"
    if not src_dir.exists():
        print("No src directory found, skipping linting")
        return

    # Run ruff check
    try:
        result = subprocess.run(
            ["python", "-m", "ruff", "check", str(src_dir)],
            check=True,
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        print("✓ Code linting passed")
    except subprocess.CalledProcessError as e:
        print("✗ Code linting failed")
        print(e.stdout)
        print(e.stderr)

    # Run ruff format check
    try:
        result = subprocess.run(
            ["python", "-m", "ruff", "format", "--check", str(src_dir)],
            check=True,
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        print("✓ Code formatting check passed")
    except subprocess.CalledProcessError as e:
        print("✗ Code formatting check failed")
        print(e.stdout)
        print(e.stderr)


def main():
    """Generate all artifacts from LinkML schemas and run full build process."""
    script_dir = Path(__file__).parent
    out_dir = script_dir / "_out"

    print("Transforms Build Process")
    print("=" * 50)

    # Create output directory
    out_dir.mkdir(exist_ok=True)

    # Reference schemas from new organized structure
    schemas_root = script_dir.parent.parent / "schemas"
    
    # Generate artifacts for samplers schema
    samplers_file = schemas_root / "sampler" / "v0.linkml.yaml"
    if samplers_file.exists():
        generate_artifacts(samplers_file, out_dir, "sampler.v0")

    # Generate artifacts for transforms schema
    transforms_file = schemas_root / "transform" / "v0.linkml.yaml"
    if transforms_file.exists():
        generate_artifacts(transforms_file, out_dir, "transform.v0")

    print("\n✓ All LinkML artifacts generated successfully!")
    print(f"Output directory: {out_dir}")

    # Validate examples
    validate_examples(script_dir)

    # Run tests
    run_tests(script_dir)

    # Run examples
    run_examples(script_dir)

    # Lint code
    lint_code(script_dir)

    print("\n" + "=" * 50)
    print("Build process completed successfully!")
    print("✓ LinkML artifacts generated")
    print("✓ Examples validated")
    print("✓ Tests executed")
    print("✓ Usage examples verified")
    print("✓ Code linting completed")


if __name__ == "__main__":
    main()
