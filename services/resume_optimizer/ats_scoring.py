from __future__ import annotations
import re
from typing import List
from schemas.resume_schemas import ATSReport, StructuredJD, StructuredResume

KEYWORD_FIELDS = [
    "summary",
    "education",
    "certifications",
    "skills",
    "tools_technologies",
    "experience",
    "projects",
]

WEAK_SECTION_THRESHOLDS = {
    "summary": 50,
    "experience": 1,
    "projects": 1,
    "education": 1,
    "certifications": 0,
}

FORMAT_PATTERNS = {
    "missing_summary": re.compile(r"^\s*$", re.MULTILINE),
    "too_long_bullet": re.compile(r"^.{151,}$", re.MULTILINE),
    "inconsistent_bullets": re.compile(r"^\s*[-*•]\s+.+", re.MULTILINE),
}


def _normalize(term: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]", "", term.lower()).strip()


def _build_resume_text(resume: StructuredResume) -> str:
    parts = [resume.summary or ""]
    parts.extend(resume.skills)
    parts.extend(resume.tools_technologies)
    parts.extend(project for project in resume.projects)
    parts.extend(resume.education)
    parts.extend(resume.certifications)
    parts.extend(bullet for exp in resume.experience for bullet in exp.bullets)
    return " ".join(str(part) for part in parts if part)


def _phrase_match(phrases: List[str], resume_text: str) -> List[str]:
    normalized = _normalize(resume_text)
    missing = []
    for phrase in phrases:
        norm = _normalize(phrase)
        if norm and norm not in normalized:
            missing.append(phrase)
    return missing


def _project_score(resume: StructuredResume, jd: StructuredJD) -> float:
    if not resume.projects and not jd.responsibilities:
        return 1.0
    if not resume.projects:
        return 0.0

    project_text = " ".join(resume.projects).lower()
    matches = 0
    keywords = jd.required_skills + jd.preferred_skills
    for keyword in keywords:
        if keyword.lower() in project_text:
            matches += 1
    return min(1.0, matches / max(1, len(keywords)))


def _education_score(resume: StructuredResume, jd: StructuredJD) -> float:
    if not jd.education_requirements:
        return 1.0
    resume_text = _build_resume_text(resume).lower()
    matches = 0
    for requirement in jd.education_requirements:
        if requirement.lower() in resume_text:
            matches += 1
    return matches / len(jd.education_requirements)


def _certification_score(resume: StructuredResume, jd: StructuredJD) -> float:
    if not jd.certifications:
        return 1.0
    resume_text = _build_resume_text(resume).lower()
    matches = 0
    for cert in jd.certifications:
        if cert.lower() in resume_text:
            matches += 1
    return matches / len(jd.certifications)


def _keyword_score(resume: StructuredResume, jd: StructuredJD) -> float:
    resume_text = _build_resume_text(resume).lower()
    keywords = jd.responsibilities + jd.qualifications
    if not keywords:
        return 1.0
    matches = 0
    for keyword in keywords:
        if keyword.lower() in resume_text:
            matches += 1
    return matches / len(keywords)


def _weak_sections(resume: StructuredResume) -> List[str]:
    weak = []
    if not resume.summary or len(resume.summary) < WEAK_SECTION_THRESHOLDS["summary"]:
        weak.append("summary")
    if len(resume.experience) < WEAK_SECTION_THRESHOLDS["experience"]:
        weak.append("experience")
    if len(resume.projects) < WEAK_SECTION_THRESHOLDS["projects"]:
        weak.append("projects")
    if len(resume.education) < WEAK_SECTION_THRESHOLDS["education"]:
        weak.append("education")
    return weak


def _formatting_issues(resume: StructuredResume) -> List[str]:
    issues = []
    if not resume.summary or not resume.summary.strip():
        issues.append("missing summary")
    if any(len(bullet) > 150 for exp in resume.experience for bullet in exp.bullets):
        issues.append("long experience bullet")
    if resume.projects and any(len(project) > 200 for project in resume.projects):
        issues.append("long project description")
    return issues


def build_ats_report(jd: StructuredJD, resume: StructuredResume) -> ATSReport:
    overall_score = (
        _project_score(resume, jd) * 0.15
        + _education_score(resume, jd) * 0.15
        + _certification_score(resume, jd) * 0.10
        + _keyword_score(resume, jd) * 0.20
        + min(1.0, len(resume.skills) / max(1, len(jd.required_skills))) * 0.40
    )

    missing_skills = _phrase_match(jd.required_skills + jd.preferred_skills, _build_resume_text(resume))
    missing_keywords = _phrase_match(jd.responsibilities + jd.qualifications, _build_resume_text(resume))
    weak_sections = _weak_sections(resume)
    formatting_issues = _formatting_issues(resume)

    return ATSReport(
        overall_score=round(overall_score * 100, 1),
        skills_score=round(min(1.0, len(resume.skills) / max(1, len(jd.required_skills))) * 100, 1),
        experience_score=round(_project_score(resume, jd) * 100, 1),
        project_score=round(_project_score(resume, jd) * 100, 1),
        education_score=round(_education_score(resume, jd) * 100, 1),
        certification_score=round(_certification_score(resume, jd) * 100, 1),
        missing_skills=missing_skills,
        missing_keywords=missing_keywords,
        weak_sections=weak_sections,
        formatting_issues=formatting_issues,
    )
