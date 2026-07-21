"""
Keyword matching utilities.

This module evaluates how well the resume aligns with the
responsibilities and qualifications mentioned in a job description.
"""

from __future__ import annotations

from dataclasses import dataclass

from matching.common import match_ratio
from matching.corpus import ResumeCorpus


@dataclass(slots=True)
class KeywordMatchResult:
    """
    Result of keyword matching.
    """

    matched_keywords: list[str]

    missing_keywords: list[str]

    keyword_score: float


def match_keywords(
    responsibilities: list[str],
    qualifications: list[str],
    corpus: ResumeCorpus,
) -> KeywordMatchResult:
    """
    Match JD responsibilities and qualifications against the resume.
    """

    phrases = responsibilities + qualifications

    matched, missing, score = match_ratio(
        phrases,
        corpus,
    )

    return KeywordMatchResult(
        matched_keywords=matched,
        missing_keywords=missing,
        keyword_score=score,
    )