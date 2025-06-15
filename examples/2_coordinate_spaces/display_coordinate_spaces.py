#!/usr/bin/env python3
"""
Example script demonstrating coordinate spaces recordset concept.
Shows how coordinate spaces with dimensions would be accessed via croissant.
"""

import json
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich import print as rprint

console = Console()

def simulate_recordset():
    """Simulates what mlcroissant.Dataset.records() would return for coordinate spaces"""
    examples_dir = Path(__file__).parent
    table_file = examples_dir / "coordinate_spaces_table.json"
    
    with open(table_file) as f:
        spaces = json.load(f)
    
    return spaces

def get_type_color(dim_type):
    """Get color for dimension type"""
    colors = {
        'space': 'blue',
        'time': 'green', 
        'other': 'yellow'
    }
    return colors.get(dim_type, 'white')

def get_unit_color(unit):
    """Get color for unit type"""
    if unit in ['index', 'arbitrary']:
        return 'dim'
    else:
        return 'cyan'  # Physical units

def format_dimensions(dimensions):
    """Format dimensions array for colorized display"""
    dim_texts = []
    for dim in dimensions:
        # Dimension name in bold
        dim_text = Text(dim['name'], style="bold")
        
        # Type in parentheses with color
        dim_text.append("(", style="dim")
        dim_text.append(dim['type'], style=get_type_color(dim['type']))
        dim_text.append(")", style="dim")
        
        # Unit in brackets with color
        if dim.get('unit'):
            dim_text.append("[", style="dim")
            dim_text.append(dim['unit'], style=get_unit_color(dim['unit']))
            dim_text.append("]", style="dim")
        
        dim_texts.append(dim_text)
    
    # Join with colored commas
    result = Text()
    for i, dim_text in enumerate(dim_texts):
        if i > 0:
            result.append(", ", style="dim")
        result.append(dim_text)
    
    return result

def main():
    console.print("Coordinate Space Examples via RecordSet:", style="bold magenta")
    console.print("(Simulating mlcroissant recordset functionality)", style="italic")
    console.print("=" * 60, style="dim")
    
    # This simulates: dataset.records(record_set="coordinate_spaces")
    spaces_recordset = simulate_recordset()
    
    for i, record in enumerate(spaces_recordset):
        console.print()
        
        # Space number and name
        name_text = Text(f"{i+1}. ")
        name_text.append(record.get('name', 'Unnamed space'), style="bold bright_white")
        console.print(name_text)
        
        # ID
        id_text = Text("   ID: ", style="white")
        id_text.append(record.get('id', 'N/A'), style="white")
        console.print(id_text)
        
        # Description  
        desc_text = Text("   Description: ", style="white")
        desc_text.append(record.get('description', 'No description'), style="white")
        console.print(desc_text)
        
        dimensions = record.get('dimensions', [])
        if dimensions:
            # Dimensions
            dim_text = Text("   Dimensions: ", style="white")
            dim_text.append(format_dimensions(dimensions))
            console.print(dim_text)
            
            # Dimensionality
            console.print(f"   [white]Dimensionality:[/white] [bright_magenta]{len(dimensions)}D[/bright_magenta]")
            
            # Analyze dimension types
            types = [d['type'] for d in dimensions]
            type_counts = {t: types.count(t) for t in set(types)}
            
            type_text = Text("   Types: ", style="white")
            type_parts = []
            for dim_type, count in type_counts.items():
                part = Text(f"{count} ", style="white")
                part.append(dim_type, style=get_type_color(dim_type))
                type_parts.append(part)
            
            for i, part in enumerate(type_parts):
                if i > 0:
                    type_text.append(", ", style="dim")
                type_text.append(part)
            console.print(type_text)
            
            # Check for physical units
            units = [d.get('unit', 'none') for d in dimensions]
            physical_units = [u for u in units if u not in ['index', 'arbitrary', 'none']]
            if physical_units:
                unit_text = Text("   Physical units: ", style="white")
                unit_list = Text(', '.join(set(physical_units)), style="cyan")
                unit_text.append(unit_list)
                console.print(unit_text)
        else:
            console.print("   [red]No dimensions defined[/red]")
    
    console.print()
    console.print(f"[bold]Total coordinate spaces: [bright_magenta]{len(spaces_recordset)}[/bright_magenta][/bold]")
    console.print()
    console.print("[dim]Note: This demonstrates the coordinate spaces recordset concept.[/dim]")
    console.print("[dim]The croissant file defines how to extract records from coordinate_spaces_table.json[/dim]")

if __name__ == "__main__":
    main()