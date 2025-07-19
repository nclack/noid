# Dispatch Registry Design

## Goal

Replace manual if/elif chains with maintainable registries that support multi-schema namespaces and PyLD integration.

## Public API

```python
# Single transform from dictionary
result = transforms.from_data({"translation": [10, 20, 5]})
# -> Translation(translation=[10, 20, 5])

# Multi-schema JSON-LD processing
jsonld_data = {
    "@context": {
        "tr": "https://github.com/nclack/noid/schemas/transforms/",
        "samplers": "https://github.com/nclack/noid/schemas/transforms/samplers/"
    },
    "tr:translation": [10, 20, 30],
    "samplers:interpolation": "nearest"
}

# JSON-LD to Python objects (preserves structure and context)
result = transforms.from_jsonld(jsonld_data)
# -> {
#     "@context": {...},
#     "tr:translation": Translation(translation=[10, 20, 30]),
#     "samplers:interpolation": InterpolationConfig("nearest")
# }

# Python objects back to JSON-LD (roundtrip support)
jsonld_output = transforms.to_jsonld(result)
# -> Original jsonld_data structure with serialized transform objects

# Error handling with smart suggestions
try:
    transforms.from_data({"translaton": [1, 2, 3]})  # typo
except ValueError as e:
    print(e)  # "Unknown transform type: 'translaton'. Did you mean 'translation'?"

try:
    transforms.from_data({"unknown": [1, 2, 3]})
except ValueError as e:
    print(e)  # "Unknown transform type: 'unknown'. Available: [translation, scale, mapAxis, ...]"
```

## Simple Module-Level Registration

```python
# transforms/factory.py - Main transforms module
from .registry import registry, set_namespace

# Set namespace once at module level
set_namespace("https://github.com/nclack/noid/schemas/transforms/", prefix="tr")

# Simple registration - IRI and short names auto-generated
@register
def translation(data: List[float]) -> Translation:
    """Create translation from list data."""
    return Translation(translation=data)

@register
def scale(data: List[float]) -> Scale:
    """Create scale from list data."""
    return Scale(scale=data)

@register
def identity() -> Identity:
    """Create identity transform."""
    return Identity()

# Custom name override when needed
@register("mapAxis")  # Function name is map_axis, but schema uses mapAxis
def map_axis(data: List[int]) -> MapAxis:
    """Create map axis from list data."""
    return MapAxis(mapAxis=data)
```

```python
# samplers/factory.py - Samplers module
from ..registry import registry, set_namespace

# Different namespace for samplers
set_namespace("https://github.com/nclack/noid/schemas/transforms/samplers/", prefix="samplers")

@register
def interpolation(data: str) -> InterpolationConfig:
    """Create interpolation config from string."""
    return InterpolationConfig(method=data)

@register
def extrapolation(data: str) -> ExtrapolationConfig:
    """Create extrapolation config from string."""
    return ExtrapolationConfig(method=data)
```

### Auto-Generated IRIs and Short Names

```python
# Function name + namespace → full IRI + short name
# translation() → "https://github.com/nclack/noid/schemas/transforms/translation" + "tr:translation"
# interpolation() → "https://github.com/nclack/noid/schemas/transforms/samplers/interpolation" + "samplers:interpolation"
```

## Internal Registry Implementation

