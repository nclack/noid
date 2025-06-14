#!/usr/bin/env python3
"""
Example script demonstrating recordset concept with transform examples.
Shows how croissant recordsets would work once validation issues are resolved.
"""

import json
from pathlib import Path
from rich.console import Console
from rich.text import Text

console = Console()

def simulate_recordset():
    """Simulates what mlcroissant.Dataset.records() would return"""
    # Load the transforms table that the recordset would extract from
    examples_dir = Path(__file__).parent
    table_file = examples_dir / "transforms_table.json"
    
    with open(table_file) as f:
        transforms = json.load(f)
    
    return transforms

def get_transform_color(param_key):
    """Get color for transform type"""
    colors = {
        'translation': 'green',
        'scale': 'blue',
        'matrix': 'magenta',
        'mapAxis': 'yellow',
        'sequence': 'cyan',
        'displacements': 'red',
        'coordinates': 'bright_blue'
    }
    return colors.get(param_key, 'white')

def format_parameter_value(value):
    """Format parameter value with appropriate styling"""
    if isinstance(value, list):
        # Handle nested arrays (like matrices)
        if value and isinstance(value[0], list):
            # Matrix format - show dimensions
            rows = len(value)
            cols = len(value[0]) if value else 0
            return Text(f"[{rows}x{cols} matrix]", style="dim italic")
        else:
            # Simple array
            json_str = json.dumps(value, separators=(',', ':'))
            return Text(json_str, style="cyan")
    elif isinstance(value, dict):
        return Text(json.dumps(value, separators=(',', ':')), style="yellow")
    else:
        return Text(str(value), style="cyan")

def main():
    console.print("Transform Examples via RecordSet:", style="bold magenta")
    console.print("(Simulating mlcroissant recordset functionality)", style="italic")
    console.print("=" * 50, style="dim")
    
    # This simulates: dataset.records(record_set="transforms") 
    transforms_recordset = simulate_recordset()
    
    for i, record in enumerate(transforms_recordset):
        console.print()
        
        # Transform number and name
        name_text = Text(f"{i+1}. ")
        name_text.append(record.get('label', 'Unnamed transform'), style="bold bright_white")
        console.print(name_text)
        
        # ID
        id_text = Text("   ID: ", style="white")
        id_text.append(record.get('id', 'N/A'), style="white")
        console.print(id_text)
        
        # Display parameters based on what's present
        param_keys = ['translation', 'scale', 'matrix', 'mapAxis', 'sequence', 
                     'displacements', 'coordinates']
        
        param_found = False
        for key in param_keys:
            if key in record and record[key] is not None:
                value = record[key]
                
                # Parameter type with color
                param_text = Text("   Transform type: ", style="white")
                param_text.append(key, style=get_transform_color(key))
                console.print(param_text)
                
                # Parameter value
                value_text = Text("   Parameters: ", style="white")
                value_text.append(format_parameter_value(value))
                console.print(value_text)
                
                param_found = True
                break  # Only show the main parameter for each transform
                
        # If no parameters found, it's probably identity
        if not param_found:
            param_text = Text("   Transform type: ", style="white")
            param_text.append("identity", style="bright_green")
            console.print(param_text)
            console.print("   [dim italic](no parameters)[/dim italic]")
    
    console.print()
    console.print(f"[bold]Total transforms: [bright_magenta]{len(transforms_recordset)}[/bright_magenta][/bold]")
    console.print()
    console.print("[dim]Note: This demonstrates the recordset concept.[/dim]")
    console.print("[dim]The croissant file defines how to extract records from transforms_table.json[/dim]")

if __name__ == "__main__":
    main()