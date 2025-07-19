#!/usr/bin/env python3
"""
Task runner for noid-transforms development.

Usage:
    python tasks.py check      # Run quality checks
    python tasks.py build      # Run build process
    python tasks.py test       # Run tests only
    python tasks.py lint       # Run linting only
    python tasks.py format     # Auto-format code
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"Running {description}...")
    try:
        subprocess.run(cmd, check=True)
        print(f"✓ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed (exit code {e.returncode})")
        return False


def check() -> int:
    """Run all quality checks."""
    print("noid-transforms Quality Checks")
    print("=" * 50)

    success = run_command(["pre-commit", "run", "--all-files"], "quality checks")

    print("\n" + "=" * 50)
    if success:
        print("✓ All quality checks passed!")
        return 0
    else:
        print("✗ Some quality checks failed!")
        return 1


def build() -> int:
    """Run the build process."""
    print("noid-transforms Build Process")
    print("=" * 50)

    success = run_command(["python", "build.py"], "build process")

    if success:
        print("✓ Build completed successfully!")
        return 0
    else:
        print("✗ Build failed!")
        return 1


def test() -> int:
    """Run tests only."""
    success = run_command(["pytest", "tests/", "-v"], "tests")
    return 0 if success else 1


def lint() -> int:
    """Run linting only."""
    success = run_command(["ruff", "check", "src/"], "linting")
    return 0 if success else 1


def format_code() -> int:
    """Auto-format code."""
    success = run_command(["ruff", "format", "src/"], "code formatting")
    return 0 if success else 1


def main() -> int:
    """Main task runner."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    task = sys.argv[1]

    tasks = {
        "check": check,
        "build": build,
        "test": test,
        "lint": lint,
        "format": format_code,
    }

    if task not in tasks:
        print(f"Unknown task: {task}")
        print(f"Available tasks: {', '.join(tasks.keys())}")
        return 1

    return tasks[task]()


if __name__ == "__main__":
    sys.exit(main())
