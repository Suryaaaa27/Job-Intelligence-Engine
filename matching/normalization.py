"""
Text normalization utilities for resume and job matching.

This module provides a single source of truth for converting text into a
canonical form before any deterministic comparison.
"""

from __future__ import annotations

import re


def normalize(text: str | None) -> str:
    """
    Normalize text for deterministic matching.

    Examples:
        Python              -> python
        Machine-Learning    -> machine learning
        REST APIs           -> rest apis
        C++                 -> c++
        Node.js             -> node.js
    """

    if not text:
        return ""

    text = text.lower().strip()

    # Replace separators with spaces
    text = re.sub(r"[-_/]+", " ", text)

    # Remove unwanted punctuation while preserving
    # characters common in technical skills.
    text = re.sub(r"[^a-z0-9+#.\s]", "", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


def normalize_collection(items: list[str] | None) -> set[str]:
    """
    Normalize a list of strings.

    Returns a set for fast membership lookup.
    """

    if not items:
        return set()

    normalized = set()

    for item in items:
        value = normalize(item)
        if value:
            normalized.add(value)

    return normalized