```python
from typing import Dict, Callable, Any, Optional
import threading
from functools import wraps

# Thread-local storage for current namespace context
_context = threading.local()

def set_namespace(namespace_iri: str, prefix: str = None) -> None:
    """Set namespace for subsequent registrations in this module."""
    _context.namespace_iri = namespace_iri
    _context.prefix = prefix or _auto_generate_prefix(namespace_iri)

def _auto_generate_prefix(namespace_iri: str) -> str:
    """Auto-generate reasonable prefix from namespace IRI."""
    from urllib.parse import urlparse

    parsed = urlparse(namespace_iri)
    path_parts = [p for p in parsed.path.split('/') if p]

    if path_parts:
        # Use last meaningful path component
        last_part = path_parts[-1]
        return last_part[:4]  # "transforms" → "tran", "samplers" → "samp"

    # Fallback to domain
    domain = parsed.netloc.split('.')[0]
    return domain[:4]

class TransformRegistry:
    """Registry with module-level namespace support."""

    def __init__(self):
        self._factories = {}        # full_iri → factory_func
        self._type_to_short = {}    # Transform class → short_name
        self._short_to_iri = {}     # short_name → full_iri
        self._adapter = PyLDDataAdapter()

    def register(self, name_override: str = None):
        """Decorator for registering factory functions with current namespace."""
        def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
            # Get current namespace from thread-local context
            namespace_iri = getattr(_context, 'namespace_iri', None)
            prefix = getattr(_context, 'prefix', None)

            if not namespace_iri:
                raise RuntimeError("No namespace set. Call set_namespace() first.")

            # Use override name or derive from function name
            local_name = name_override or func.__name__

            # Build full IRI and short name
            full_iri = f"{namespace_iri.rstrip('/')}/{local_name}"
            short_name = f"{prefix}:{local_name}" if prefix else local_name

            # Register the factory
            self._factories[full_iri] = func

            # Register type mapping for serialization (introspect return type)
            return_type = self._get_return_type(func)
            if return_type:
                self._type_to_short[return_type] = short_name
                self._short_to_iri[short_name] = full_iri

            return func

        # Support both @register and @register("name")
        if callable(name_override):
            # @register (no parentheses)
            func = name_override
            name_override = None
            return decorator(func)
        else:
            # @register("name") or @register()
            return decorator

    def _get_return_type(self, func: Callable) -> Optional[type]:
        """Extract return type from function annotation."""
        import inspect
        sig = inspect.signature(func)
        return_annotation = sig.return_annotation

        if return_annotation != inspect.Signature.empty:
            # Handle typing generics like List[float] → just return the base type
            origin = getattr(return_annotation, '__origin__', None)
            if origin is None:
                return return_annotation

        return None

# Global registry instance
registry = TransformRegistry()

# Export the register decorator
register = registry.register
```

## Benefits of Module-Level Approach

### **1. Minimal Boilerplate**
```python
# OLD: Verbose per-function configuration
@registry.register(
    iri="https://github.com/nclack/noid/transforms/translation",
    short_name="tr:translation"
)
def translation(data: List[float]) -> Translation:
    return Translation(translation=data)

# NEW: Set once, use everywhere
set_namespace("https://github.com/nclack/noid/schemas/transforms/", prefix="tr")

@register
def translation(data: List[float]) -> Translation:
    return Translation(translation=data)
```

### **2. DRY Principle**
- Namespace declared once per module
- IRI construction automated
- Short name generation automated
- Consistent naming across module

### **3. Override When Needed**
```python
# Most functions use auto-naming
@register
def translation(data: List[float]) -> Translation: ...

# Override for schema mismatches
@register("mapAxis")  # Schema uses camelCase, Python uses snake_case
def map_axis(data: List[int]) -> MapAxis: ...
```

### **4. Module Organization**
```python
# transforms/factory.py
set_namespace("https://github.com/nclack/noid/schemas/transforms/", prefix="tr")
# All @register calls in this module use the transforms namespace

# samplers/factory.py
set_namespace("https://github.com/nclack/noid/schemas/transforms/samplers/", prefix="samplers")
# All @register calls in this module use the samplers namespace
```

### **5. Type-Safe Return Types**
The registry automatically introspects function return types for bidirectional mapping:

```python
@register
def translation(data: List[float]) -> Translation:  # Return type extracted automatically
    return Translation(translation=data)

# Later...
transform_obj = Translation([1, 2, 3])
short_name = registry.get_short_name(transform_obj)  # → "tr:translation"
```

