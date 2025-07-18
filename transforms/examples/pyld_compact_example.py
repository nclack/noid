#!/usr/bin/env python3
"""
Example demonstrating PyLD's compact() function vs our custom IRI processing.

Run with: python examples/pyld_compact_example.py
"""

import json

from pyld import jsonld


def main():
    print("=== PyLD compact() vs Custom IRI Processing ===\n")

    # Example 1: Starting with expanded (full IRI) document
    print("1. Starting with expanded document (full IRIs):")
    expanded_doc = {
        "https://github.com/nclack/noid/schemas/transforms/translation": [10, 20, 30],
        "https://github.com/nclack/noid/schemas/transforms/scale": [2.0, 1.5, 0.5],
        "https://github.com/nclack/noid/schemas/transforms/samplers/interpolation": "linear",
        "other_data": "preserved",
    }
    print(json.dumps(expanded_doc, indent=2))

    # Context for compaction
    context = {
        "tr": "https://github.com/nclack/noid/schemas/transforms/",
        "samplers": "https://github.com/nclack/noid/schemas/transforms/samplers/",
    }

    print("\n2. Context for compaction:")
    print(json.dumps(context, indent=2))

    # Compact using PyLD
    print("\n3. After PyLD compact():")
    compacted = jsonld.compact(expanded_doc, context)
    print(json.dumps(compacted, indent=2))

    print("\n" + "=" * 60 + "\n")

    # Example 2: Starting with compact document, expanding it
    print("4. Starting with compact document:")
    compact_doc = {
        "@context": {
            "tr": "https://github.com/nclack/noid/schemas/transforms/",
            "samplers": "https://github.com/nclack/noid/schemas/transforms/samplers/",
        },
        "tr:translation": [10, 20, 30],
        "tr:scale": [2.0, 1.5, 0.5],
        "samplers:interpolation": "linear",
    }
    print(json.dumps(compact_doc, indent=2))

    # Expand using PyLD
    print("\n5. After PyLD expand():")
    expanded = jsonld.expand(compact_doc)
    print(json.dumps(expanded, indent=2))

    print("\n" + "=" * 60 + "\n")

    # Example 3: Show our custom functions in action
    print("6. Our custom IRI processing (granular control):")

    # Simulate what our _iri_to_short_key function does
    def demo_iri_to_short_key(iri: str, context: dict) -> str:
        """Demo version of our _iri_to_short_key function."""
        for prefix, namespace in context.items():
            if isinstance(namespace, str) and iri.startswith(namespace):
                local_name = iri[len(namespace) :]
                return f"{prefix}:{local_name}"
        # Fallback to local name
        return iri.split("/")[-1] if "/" in iri else iri

    test_iris = [
        "https://github.com/nclack/noid/schemas/transforms/translation",
        "https://github.com/nclack/noid/schemas/transforms/samplers/interpolation",
        "https://example.com/unknown/property",
    ]

    for iri in test_iris:
        short_key = demo_iri_to_short_key(iri, context)
        print(f"  {iri}")
        print(f"  → {short_key}")
        print()


if __name__ == "__main__":
    main()
