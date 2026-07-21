"""
Experience matching utilities.

This module compares a candidate's work experience against the
minimum experience required by the job description.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExperienceMatchResult:
    """
    Result of experience matching.
    """

    candidate_years: float

    required_years: float | None

    experience_gap_years: float | None

    experience_score: float


def match_experience(
    candidate_years: float | None,
    required_years: float | None,
) -> ExperienceMatchResult:
    """
    Compare candidate experience against the job requirement.

    Returns:
        ExperienceMatchResult
    """

    candidate = candidate_years or 0.0

    # No experience requirement in JD
    if required_years is None:
        return ExperienceMatchResult(
            candidate_years=candidate,
            required_years=None,
            experience_gap_years=None,
            experience_score=1.0,
        )

    # Prevent division by zero
    if required_years <= 0:
        return ExperienceMatchResult(
            candidate_years=candidate,
            required_years=required_years,
            experience_gap_years=0.0,
            experience_score=1.0,
        )

    gap = candidate - required_years

    # Score between 0 and 1
    score = min(1.0, candidate / required_years)

    return ExperienceMatchResult(
        candidate_years=candidate,
        required_years=required_years,
        experience_gap_years=round(gap, 1),
        experience_score=round(score, 4),
    )