## Proposed Adapter Pattern

### **PyLD Data Adapter**
```python
class PyLDDataAdapter:
    """Normalize PyLD expanded data before passing to factory functions.

    PyLD expansion wraps all values in @value objects and arrays:
    - [10, 20, 30] → [{"@value": 10}, {"@value": 20}, {"@value": 30}]
    - "linear" → [{"@value": "linear"}]
    """

    def normalize(self, data: Any) -> Any:
        """Convert PyLD expansion output to clean factory input."""

        # PyLD always returns arrays, even for scalars
        if isinstance(data, list):
            # Handle array of @value objects: [{"@value": 10}, {"@value": 20}] → [10, 20]
            if all(isinstance(item, dict) and "@value" in item for item in data):
                normalized_items = [self._extract_value(item) for item in data]

                # If single item, unwrap from array (scalar case)
                if len(normalized_items) == 1:
                    return normalized_items[0]
                return normalized_items

            # Handle mixed or complex arrays
            return [self.normalize(item) for item in data]

        # Handle single @value object (shouldn't happen with PyLD but defensive)
        if isinstance(data, dict) and "@value" in data:
            return self._extract_value(data)

        # Pass through other values
        return data

    def _extract_value(self, item: Dict[str, Any]) -> Any:
        """Extract value from @value wrapper, handling type conversion."""
        value = item["@value"]

        # Handle typed values with conversion
        if "@type" in item:
            type_iri = item["@type"]
            return self._convert_typed_value(value, type_iri)

        return value

    def _convert_typed_value(self, value: Any, type_iri: str) -> Any:
        """Convert typed literals to appropriate Python types."""
        if type_iri == "http://www.w3.org/2001/XMLSchema#float":
            return float(value)
        elif type_iri == "http://www.w3.org/2001/XMLSchema#integer":
            return int(value)
        elif type_iri == "http://www.w3.org/2001/XMLSchema#boolean":
            return str(value).lower() in ("true", "1")
        return value  # Default passthrough
```

### **Factory Registration with Short Names**
```python
# Register with both full IRI and preferred short name for serialization
@registry.register(
    iri="https://github.com/nclack/noid/transforms/translation",
    short_name="tr:translation"
)
def translation_factory(data: List[float]) -> Translation:
    """Create translation from clean list data."""
    return Translation(translation=data)

@registry.register(
    iri="https://github.com/nclack/noid/transforms/scale",
    short_name="tr:scale"
)
def scale_factory(data: List[float]) -> Scale:
    """Create scale from clean list data."""
    return Scale(scale=data)

@registry.register(
    iri="https://github.com/nclack/noid/transforms/samplers/interpolation",
    short_name="samplers:interpolation"
)
def interpolation_factory(data: str) -> InterpolationConfig:
    """Create interpolation config from clean string."""
    return InterpolationConfig(method=data)
```

### **Registry with Bidirectional Mapping**
```python
class TransformRegistry:
    """Registry supporting both IRI→factory and type→short_name mapping."""

    def __init__(self):
        self._factories = {}        # IRI → factory_func
        self._type_to_short = {}    # Transform class → preferred short name
        self._short_to_iri = {}     # short name → full IRI
        self._adapter = PyLDDataAdapter()

    def register(self, iri: str, factory_func: Callable[[Any], Transform],
                 short_name: str = None):
        """Register factory with optional preferred short name for serialization."""
        self._factories[iri] = factory_func

        if short_name:
            # Get the transform type from factory inspection
            transform_type = self._get_transform_type(factory_func)
            self._type_to_short[transform_type] = short_name
            self._short_to_iri[short_name] = iri

    def create(self, iri: str, raw_data: Any) -> Transform:
        """Create transform from IRI + PyLD data."""
        if iri not in self._factories:
            available = list(self._factories.keys())
            raise UnknownTransformError(iri, available)

        try:
            clean_data = self._adapter.normalize(raw_data)
            factory = self._factories[iri]
            return factory(clean_data)
        except Exception as e:
            raise FactoryValidationError(iri, raw_data, e)

    def get_short_name(self, transform: Transform) -> str:
        """Get preferred short name for serialization (e.g., 'tr:translation')."""
        transform_type = type(transform)
        return self._type_to_short.get(transform_type, self._iri_to_short_fallback(transform_type))

    def get_iri(self, short_name: str) -> str:
        """Convert short name to full IRI."""
        return self._short_to_iri.get(short_name, short_name)

    def _get_transform_type(self, factory_func):
        """Extract transform type from factory function (implementation dependent)."""
        # Could use type hints, naming conventions, or factory inspection
        pass

    def _iri_to_short_fallback(self, transform_type):
        """Fallback short name generation if not explicitly registered."""
        # Find registered IRI for this type and create reasonable short name
        pass
```

