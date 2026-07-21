"""
Education matching utilities.

This module compares a candidate's education against the
education requirements specified in the job description.
"""

from __future__ import annotations

from dataclasses import dataclass

from matching.corpus import ResumeCorpus
from matching.common import contains_phrase


@dataclass(slots=True)
class EducationMatchResult:
    """
    Result of education matching.
    """

    matched_education: list[str]

    missing_education: list[str]

    education_score: float


def match_education(
    required_education: list[str],
    corpus: ResumeCorpus,
) -> EducationMatchResult:
    """
    Compare education requirements against the resume.
    """

    # No education requirement specified.
    if not required_education:
        return EducationMatchResult(
            matched_education=[],
            missing_education=[],
            education_score=1.0,
        )

    matched = [
        education
        for education in required_education
        if contains_phrase(education, corpus)
    ]

    missing = [
        education
        for education in required_education
        if not contains_phrase(education, corpus)
    ]

    score = len(matched) / len(required_education)

    return EducationMatchResult(
        matched_education=matched,
        missing_education=missing,
        education_score=round(score, 4),
    )