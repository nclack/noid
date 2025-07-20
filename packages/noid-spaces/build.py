#!/usr/bin/env python3
"""
Build script for spaces schema artifacts.

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

from collections.abc import Sequence
import json
import logging
from pathlib import Path
import shutil
import subprocess
import sys

logging.basicConfig(level=logging.INFO)


def run_command(
    cmd: list[str], description: str, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Run a command and handle errors."""
    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, cwd=cwd
        )
        logging.info(f"✓ {description}")
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"✗ Failed to run {description}")
        logging.error(f"Command: {' '.join(cmd)}")
        logging.error(f"Return code: {e.returncode}")
        logging.error(f"STDOUT: {e.stdout}")
        logging.error(f"STDERR: {e.stderr}")
        sys.exit(1)


def generate_artifacts(schema_file: Path, out_dir: Path, schema_name: str) -> None:
    """Generate artifacts for a single schema."""
    # Generate JSON Schema
    json_schema_file = out_dir / f"{schema_name}.schema.json"
    result = run_command(
        ["gen-json-schema", str(schema_file)], f"{schema_name} JSON Schema generation"
    )
    json_schema_file.write_text(result.stdout)

    # Generate JSON-LD context
    jsonld_file = out_dir / f"{schema_name}.context.jsonld"
    result = run_command(
        ["gen-jsonld-context", str(schema_file)],
        f"{schema_name} JSON-LD context generation",
    )
    jsonld_file.write_text(result.stdout)

    # Generate Python classes
    python_dir = out_dir / "python"
    python_dir.mkdir(exist_ok=True)
    python_file = python_dir / f"{schema_name}.py"
    result = run_command(
        ["gen-python", str(schema_file)], f"{schema_name} Python classes generation"
    )
    python_file.write_text(result.stdout)

    # Generate documentation
    docs_dir = out_dir / "docs"
    docs_dir.mkdir(exist_ok=True)

    run_command(
        ["gen-doc", str(schema_file), "-d", str(docs_dir)],
        f"{schema_name} documentation generation",
    )


def validate_examples(script_dir: Path) -> None:
    """Validate example files against schemas."""

    examples_dir = script_dir / "examples"
    if not examples_dir.exists():
        logging.info("No examples directory found, skipping validation")
        return

    # Validate JSON examples
    json_files = list(examples_dir.glob("*.json"))
    for json_file in json_files:
        try:
            with open(json_file) as f:
                json.load(f)  # Validate JSON syntax
            logging.info(f"✓ {json_file.name} is valid JSON")
        except json.JSONDecodeError as e:
            logging.error(f"✗ {json_file.name} has invalid JSON: {e}")

    # Validate JSON-LD examples using comprehensive validator
    jsonld_files = list(examples_dir.glob("*.jsonld"))
    if jsonld_files:
        # Try to use the comprehensive validator if available
        project_root = script_dir.parent
        validator_script = project_root / "validate_jsonld.py"

        if validator_script.exists():
            # Use uv run to automatically handle dependencies
            cmd = ["uv", "run", str(validator_script)] + [str(f) for f in jsonld_files]
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=project_root
            )
            if result.stdout:
                logging.info(result.stdout)
            if result.stderr:
                logging.error(f"Errors: {result.stderr}")
        else:
            # Fallback to basic validation
            _basic_jsonld_validation(jsonld_files)


def _basic_jsonld_validation(jsonld_files: Sequence[Path]) -> None:
    """Basic JSON-LD validation fallback."""
    for jsonld_file in jsonld_files:
        try:
            with open(jsonld_file) as f:
                data = json.load(f)
            # Basic JSON-LD checks
            if isinstance(data, dict):
                if "@context" not in data:
                    logging.warning(f"  ⚠ {jsonld_file.name}: No @context found")
                if "@type" not in data and "examples" not in data:
                    logging.warning(f"  ⚠ {jsonld_file.name}: No @type found")
            logging.info(f"✓ {jsonld_file.name} validated")
        except json.JSONDecodeError as e:
            logging.error(f"✗ {jsonld_file.name} has invalid JSON: {e}")


def run_tests(script_dir: Path) -> None:
    """Run tests for the enhanced library."""

    tests_dir = script_dir / "tests"
    if not tests_dir.exists():
        logging.info("No tests directory found, skipping tests")
        return

    # Run pytest using uv to ensure workspace dependencies are available
    run_command(
        ["uv", "run", "pytest", str(tests_dir), "-v"],
        "Running tests",
        cwd=script_dir,
    )


def run_examples(script_dir: Path) -> None:
    """Run usage examples to ensure they work."""

    examples_dir = script_dir / "examples"
    usage_examples = examples_dir / "usage_examples.py"

    if usage_examples.exists():
        run_command(
            ["uv", "run", str(usage_examples)], "Running usage examples", cwd=script_dir
        )
    else:
        logging.info("No usage examples found, skipping")


def lint_code(script_dir: Path) -> None:
    """Run code linting."""

    src_dir = script_dir / "src"
    if not src_dir.exists():
        logging.info("No src directory found, skipping linting")
        return

    # Run ruff check (includes type annotation checking via ANN rules)
    run_command(
        ["uv", "run", "ruff", "check", str(src_dir)],
        "Code linting and type annotations check",
        cwd=script_dir,
    )

    # Run ruff format check
    run_command(
        ["uv", "run", "ruff", "format", "--check", str(src_dir)],
        "Code formatting check",
        cwd=script_dir,
    )


def main() -> None:
    """Generate all artifacts from LinkML schemas and run full build process."""
    script_dir = Path(__file__).parent
    out_dir = script_dir / "_out"

    logging.info("spaces Build Process")
    logging.info("=" * 50)

    # Clean and create output directory
    if out_dir.exists():
        shutil.rmtree(out_dir)
        logging.info("✓ Cleaned existing _out directory")
    out_dir.mkdir(exist_ok=True)

    # Reference schemas from new organized structure
    schemas_root = script_dir.parent.parent / "schemas"

    # Generate artifacts for spaces schema
    spaces_file = schemas_root / "space" / "v0.linkml.yaml"
    if spaces_file.exists():
        generate_artifacts(spaces_file, out_dir, "spaces_v0")

    logging.info(f"✓ All LinkML artifacts generated successfully! Output: {out_dir}")

    # Validate examples
    validate_examples(script_dir)

    # Run tests
    run_tests(script_dir)

    # Run examples
    run_examples(script_dir)

    # Lint code
    lint_code(script_dir)

    logging.info("✓ Build process completed successfully!")


if __name__ == "__main__":
    main()