### **Updated from_jsonld Implementation**
```python
def from_jsonld(jsonld_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process JSON-LD with clean adapter-based dispatch."""

    # Step 1: Build mapping of original keys → full IRIs before expansion
    key_mapping = _build_key_to_iri_mapping(jsonld_data)

    # Step 2: PyLD expansion (handles @context → full IRIs)
    expanded = jsonld.expand(jsonld_data)

    # Step 3: Process expanded data
    result = {}

    # Preserve original context
    if "@context" in jsonld_data:
        result["@context"] = jsonld_data["@context"]

    # Process each expanded item
    for expanded_item in expanded:
        for iri, raw_value in expanded_item.items():
            if iri.startswith("@"):
                continue  # Skip JSON-LD keywords

            # Find original key that mapped to this IRI
            original_key = key_mapping.get(iri)
            if not original_key:
                # Fallback: use IRI if no mapping found
                original_key = iri

            # Try registry dispatch with adapter
            try:
                transform_obj = registry.create(iri, raw_value)
                result[original_key] = transform_obj
            except UnknownTransformError:
                # Not a registered transform - pass through
                result[original_key] = raw_value

    return result


def _build_key_to_iri_mapping(jsonld_data: Dict[str, Any]) -> Dict[str, str]:
    """Build mapping from original keys to their expanded IRIs."""
    mapping = {}

    # Extract non-context keys
    data_keys = {k for k in jsonld_data.keys() if not k.startswith("@")}

    # Create minimal document for expansion to get key mappings
    minimal_doc = {"@context": jsonld_data.get("@context", {})}
    for key in data_keys:
        minimal_doc[key] = "placeholder"  # Value doesn't matter for key mapping

    # Expand to see how keys map to IRIs
    expanded_minimal = jsonld.expand(minimal_doc)

    if expanded_minimal:
        expanded_keys = expanded_minimal[0].keys()

        # Match original keys to expanded IRIs
        # This is heuristic but should work for most cases
        for original_key in data_keys:
            for iri in expanded_keys:
                if iri.endswith(original_key.split(":")[-1]):  # Match local part
                    mapping[iri] = original_key
                    break

    return mapping
```

## Benefits of This Approach

### **1. Single Responsibility**
- **Adapter**: Handles PyLD format variations
- **Factory**: Creates objects from clean data
- **Registry**: Bidirectional mapping (IRI↔factory, type↔short_name)

### **2. Easier Testing**
```python
def test_translation_factory():
    """Test factory with clean data only."""
    result = translation_factory([10.0, 20.0, 5.0])
    assert result.translation == [10.0, 20.0, 5.0]

def test_pyld_adapter():
    """Test adapter normalization with actual PyLD output."""
    adapter = PyLDDataAdapter()

    # Test PyLD array expansion: [{"@value": 10}, {"@value": 20}] → [10, 20]
    pyld_array = [{"@value": 10}, {"@value": 20}, {"@value": 30}]
    assert adapter.normalize(pyld_array) == [10, 20, 30]

    # Test PyLD scalar expansion: [{"@value": "linear"}] → "linear"
    pyld_scalar = [{"@value": "linear"}]
    assert adapter.normalize(pyld_scalar) == "linear"

    # Test typed values: [{"@value": 10.0, "@type": "xsd:float"}] → 10.0
    pyld_typed = [{"@value": "10.0", "@type": "http://www.w3.org/2001/XMLSchema#float"}]
    assert adapter.normalize(pyld_typed) == 10.0
```

