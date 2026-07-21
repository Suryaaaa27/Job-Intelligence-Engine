"""
Certification matching utilities.

This module compares candidate certifications against the
certification requirements specified in the job description.
"""

from __future__ import annotations

from dataclasses import dataclass

from matching.corpus import ResumeCorpus
from matching.common import contains_phrase


@dataclass(slots=True)
class CertificationMatchResult:
    """
    Result of certification matching.
    """

    matched_certifications: list[str]

    missing_certifications: list[str]

    certification_score: float


def match_certifications(
    required_certifications: list[str],
    corpus: ResumeCorpus,
) -> CertificationMatchResult:
    """
    Compare certification requirements against the resume.
    """

    # No certification requirement in JD
    if not required_certifications:
        return CertificationMatchResult(
            matched_certifications=[],
            missing_certifications=[],
            certification_score=1.0,
        )

    matched = [
        certification
        for certification in required_certifications
        if contains_phrase(certification, corpus)
    ]

    missing = [
        certification
        for certification in required_certifications
        if not contains_phrase(certification, corpus)
    ]

    score = len(matched) / len(required_certifications)

    return CertificationMatchResult(
        matched_certifications=matched,
        missing_certifications=missing,
        certification_score=round(score, 4),
    )