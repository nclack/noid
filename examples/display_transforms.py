#!/usr/bin/env python3
"""
Example script demonstrating recordset concept with transform examples.
Shows how croissant recordsets would work once validation issues are resolved.
"""

import json
from pathlib import Path

def simulate_recordset():
    """Simulates what mlcroissant.Dataset.records() would return"""
    # Load the transforms table that the recordset would extract from
    examples_dir = Path(__file__).parent
    table_file = examples_dir / "transforms_table.json"
    
    with open(table_file) as f:
        transforms = json.load(f)
    
    return transforms

def main():
    print("Transform Examples via RecordSet:")
    print("(Simulating mlcroissant recordset functionality)")
    print("=" * 50)
    
    # This simulates: dataset.records(record_set="transforms") 
    transforms_recordset = simulate_recordset()
    
    for i, record in enumerate(transforms_recordset):
        print(f"\n{i+1}. {record.get('label', 'Unnamed transform')}")
        print(f"   ID: {record.get('id', 'N/A')}")
        
        # Display parameters based on what's present
        param_keys = ['translation', 'scale', 'matrix', 'mapAxis', 'sequence', 
                     'displacements', 'coordinates']
        
        for key in param_keys:
            if key in record and record[key] is not None:
                value = record[key]
                if isinstance(value, (list, dict)):
                    print(f"   {key}: {json.dumps(value, separators=(',', ':'))}")
                else:
                    print(f"   {key}: {value}")
                break  # Only show the main parameter for each transform
                
        # If no parameters found, it's probably identity
        else:
            print("   (identity transform - no parameters)")
    
    print(f"\nTotal transforms: {len(transforms_recordset)}")
    print("\nNote: This demonstrates the recordset concept.")
    print("The croissant file defines how to extract records from transforms_table.json")

if __name__ == "__main__":
    main()