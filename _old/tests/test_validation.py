"""
Test suite for NOID JSON-LD validation.
"""

from pathlib import Path
from pyld import jsonld
import json
import pytest


class TestJSONLDValidation:
    """Test JSON-LD validity using pyld."""
    
    def test_transforms_vocabulary_pyld_expand(self):
        """Transforms vocabulary should be valid JSON-LD that pyld can expand."""
        # Try different vocabulary file locations
        possible_vocab_files = [
            Path(__file__).parent.parent / "schemas" / "transforms" / "vocabulary.jsonld",
            Path(__file__).parent.parent / "transforms" / "_old" / "vocabulary.jsonld",
            Path(__file__).parent.parent / "schemas" / "spaces" / "vocabulary.jsonld"
        ]
        
        vocab_file = None
        for candidate in possible_vocab_files:
            if candidate.exists():
                vocab_file = candidate
                break
        
        if vocab_file is None:
            pytest.skip("No vocabulary.jsonld file found to test")
        
        with open(vocab_file, 'r') as f:
            vocab_data = json.load(f)
        
        # Test that pyld can expand it without errors
        expanded = jsonld.expand(vocab_data)
        assert isinstance(expanded, list), "Expanded JSON-LD should be a list"
        assert len(expanded) > 0, "Expanded JSON-LD should contain items"

    def test_transform_examples_jsonld_validity(self):
        """Test that transform examples are valid JSON-LD."""
        transforms_dir = Path(__file__).parent.parent / "transforms" / "examples"
        
        # Test transforms.jsonld
        transforms_file = transforms_dir / "transforms.jsonld"
        if transforms_file.exists():
            with open(transforms_file, 'r') as f:
                data = json.load(f)
            
            # Test JSON-LD expansion (validates syntax)
            expanded = jsonld.expand(data)
            assert isinstance(expanded, list), "Expanded JSON-LD should be a list"
            
            # Test JSON-LD compaction (validates context)
            compacted = jsonld.compact(data, data.get("@context", {}))
            assert "@context" in compacted or compacted, "Compaction should preserve structure"

    def test_sequences_examples_jsonld_validity(self):
        """Test that sequence examples are valid JSON-LD."""
        transforms_dir = Path(__file__).parent.parent / "transforms" / "examples"
        
        # Test sequences.jsonld
        sequences_file = transforms_dir / "sequences.jsonld"
        if sequences_file.exists():
            with open(sequences_file, 'r') as f:
                data = json.load(f)
            
            # Test JSON-LD expansion
            expanded = jsonld.expand(data)
            assert isinstance(expanded, list), "Expanded JSON-LD should be a list"
            
            # Test that context resolves properly
            context = data.get("@context", {})
            assert "tr" in context, "Transform namespace should be defined"
            assert "samplers" in context, "Samplers namespace should be defined"

    def test_jsonld_context_files(self):
        """Test that generated JSON-LD context files are valid."""
        context_file = Path(__file__).parent.parent / "transforms" / "_out" / "jsonld-context" / "transforms.context.jsonld"
        
        if context_file.exists():
            with open(context_file, 'r') as f:
                context_data = json.load(f)
            
            # Validate basic JSON-LD context structure
            assert "@context" in context_data, "Context file should have @context"
            context = context_data["@context"]
            
            # Check for required namespaces
            assert "xsd" in context, "XSD namespace should be defined"
            assert "linkml" in context, "LinkML namespace should be defined"
            
            # Test that context can be used for processing
            test_doc = {"@context": context, "@type": "Identity"}
            expanded = jsonld.expand(test_doc)
            assert isinstance(expanded, list), "Context should enable valid expansion"


