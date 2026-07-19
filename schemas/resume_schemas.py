"""
Shared data schemas for Team B — Group E (Resume & ATS Optimization).

These models define the CONTRACT between:
  - Box D (Job Description Analysis) -> produces StructuredJD
  - Box E (Resume & ATS Optimization) -> consumes StructuredJD + Resume

Until Box D's real output is wired in, use data/samples/sample_jd.json
(matching StructuredJD) as a stand-in. Swap the source later without
touching matcher/optimizer code, as long as the field names below stay
the same.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class StructuredJD(BaseModel):
    """Structured Job Description — expected output of Box D."""

    job_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None  # full-time, contract, internship, etc.
    salary_range: Optional[str] = None

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    tools_technologies: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    min_experience_years: Optional[float] = None
    education_requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)

    raw_text: Optional[str] = None  # full JD text, if available


class ResumeExperienceEntry(BaseModel):
    title: str
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: list[str] = Field(default_factory=list)


class StructuredResume(BaseModel):
    """Parsed resume — input to Box E from the candidate's raw resume."""

    candidate_name: Optional[str] = None
    contact_info: Optional[dict] = Field(default_factory=dict)
    summary: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    tools_technologies: list[str] = Field(default_factory=list)
    experience: list[ResumeExperienceEntry] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    total_experience_years: Optional[float] = None

    raw_text: Optional[str] = None  # full resume text, if available


class SkillGap(BaseModel):
    skill: str
    importance: str  # "required" | "preferred"
    present_in_resume: bool


class MatchResult(BaseModel):
    """Output of the matcher: score + gap analysis."""

    match_score: float  # 0-100
    matched_required_skills: list[str]
    matched_preferred_skills: list[str]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]
    missing_education: list[str] = Field(default_factory=list)
    missing_certifications: list[str] = Field(default_factory=list)
    experience_gap_years: Optional[float] = None  # negative = candidate exceeds requirement
    skills_score: float
    experience_score: float
    education_score: float
    certification_score: float
    keyword_score: float
    semantic_score: float
    skill_gaps: list[SkillGap] = Field(default_factory=list)


class ATSReport(BaseModel):
    overall_score: float
    skills_score: float
    experience_score: float
    project_score: float
    education_score: float
    certification_score: float
    missing_skills: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    weak_sections: list[str] = Field(default_factory=list)
    formatting_issues: list[str] = Field(default_factory=list)


class OptimizationSuggestion(BaseModel):
    category: str  # "keyword" | "bullet_rewrite" | "structure" | "experience"
    suggestion: str
    priority: str  # "high" | "medium" | "low"


class OptimizationResult(BaseModel):
    match_result: MatchResult
    suggestions: list[OptimizationSuggestion]
    tailored_summary: Optional[str] = None
    tailored_bullets: dict[str, list[str]] = Field(default_factory=dict)  # job_title -> bullets


class OptimizedResume(BaseModel):
    candidate_name: Optional[str] = None
    original_resume: StructuredResume
    target_job: StructuredJD
    match_result: MatchResult
    ats_report: ATSReport
    optimization_suggestions: list[OptimizationSuggestion] = Field(default_factory=list)
    optimized_summary: Optional[str] = None
    optimized_bullets: dict[str, list[str]] = Field(default_factory=dict)
    generated_for_job_id: Optional[str] = None
    generated_for_job_title: Optional[str] = None
