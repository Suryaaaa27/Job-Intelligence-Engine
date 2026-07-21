"""
Skill matching utilities.

This module is responsible for comparing resume skills against the job
description and producing skill scores and gap information.
"""

from __future__ import annotations

from dataclasses import dataclass

from matching.corpus import ResumeCorpus
from matching.normalization import normalize
from schemas.resume_schema import SkillGap
from matching.common import contains_phrase

@dataclass(slots=True)
class SkillMatchResult:
    """
    Result of deterministic skill matching.
    """

    matched_required: list[str]

    missing_required: list[str]

    matched_preferred: list[str]

    missing_preferred: list[str]

    skills_score: float

    skill_gaps: list[SkillGap]

def match_skills(
    required_skills: list[str],
    preferred_skills: list[str],
    corpus: ResumeCorpus,
) -> SkillMatchResult:
    """
    Compare required and preferred skills against a resume corpus.
    """

    matched_required = [
        skill
        for skill in required_skills
        if contains_phrase(skill, corpus)
    ]

    missing_required = [
        skill
        for skill in required_skills
        if not contains_phrase(skill, corpus)
    ]

    matched_preferred = [
        skill
        for skill in preferred_skills
        if contains_phrase(skill, corpus)
    ]

    missing_preferred = [
        skill
        for skill in preferred_skills
        if not contains_phrase(skill, corpus)
    ]

    required_score = (
        len(matched_required) / len(required_skills)
        if required_skills
        else 1.0
    )

    preferred_score = (
        len(matched_preferred) / len(preferred_skills)
        if preferred_skills
        else 1.0
    )

    # Required skills contribute more heavily.
    skills_score = (
        required_score * 0.75
        + preferred_score * 0.25
    )

    skill_gaps = [
        SkillGap(
            skill=skill,
            importance="required",
            present_in_resume=False,
        )
        for skill in missing_required
    ]

    skill_gaps.extend(
        SkillGap(
            skill=skill,
            importance="preferred",
            present_in_resume=False,
        )
        for skill in missing_preferred
    )

    return SkillMatchResult(
        matched_required=matched_required,
        missing_required=missing_required,
        matched_preferred=matched_preferred,
        missing_preferred=missing_preferred,
        skills_score=skills_score,
        skill_gaps=skill_gaps,
    )