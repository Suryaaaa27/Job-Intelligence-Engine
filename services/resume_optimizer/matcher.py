"""
Match score calculator — Box E component.

Deterministic (no LLM call) so it's fast, cheap, and testable.
Compares a StructuredResume against a StructuredJD and produces a MatchResult.
"""

from __future__ import annotations
import re
from typing import Iterable
from schemas.resume_schemas import StructuredJD, StructuredResume, MatchResult, SkillGap

SKILL_WEIGHT = 0.45
EXPERIENCE_WEIGHT = 0.20
EDUCATION_WEIGHT = 0.10
CERTIFICATION_WEIGHT = 0.05
KEYWORD_WEIGHT = 0.10
SEMANTIC_WEIGHT = 0.10


def _normalize(term: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]", "", term.lower()).strip()


def _resume_corpus(resume: StructuredResume) -> tuple[set[str], str, str, str]:
    """All normalized resume terms and text blobs for matching."""
    terms = set(_normalize(item) for item in resume.skills + resume.tools_technologies)
    blob = " ".join(
        [resume.summary or ""]
        + [b for exp in resume.experience for b in exp.bullets]
    ).lower()
    education_blob = " ".join(resume.education).lower()
    certification_blob = " ".join(resume.certifications).lower()
    return terms, blob, education_blob, certification_blob


def _present(term: str, terms: set[str], blob: str) -> bool:
    norm = _normalize(term)
    if not norm:
        return False
    if norm in terms:
        return True
    return norm in blob


def _phrase_match_ratio(phrases: list[str], terms: set[str], blob: str) -> float:
    if not phrases:
        return 1.0
    matched = 0
    for phrase in phrases:
        if _present(phrase, terms, blob):
            matched += 1
    return matched / len(phrases)


def _semantic_overlap(jd_text: str, resume_text: str) -> float:
    jd_words = set(_normalize(word) for word in re.findall(r"\w+", jd_text.lower()))
    resume_words = set(_normalize(word) for word in re.findall(r"\w+", resume_text.lower()))
    jd_words.discard("")
    resume_words.discard("")
    if not jd_words or not resume_words:
        return 1.0
    intersection = jd_words.intersection(resume_words)
    return len(intersection) / max(len(jd_words), len(resume_words))


def calculate_match(jd: StructuredJD, resume: StructuredResume) -> MatchResult:
    resume_terms, resume_blob, education_blob, certification_blob = _resume_corpus(resume)
    resume_text = " ".join([resume_blob, education_blob, certification_blob])

    matched_required = [s for s in jd.required_skills if _present(s, resume_terms, resume_blob)]
    missing_required = [s for s in jd.required_skills if not _present(s, resume_terms, resume_blob)]
    matched_preferred = [s for s in jd.preferred_skills if _present(s, resume_terms, resume_blob)]
    missing_preferred = [s for s in jd.preferred_skills if not _present(s, resume_terms, resume_blob)]

    required_score = len(matched_required) / len(jd.required_skills) if jd.required_skills else 1.0
    preferred_score = len(matched_preferred) / len(jd.preferred_skills) if jd.preferred_skills else 1.0
    skills_score = required_score * 0.75 + preferred_score * 0.25

    experience_gap = None
    experience_score = 1.0
    if jd.min_experience_years is not None:
        candidate_years = resume.total_experience_years or 0.0
        experience_gap = candidate_years - jd.min_experience_years
        experience_score = min(1.0, max(0.0, candidate_years / jd.min_experience_years)) if jd.min_experience_years > 0 else 1.0

    education_score = _phrase_match_ratio(jd.education_requirements, resume_terms, resume_blob if resume_blob else education_blob)
    matched_education = [edu for edu in jd.education_requirements if _present(edu, resume_terms, resume_blob if resume_blob else education_blob)]
    missing_education = [edu for edu in jd.education_requirements if edu not in matched_education]

    certification_score = _phrase_match_ratio(jd.certifications, resume_terms, certification_blob)
    matched_certifications = [cert for cert in jd.certifications if _present(cert, resume_terms, certification_blob)]
    missing_certifications = [cert for cert in jd.certifications if cert not in matched_certifications]

    keyword_phrases = jd.responsibilities + jd.qualifications
    keyword_score = _phrase_match_ratio(keyword_phrases, resume_terms, resume_blob)

    semantic_score = _semantic_overlap(jd.raw_text or "", resume_text)

    total_score = (
        skills_score * SKILL_WEIGHT
        + experience_score * EXPERIENCE_WEIGHT
        + education_score * EDUCATION_WEIGHT
        + certification_score * CERTIFICATION_WEIGHT
        + keyword_score * KEYWORD_WEIGHT
        + semantic_score * SEMANTIC_WEIGHT
    ) * 100

    skill_gaps = [
        SkillGap(skill=s, importance="required", present_in_resume=False)
        for s in missing_required
    ] + [
        SkillGap(skill=s, importance="preferred", present_in_resume=False)
        for s in missing_preferred
    ]

    return MatchResult(
        match_score=round(total_score, 1),
        matched_required_skills=matched_required,
        matched_preferred_skills=matched_preferred,
        missing_required_skills=missing_required,
        missing_preferred_skills=missing_preferred,
        missing_education=missing_education,
        missing_certifications=missing_certifications,
        experience_gap_years=round(experience_gap, 1) if experience_gap is not None else None,
        skills_score=round(skills_score * 100, 1),
        experience_score=round(experience_score * 100, 1),
        education_score=round(education_score * 100, 1),
        certification_score=round(certification_score * 100, 1),
        keyword_score=round(keyword_score * 100, 1),
        semantic_score=round(semantic_score * 100, 1),
        skill_gaps=skill_gaps,
    )