### **3. Factory Function Simplicity**
Following your preference for clean factories [[memory:3486044]], factory functions become simple, focused functions:

```python
# Clean and simple - exactly what you prefer
def translation(data: List[float]) -> Translation:
    return Translation(translation=data)

def scale(data: List[float]) -> Scale:
    return Scale(scale=data)
```

### **Clean Serialization with Per-Call Abbreviations**
```python
def to_jsonld(transform_dict: Dict[str, Transform]) -> Dict[str, Any]:
    """Serialize transforms back to clean JSON-LD using optimal abbreviations."""

    # Step 1: Collect all namespaces used in this serialization
    namespaces = set()
    for key, transform_obj in transform_dict.items():
        if key == "@context":
            continue
        # Extract namespace from transform's registered IRI
        namespace = registry.get_namespace_for_transform(transform_obj)
        if namespace:
            namespaces.add(namespace)

    # Step 2: Create abbreviator optimized for just these namespaces
    abbreviator = create_abbreviator_for_namespaces(namespaces)

    # Step 3: Build context with clean abbreviations
    context = {}
    for namespace in namespaces:
        abbrev = abbreviator.get_abbreviation(namespace)
        context[abbrev] = namespace

    # Step 4: Serialize with clean short names
    result = {"@context": context}

    for original_key, transform_obj in transform_dict.items():
        if original_key == "@context":
            continue

        # Get clean short name for this specific call
        short_name = registry.get_short_name(transform_obj, abbreviator)

        # Serialize transform to dict
        transform_data = transform_obj.to_data()

        # Use short name in output
        result[short_name] = transform_data

    return result

# Example - clean abbreviations optimized per call:
transform_dict = {
    "tr:translation": Translation([10, 20, 30]),
    "samplers:interpolation": InterpolationConfig("linear")
}

# Automatically generates optimal context and clean output:
# {
#   "@context": {
#     "tran": "https://github.com/nclack/noid/transforms/",
#     "samp": "https://github.com/nclack/noid/transforms/samplers/"
#   },
#   "tran:translation": [10, 20, 30],
#   "samp:interpolation": "linear"
# }
```

### **4. Clean Round-trip Serialization**
Bidirectional mapping ensures clean JSON-LD output:

```python
# Input: Clean short names
input_jsonld = {"tr:translation": [10, 20, 30]}

# Processing: Full IRIs internally
transforms = from_jsonld(input_jsonld)  # Uses full IRIs for registry lookup

# Output: Clean short names again
output_jsonld = to_jsonld(transforms)   # Uses short names for serialization
# -> {"tr:translation": [10, 20, 30]}   # Round-trip preserves original format
```

## Benefits of This Approach

**PyLD expansion does NOT provide clean data**. Testing shows PyLD wraps everything:

```python
# Input JSON-LD
{"tr:translation": [10, 20, 30]}

# PyLD expansion output
{
  "https://github.com/nclack/noid/transforms/translation": [
    {"@value": 10}, {"@value": 20}, {"@value": 30}
  ]
}

# Even scalars become arrays!
{"samplers:interpolation": "linear"}
→ {"https://.../interpolation": [{"@value": "linear"}]}
```

**Without the adapter**, factory functions would need complex PyLD-specific logic:

```python
# BAD: Factory handling PyLD directly
def translation_factory(pyld_data):
    if isinstance(pyld_data, list):
        values = [item["@value"] for item in pyld_data if "@value" in item]
        return Translation(translation=values)
    # ... more PyLD-specific handling
```

