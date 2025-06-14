#!/usr/bin/env python3
"""
Example script demonstrating coordinate transforms recordset concept.
Shows how coordinate spaces and transforms work together.
"""

import json
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.table import Table

console = Console()

def simulate_recordset():
    """Simulates what mlcroissant.Dataset.records() would return for coordinate transforms"""
    examples_dir = Path(__file__).parent
    table_file = examples_dir / "coordinate_transforms_table.json"
    
    with open(table_file) as f:
        transforms = json.load(f)
    
    return transforms

def get_type_color(dim_type):
    """Get color for dimension type"""
    colors = {
        'space': 'blue',
        'time': 'green', 
        'other': 'yellow'
    }
    return colors.get(dim_type, 'white')

def get_transform_color(transform_type):
    """Get color for transform type"""
    colors = {
        'translation': 'green',
        'scale': 'blue',
        'homogeneous': 'magenta',
        'rotation': 'cyan',
        'sequence': 'bright_magenta',
        'coordinates': 'bright_blue',
        'mapAxis': 'yellow'
    }
    return colors.get(transform_type, 'white')

def format_dimensions(dimensions):
    """Format dimensions array for display"""
    dim_texts = []
    for dim in dimensions:
        dim_text = Text(dim['name'], style="bold")
        dim_text.append("(", style="dim")
        dim_text.append(dim['type'], style=get_type_color(dim['type']))
        dim_text.append(")", style="dim")
        if dim.get('unit'):
            dim_text.append("[", style="dim")
            dim_text.append(dim['unit'], style="cyan" if dim['unit'] not in ['index', 'arbitrary'] else "dim")
            dim_text.append("]", style="dim")
        dim_texts.append(dim_text)
    
    result = Text()
    for i, dim_text in enumerate(dim_texts):
        if i > 0:
            result.append(", ", style="dim")
        result.append(dim_text)
    return result

def format_transform(transform):
    """Format transform for display"""
    transform_type = transform.get('type', 'unknown')
    
    result = Text(transform_type, style=get_transform_color(transform_type))
    
    # Add brief parameter summary
    if transform_type == 'translation' and 'translation' in transform:
        result.append(f" {transform['translation']}", style="dim")
    elif transform_type == 'sequence' and 'sequence' in transform:
        seq = transform['sequence']
        if isinstance(seq[0], dict):
            types = [t.get('type', 'unknown') for t in seq]
            result.append(f" [{' → '.join(types)}]", style="dim")
        else:
            result.append(f" {seq}", style="dim")
    elif transform_type == 'homogeneous' and 'matrix' in transform:
        matrix = transform['matrix']
        if isinstance(matrix, list) and isinstance(matrix[0], list):
            rows, cols = len(matrix), len(matrix[0])
            result.append(f" [{rows}x{cols}]", style="dim")
    elif transform_type == 'mapAxis' and 'mapAxis' in transform:
        result.append(" [channel mapping]", style="dim")
    elif transform_type == 'coordinates' and 'coordinates' in transform:
        coords = transform['coordinates']
        if isinstance(coords, dict) and 'conversion' in coords:
            result.append(f" [{coords['conversion']}]", style="dim")
    
    return result

def main():
    console.print("Coordinate Transform Examples via RecordSet:", style="bold magenta")
    console.print("(Demonstrating input/output space relationships)", style="italic")
    console.print("=" * 70, style="dim")
    
    # This simulates: dataset.records(record_set="coordinate_transforms")
    transforms_recordset = simulate_recordset()
    
    for i, record in enumerate(transforms_recordset):
        console.print()
        
        # Transform number and name
        name_text = Text(f"{i+1}. ")
        name_text.append(record.get('name', 'Unnamed transform'), style="bold bright_white")
        console.print(name_text)
        
        # ID
        id_text = Text("   ID: ", style="white")
        id_text.append(record.get('id', 'N/A'), style="white")
        console.print(id_text)
        
        # Description
        desc_text = Text("   Description: ", style="white")
        desc_text.append(record.get('description', 'No description'), style="white")
        console.print(desc_text)
        
        # Input space
        input_space = record.get('input_space', {})
        if input_space:
            input_text = Text("   Input: ", style="white")
            input_text.append(input_space.get('name', 'Unknown'), style="bright_cyan")
            console.print(input_text)
            
            dimensions = input_space.get('dimensions', [])
            if dimensions:
                dim_text = Text("          ", style="dim")
                dim_text.append(format_dimensions(dimensions))
                console.print(dim_text)
        
        # Transform
        transform = record.get('transform', {})
        if transform:
            transform_text = Text("   Transform: ", style="white")
            transform_text.append(format_transform(transform))
            console.print(transform_text)
        
        # Output space  
        output_space = record.get('output_space', {})
        if output_space:
            output_text = Text("   Output: ", style="white")
            output_text.append(output_space.get('name', 'Unknown'), style="bright_green")
            console.print(output_text)
            
            dimensions = output_space.get('dimensions', [])
            if dimensions:
                dim_text = Text("           ", style="dim")
                dim_text.append(format_dimensions(dimensions))
                console.print(dim_text)
        
        # Show dimensionality change
        input_dims = len(input_space.get('dimensions', []))
        output_dims = len(output_space.get('dimensions', []))
        if input_dims and output_dims:
            if input_dims == output_dims:
                dim_change = Text(f"   Dimensionality: {input_dims}D → {output_dims}D", style="dim")
            else:
                dim_change = Text(f"   Dimensionality: ", style="white")
                dim_change.append(f"{input_dims}D → {output_dims}D", style="yellow")
            console.print(dim_change)
    
    console.print()
    console.print(f"[bold]Total coordinate transforms: [bright_magenta]{len(transforms_recordset)}[/bright_magenta][/bold]")
    console.print()
    console.print("[dim]Note: This demonstrates the (input space, output space, transform) triple pattern.[/dim]")
    console.print("[dim]The croissant file defines how to extract records from coordinate_transforms_table.json[/dim]")

if __name__ == "__main__":
    main()