"""
Resume corpus builder.

Builds a normalized representation of a resume so that all matching modules
operate on the same searchable data instead of rebuilding text repeatedly.
"""

from __future__ import annotations

from dataclasses import dataclass

from schemas.resume_schema import StructuredResume
from matching.normalization import normalize, normalize_collection


@dataclass(slots=True)
class ResumeCorpus:
    """
    Searchable representation of a structured resume.
    """

    skills: set[str]

    summary: str

    experience: str

    education: str

    certifications: str

    projects: str

    full_text: str


def build_resume_corpus(resume: StructuredResume) -> ResumeCorpus:
    """
    Convert a StructuredResume into a searchable corpus.
    """

    skills = normalize_collection(
        (resume.skills or [])
        + (resume.tools_technologies or [])
    )

    summary = normalize(resume.summary)

    experience = normalize(
        " ".join(
            bullet
            for exp in resume.experience
            for bullet in exp.bullets
        )
    )

    education = normalize(" ".join(resume.education or []))

    certifications = normalize(
        " ".join(resume.certifications or [])
    )

    projects = normalize(
        " ".join(resume.projects or [])
    )

    full_text = " ".join(
        filter(
            None,
            [
                summary,
                experience,
                education,
                certifications,
                projects,
                " ".join(skills),
            ],
        )
    )

    return ResumeCorpus(
        skills=skills,
        summary=summary,
        experience=experience,
        education=education,
        certifications=certifications,
        projects=projects,
        full_text=full_text,
    )