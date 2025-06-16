"""
Test suite for NOID JSON-LD validation.
"""

from pathlib import Path
from pyld import jsonld
import json


class TestJSONLDValidation:
    """Test JSON-LD validity using pyld."""
    
    def test_transforms_vocabulary_pyld_expand(self):
        """Transforms vocabulary should be valid JSON-LD that pyld can expand."""
        vocab_file = Path(__file__).parent.parent / "schemas" / "transforms" / "vocabulary.jsonld"
        
        with open(vocab_file, 'r') as f:
            vocab_data = json.load(f)
        
        # Test that pyld can expand it without errors
        expanded = jsonld.expand(vocab_data)
        assert isinstance(expanded, list), "Expanded JSON-LD should be a list"
        assert len(expanded) > 0, "Expanded JSON-LD should contain items"


