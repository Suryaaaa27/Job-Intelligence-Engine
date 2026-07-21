"""
Common matching utilities shared across all matching modules.
"""

from __future__ import annotations

from matching.corpus import ResumeCorpus
from matching.normalization import normalize


def contains_phrase(phrase: str, corpus: ResumeCorpus) -> bool:
    """
    Check whether a normalized phrase exists anywhere in the resume corpus.
    """

    phrase = normalize(phrase)

    if not phrase:
        return False

    if phrase in corpus.skills:
        return True

    return phrase in corpus.full_text


def match_ratio(
    phrases: list[str],
    corpus: ResumeCorpus,
) -> tuple[list[str], list[str], float]:
    """
    Match a list of phrases against a resume corpus.

    Returns:
        (
            matched_phrases,
            missing_phrases,
            score
        )
    """

    if not phrases:
        return [], [], 1.0

    matched = [
        phrase
        for phrase in phrases
        if contains_phrase(phrase, corpus)
    ]

    missing = [
        phrase
        for phrase in phrases
        if not contains_phrase(phrase, corpus)
    ]

    score = len(matched) / len(phrases)

    return matched, missing, round(score, 4)