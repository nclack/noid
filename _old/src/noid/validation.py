"""Validation utilities for NOID schemas and data."""

from pathlib import Path
from typing import List, Union
from mlcroissant import validate as mlcroissant_validate


def validate_croissant(croissant_path: Union[str, Path]) -> List[str]:
    """
    Validate a croissant dataset file.

    Args:
        croissant_path: Path to croissant JSON file

    Returns:
        List of validation error messages (empty if valid)
    """
    try:
        mlcroissant_validate(str(croissant_path))
        return []
    except Exception as e:
        return [str(e)]
