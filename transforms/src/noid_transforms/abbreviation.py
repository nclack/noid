"""
Namespace abbreviation system for clean JSON-LD serialization.

This module provides collision-aware namespace abbreviation with per-call optimization.
Each serialization operation gets the cleanest possible abbreviations for its specific
set of namespaces, enabling reuse of clean abbreviations across different calls.
"""

from collections.abc import Callable
import hashlib
from urllib.parse import urlparse


class NamespaceAbbreviator:
    """Smart namespace abbreviation with collision detection and per-call optimization."""

    def __init__(self):
        self._namespace_to_abbrev: dict[str, str] = {}
        self._abbrev_to_namespace: dict[str, str] = {}

    def get_abbreviation(self, namespace_iri: str) -> str:
        """Get or create abbreviation for namespace.

        Args:
            namespace_iri: Full namespace IRI

        Returns:
            Clean abbreviation for the namespace
        """
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

    def get_all_abbreviations(self) -> dict[str, str]:
        """Get all abbreviation mappings.

        Returns:
            Dictionary mapping abbreviations to namespace IRIs
        """
        return self._abbrev_to_namespace.copy()

    def _generate_candidates(self, namespace_iri: str) -> list[str]:
        """Generate candidate abbreviations in order of preference.

        Args:
            namespace_iri: Namespace IRI to abbreviate

        Returns:
            List of candidate abbreviations, most preferred first
        """
        parsed = urlparse(namespace_iri)
        path_parts = [p for p in parsed.path.split("/") if p]

        candidates = []

        # Strategy 1: Use last path component
        if path_parts:
            last_part = path_parts[-1]
            # Try different lengths: "schemas" → "sche", "sc"
            for length in [4, 2, 3, 1]:
                if len(last_part) >= length:
                    candidates.append(last_part[:length])

        # Strategy 2: Use domain-based abbreviations
        domain_parts = parsed.netloc.split(".")
        if domain_parts:
            domain = domain_parts[0]  # "github" from "github.com"
            for length in [4, 2, 3]:
                if len(domain) >= length:
                    candidates.append(domain[:length])

        # Strategy 3: Combined domain + path
        if path_parts and domain_parts:
            domain = domain_parts[0]
            path = path_parts[-1]
            # "github" + "schemas" → "gi-sc", "gh-sc"
            for d_len, p_len in [(2, 2), (2, 4), (4, 2)]:
                if len(domain) >= d_len and len(path) >= p_len:
                    candidates.append(f"{domain[:d_len]}-{path[:p_len]}")

        # Strategy 4: Initials from path parts
        if len(path_parts) > 1:
            initials = "".join(p[0] for p in path_parts if p)
            if len(initials) > 1:
                candidates.append(initials)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def _hash_fallback(self, namespace_iri: str) -> str:
        """Fallback to meaningful+hash abbreviation.

        Args:
            namespace_iri: Namespace IRI that couldn't be abbreviated cleanly

        Returns:
            Meaningful abbreviation with hash suffix
        """
        parsed = urlparse(namespace_iri)
        path_parts = [p for p in parsed.path.split("/") if p]

        # Get meaningful prefix
        if path_parts:
            meaningful_part = path_parts[-1][:3]  # "schemas" → "sch"
        else:
            domain = parsed.netloc.split(".")[0]
            meaningful_part = domain[:3]  # "github" → "git"

        # Add hash suffix for uniqueness
        hash_digest = hashlib.md5(namespace_iri.encode()).hexdigest()
        hash_suffix = hash_digest[:4]  # Keep it short

        candidate = f"{meaningful_part}-{hash_suffix}"

        # If even this collides (extremely unlikely), use full namespace as fallback
        if candidate in self._abbrev_to_namespace:
            return namespace_iri  # Full namespace fallback

        self._namespace_to_abbrev[namespace_iri] = candidate
        self._abbrev_to_namespace[candidate] = namespace_iri
        return candidate


def create_abbreviator_for_namespaces(namespaces: set[str]) -> NamespaceAbbreviator:
    """Create abbreviator optimized for a specific set of namespaces.

    This function creates a fresh abbreviator and pre-populates it with optimal
    abbreviations for the given set of namespaces, resolving any collisions
    within the set.

    Args:
        namespaces: Set of namespace IRIs that will be used together

    Returns:
        NamespaceAbbreviator optimized for these specific namespaces

    Examples:
        >>> # Clean case - no collisions
        >>> namespaces = {
        ...     "https://github.com/nclack/noid/schemas/",
        ...     "https://github.com/nclack/noid/schemas/subschema/"
        ... }
        >>> abbrev = create_abbreviator_for_namespaces(namespaces)
        >>> abbrev.get_abbreviation(namespaces[0])  # → "sche"
        >>> abbrev.get_abbreviation(namespaces[1])  # → "sub"

        >>> # Different call with different namespaces - can reuse same abbreviations
        >>> other_namespaces = {
        ...     "https://example.org/",
        ...     "https://geospatial.org/schemas/"
        ... }
        >>> other_abbrev = create_abbreviator_for_namespaces(other_namespaces)
        >>> # Can use "sche" and "sub" again since it's a fresh abbreviator
    """
    abbreviator = NamespaceAbbreviator()

    # Pre-populate with all namespaces to resolve collisions optimally
    for namespace in sorted(namespaces):  # Sort for deterministic ordering
        abbreviator.get_abbreviation(namespace)

    return abbreviator


def extract_namespaces_from_objects(
    objects_dict: dict[str, any],
    iri_extractor: Callable[[any], str | None] | None = None,
) -> set[str]:
    """Extract all unique namespaces from a dictionary of objects.

    Args:
        objects_dict: Dictionary with registered objects (may include @context)
        iri_extractor: Optional function to extract IRI from object. If None,
                      will try to import and use the registry module.

    Returns:
        Set of namespace IRIs found in the objects
    """
    namespaces = set()

    for key, obj in objects_dict.items():
        if key == "@context":
            continue

        # Get IRI from provided extractor or registry
        iri = None
        if iri_extractor:
            iri = iri_extractor(obj)
        else:
            # Try to use registry if available
            try:
                from .registry import registry

                iri = registry.get_iri_for_object(obj)
            except ImportError:
                # Registry not available, skip this object
                continue

        if iri:
            namespace = _extract_namespace_from_iri(iri)
            if namespace:
                namespaces.add(namespace)

    return namespaces


def _extract_namespace_from_iri(iri: str) -> str:
    """Extract namespace from full IRI.

    Args:
        iri: Full IRI (e.g., "https://example.com/schemas/translation")

    Returns:
        Namespace IRI (e.g., "https://example.com/schemas/")
    """
    # Find the last occurrence of / or # to separate namespace from local name
    for delimiter in ["/", "#"]:
        if delimiter in iri:
            idx = iri.rfind(delimiter)
            return iri[: idx + 1]  # Include the delimiter

    # No delimiter found - the whole thing is the namespace
    return iri + "/"  # Add trailing slash
