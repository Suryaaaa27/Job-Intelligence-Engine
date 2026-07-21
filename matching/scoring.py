"""
Weighted score calculation utilities.

This module combines individual matching scores into a single
overall resume-job match score.
"""

from __future__ import annotations

from dataclasses import dataclass


# -----------------------------
# Default scoring weights
# -----------------------------

SKILL_WEIGHT = 0.45
EXPERIENCE_WEIGHT = 0.20
EDUCATION_WEIGHT = 0.10
CERTIFICATION_WEIGHT = 0.05
KEYWORD_WEIGHT = 0.10
LEXICAL_WEIGHT = 0.10


@dataclass(slots=True)
class MatchScores:
    """
    Individual component scores.

    All values should be floats between 0.0 and 1.0.
    """

    skills: float

    experience: float

    education: float

    certification: float

    keyword: float

    lexical: float


def calculate_overall_score(scores: MatchScores) -> float:
    """
    Calculate the weighted overall score.

    Returns:
        Overall score between 0 and 100.
    """

    overall = (
        scores.skills * SKILL_WEIGHT
        + scores.experience * EXPERIENCE_WEIGHT
        + scores.education * EDUCATION_WEIGHT
        + scores.certification * CERTIFICATION_WEIGHT
        + scores.keyword * KEYWORD_WEIGHT
        + scores.lexical * LEXICAL_WEIGHT
    )

    return round(overall * 100, 1)