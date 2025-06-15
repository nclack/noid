"""SHACL-based semantic validation for NOID schemas and data."""

import json
from pathlib import Path
from typing import Any, Dict, List, Union
from rdflib import Graph, Dataset
from pyshacl import validate
from importlib import resources
try:
    from mlcroissant import validate as mlcroissant_validate
except ImportError:
    # Fallback if mlcroissant.validate is not available
    def mlcroissant_validate(path):
        raise NotImplementedError("mlcroissant.validate not available")


def _get_schemas_path() -> Path:
    """Get the path to the schemas directory using importlib.resources."""
    # Navigate from package to project root, then to schemas
    package_path = resources.files('noid')
    return package_path.parent.parent / "schemas"


def validate_with_shacl(
    data_file: Union[str, Path], 
    shapes_file: Union[str, Path],
    data_format: str = "json-ld"
) -> List[str]:
    """
    Validate data against SHACL shapes.
    
    Args:
        data_file: Path to data file to validate
        shapes_file: Path to SHACL shapes file
        data_format: Format of data file (json-ld, turtle, etc.)
        
    Returns:
        List of validation error messages (empty if valid)
    """
    try:
        # Load data graph
        data_graph = Graph()
        data_graph.parse(str(data_file), format=data_format)
        
        # Load SHACL shapes
        shapes_graph = Graph()
        shapes_graph.parse(str(shapes_file), format="turtle")
        
        # Validate with SHACL
        conforms, results_graph, results_text = validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',  # Enable RDFS inference
            debug=False
        )
        
        if conforms:
            return []
        else:
            # Parse SHACL validation results
            return _parse_shacl_results(results_graph)
            
    except Exception as e:
        return [f"Validation error: {str(e)}"]


def _parse_shacl_results(results_graph: Graph) -> List[str]:
    """Parse SHACL validation results into human-readable messages."""
    from rdflib.namespace import SH, RDF
    
    errors = []
    
    # Query for validation results directly
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        # Get focus node, property, and message
        focus_node = None
        result_path = None
        message = None
        
        for prop, obj in results_graph.predicate_objects(subject=result):
            if prop == SH.focusNode:
                focus_node = str(obj)
            elif prop == SH.resultPath:
                result_path = str(obj)
            elif prop == SH.resultMessage:
                message = str(obj)
        
        # Format error message
        error_parts = []
        if focus_node:
            # Clean up the focus node URI
            if "file://" in focus_node:
                focus_node = focus_node.split("/")[-1]
            error_parts.append(f"Node: {focus_node}")
        if result_path:
            # Clean up the property path URI  
            if "/" in str(result_path):
                result_path = str(result_path).split("/")[-1]
            error_parts.append(f"Property: {result_path}")
        if message:
            error_parts.append(f"Error: {message}")
        else:
            error_parts.append("Validation failed")
            
        errors.append(" | ".join(error_parts))
    
    return errors


def validate_transforms(data_file: Union[str, Path]) -> List[str]:
    """
    Validate transform data against transforms SHACL shapes.
    
    Args:
        data_file: Path to transform data file (JSON-LD format)
        
    Returns:
        List of validation error messages (empty if valid)
    """
    schemas_path = _get_schemas_path()
    shapes_file = schemas_path / "transforms" / "shapes.ttl"
    
    if not shapes_file.exists():
        return [f"SHACL shapes file not found: {shapes_file}"]
    
    return validate_with_shacl(data_file, shapes_file)


def validate_coordinate_spaces(data_file: Union[str, Path]) -> List[str]:
    """
    Validate coordinate space data against coordinate spaces SHACL shapes.
    
    Args:
        data_file: Path to coordinate space data file (JSON-LD format)
        
    Returns:
        List of validation error messages (empty if valid)
    """
    schemas_path = _get_schemas_path()
    shapes_file = schemas_path / "coordinate_spaces_shapes.ttl"
    
    if not shapes_file.exists():
        return [f"SHACL shapes file not found: {shapes_file}"]
    
    return validate_with_shacl(data_file, shapes_file)


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


def validate_all_examples() -> Dict[str, List[str]]:
    """
    Validate all example files using appropriate validation methods.
    
    Returns:
        Dictionary mapping file paths to validation errors
    """
    schemas_path = _get_schemas_path()
    examples_path = schemas_path.parent / "examples"
    
    results = {}
    
    # Validate Croissant files
    croissant_files = [
        "transforms.json",
        "coordinate_spaces.json", 
        "coordinate_transforms.json"
    ]
    
    for filename in croissant_files:
        file_path = examples_path / filename
        if file_path.exists():
            results[str(file_path)] = validate_croissant(file_path)
    
    # Validate data table files with SHACL (if they have JSON-LD context)
    table_files = [
        "transforms_table.json",
        "coordinate_spaces_table.json",
        "coordinate_transforms_table.json"
    ]
    
    for filename in table_files:
        file_path = examples_path / filename
        if file_path.exists():
            # Check if file has JSON-LD context
            try:
                with open(file_path) as f:
                    data = json.load(f)
                if isinstance(data, dict) and "@context" in data:
                    # Has JSON-LD context, validate with SHACL
                    if "transforms" in filename:
                        results[str(file_path)] = validate_transforms(file_path)
                    elif "coordinate_spaces" in filename:
                        results[str(file_path)] = validate_coordinate_spaces(file_path)
                else:
                    results[str(file_path)] = ["File lacks JSON-LD @context - skipping SHACL validation"]
            except Exception as e:
                results[str(file_path)] = [f"Error reading file: {str(e)}"]
    
    return results