**With the adapter**, factories stay clean and focused:

```python
# GOOD: Clean factory with adapter handling PyLD complexity
def translation_factory(clean_data):
    return Translation(translation=clean_data)
```

This adapter pattern separates the PyLD data handling concerns from the object creation logic, making both the registry and the factory functions much simpler and more testable.

## Alternative: Auto-Generated Namespace Abbreviations

Instead of manual short name registration, auto-generate collision-resistant abbreviations:

### **Collision-Aware Namespace Abbreviator**
```python
class NamespaceAbbreviator:
    """Smart namespace abbreviation with collision detection."""

    def __init__(self):
        self._namespace_to_abbrev = {}
        self._abbrev_to_namespace = {}

    def get_abbreviation(self, namespace_iri: str) -> str:
        """Get or create abbreviation for namespace."""

        if namespace_iri in self._namespace_to_abbrev:
            return self._namespace_to_abbrev[namespace_iri]

        # Try increasingly specific abbreviations
        candidates = self._generate_candidates(namespace_iri)

        for candidate in candidates:
            if candidate not in self._abbrev_to_namespace:
                # Found available abbreviation
                self._namespace_to_abbrev[namespace_iri] = candidate
                self._abbrev_to_namespace[candidate] = namespace_iri
                return candidate

        # Fallback to hash if all candidates taken
        return self._hash_fallback(namespace_iri)

    def _generate_candidates(self, namespace_iri: str) -> List[str]:
        """Generate candidate abbreviations in order of preference."""
        from urllib.parse import urlparse

        parsed = urlparse(namespace_iri)
        path_parts = [p for p in parsed.path.split('/') if p]

        candidates = []

        # Strategy 1: Use last path component
        if path_parts:
            last_part = path_parts[-1]
            candidates.append(last_part[:4])  # "transforms" → "tran"
            candidates.append(last_part[:2])  # "transforms" → "tr"

        # Strategy 2: Use domain + path
        domain = parsed.netloc.split('.')[0]
        if path_parts:
            candidates.append(f"{domain[:2]}-{path_parts[-1][:2]}")  # "gi-tr"

        # Strategy 3: Domain-based
        candidates.append(domain[:4])

        return candidates

    def _hash_fallback(self, namespace_iri: str) -> str:
        """Fallback to meaningful+hash abbreviation."""
        import hashlib
        from urllib.parse import urlparse

        # Get meaningful prefix from the namespace
        parsed = urlparse(namespace_iri)
        path_parts = [p for p in parsed.path.split('/') if p]

        if path_parts:
            meaningful_part = path_parts[-1][:4]  # "transforms" → "tran"
        else:
            domain = parsed.netloc.split('.')[0]
            meaningful_part = domain[:4]  # "github" → "gith"

        # Add hash suffix for uniqueness
        hash_digest = hashlib.md5(namespace_iri.encode()).hexdigest()
        hash_suffix = hash_digest[:4]  # Keep it short

        candidate = f"{meaningful_part}-{hash_suffix}"

        # If even this collides (extremely unlikely), use full namespace as key
        if candidate in self._abbrev_to_namespace:
            return namespace_iri  # Full namespace fallback

        return candidate

# Per-call abbreviator (scoped to single serialization operation)
def create_abbreviator_for_namespaces(namespaces: Set[str]) -> NamespaceAbbreviator:
    """Create abbreviator for a specific set of namespaces in one to_jsonld call."""
    abbreviator = NamespaceAbbreviator()

    # Pre-populate with all namespaces to resolve collisions optimally
    for namespace in namespaces:
        abbreviator.get_abbreviation(namespace)

    return abbreviator

# Examples - each to_jsonld call gets fresh, optimal abbreviations:

# Call 1: Only transforms + samplers
namespaces_1 = {
    "https://github.com/nclack/noid/transforms/",
    "https://github.com/nclack/noid/transforms/samplers/"
}
abbrev_1 = create_abbreviator_for_namespaces(namespaces_1)
# → "tran" and "samp" (clean, no conflicts within this set)

# Call 2: Different namespaces - can reuse same abbreviations!
namespaces_2 = {
    "https://neuraltransforms.org/",
    "https://geospatial.org/transforms/"
}
abbrev_2 = create_abbreviator_for_namespaces(namespaces_2)
# → "tran" and "samp" again (no conflict since different call)
```

