"""
Build and quality check scripts for noid-transforms.

These functions are exposed as console scripts via pyproject.toml.
"""

from pathlib import Path
import subprocess
import sys


def check_main() -> int:
    """Run all quality checks using pre-commit."""
    print("noid-transforms Quality Checks")
    print("=" * 50)
    print("Running pre-commit hooks on all files...")

    try:
        # Run pre-commit on all files (not just staged ones)
        subprocess.run(
            ["pre-commit", "run", "--all-files"],
            check=True,
        )
        print("\n" + "=" * 50)
        print("✓ All quality checks passed!")
        return 0

    except FileNotFoundError:
        print("✗ pre-commit not installed. Install with:")
        print("    uv add --dev pre-commit")
        print("    pre-commit install")
        return 1

    except subprocess.CalledProcessError:
        print("\n" + "=" * 50)
        print("✗ Some quality checks failed!")
        print("\nTo fix formatting issues automatically, run:")
        print("    pre-commit run --all-files")
        return 1


def build_main() -> int:
    """Run the full build process."""
    # Import the build.py main function
    import importlib.util
    import os

    # Find the build.py file relative to this package
    build_script = Path(__file__).parent.parent.parent / "build.py"

    if not build_script.exists():
        print("✗ build.py not found")
        return 1

    try:
        # Load and execute build.py
        spec = importlib.util.spec_from_file_location("build", build_script)
        if spec and spec.loader:
            build_module = importlib.util.module_from_spec(spec)
            sys.modules["build"] = build_module
            spec.loader.exec_module(build_module)

            # Change to the correct directory for build
            old_cwd = os.getcwd()
            os.chdir(build_script.parent)
            try:
                build_module.main()
                return 0
            finally:
                os.chdir(old_cwd)
        else:
            print("✗ Could not load build.py")
            return 1

    except Exception as e:
        print(f"✗ Build failed: {e}")
        return 1


if __name__ == "__main__":
    # Allow running as python -m noid_transforms.scripts
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        sys.exit(build_main())
    else:
        sys.exit(check_main())