### **Registry with Auto-Abbreviation**
```python
class TransformRegistry:
    """Registry with per-call namespace abbreviation."""

    def __init__(self):
        self._factories = {}
        self._adapter = PyLDDataAdapter()

    def get_short_name(self, transform: Transform, abbreviator: NamespaceAbbreviator) -> str:
        """Get short name using provided abbreviator."""

        # Find the IRI for this transform type
        transform_type = type(transform)
        for iri, factory in self._factories.items():
            if self._factory_creates_type(factory, transform_type):
                namespace, local_name = self._split_iri(iri)
                abbrev = abbreviator.get_abbreviation(namespace)
                return f"{abbrev}:{local_name}"

        # Fallback
        return transform_type.__name__.lower()

    def _split_iri(self, iri: str) -> Tuple[str, str]:
        """Split IRI into namespace and local name."""
        # Find last / or # to split namespace from local name
        for delimiter in ['/', '#']:
            if delimiter in iri:
                idx = iri.rfind(delimiter)
                return iri[:idx+1], iri[idx+1:]
        return iri, ""

# Usage examples showing collision progression:
# "https://github.com/nclack/noid/transforms/translation" → "tran:translation"
# "https://github.com/nclack/noid/transforms/samplers/interpolation" → "samp:interpolation"
# "https://example.com/transforms/translation" → "tr:translation" (collision avoided)
# "https://badcase.com/transforms/translation" → "tran-e34f:translation" (meaningful + hash)
```

### **Benefits of Per-Call Auto-Abbreviation**
- **Scalable**: No manual registration needed
- **Optimal per-call**: Each `to_jsonld()` gets the cleanest possible abbreviations
- **Collision-resistant**: Multi-tier fallback strategies ensure uniqueness within call
- **Readable hash fallbacks**: `"tran-e34f"` vs cryptic `"h3a7f2"`
- **Reusable abbreviations**: Different calls can use same clean names for different namespaces
- **Bounded complexity**: Worst case is full namespace (always works)
- **Extensible**: Works with any namespace, not just known ones

### **Per-Call Optimization Examples**
```python
# Example 1: Simple case - only 2 namespaces, both get clean names
transform_set_1 = {
    "transforms_obj": Translation([10, 20, 30]),
    "samplers_obj": InterpolationConfig("linear")
}
# Creates abbreviator for: {transforms/, samplers/}
# Result: "tran:translation", "samp:interpolation" (both clean!)

# Example 2: Different call with overlapping namespace concepts
transform_set_2 = {
    "neural_obj": NeuralTransform(...),
    "geospatial_obj": ProjectionTransform(...)
}
# Creates fresh abbreviator for: {neuraltransforms.org/, geospatial.org/transforms/}
# Result: "tran:neural", "samp:projection" (can reuse same abbreviations!)

# Example 3: Bad collision case within single call
transform_set_3 = {
    "obj1": Transform_from_namespace("https://example.com/transforms/"),
    "obj2": Transform_from_namespace("https://badcase.com/transforms/"),
    "obj3": Transform_from_namespace("https://another.com/transforms/")
}
# Creates abbreviator for: all 3 transform namespaces
# Results: "tran", "tr", "tran-e34f" (optimal given the collision within this call)

# Key insight: Each call optimizes for ITS specific namespace set
# No global pollution - next call starts fresh with clean slate
```
