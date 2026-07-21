from __future__ import annotations

from schemas.resume_schema import StructuredResume, ResumeExperienceEntry
from .schema import ResumeSchema


def parse_resume_to_structured_resume(parsed_resume: ResumeSchema) -> StructuredResume:
    experience = [
        ResumeExperienceEntry(
            title=item.job_title or "",
            company=item.company,
            start_date=item.start_date,
            end_date=item.end_date,
            bullets=item.bullets,
        )
        for item in parsed_resume.experience
    ]

    return StructuredResume(
        candidate_name=parsed_resume.contact_info.full_name,
        summary=parsed_resume.summary,
        skills=parsed_resume.skills,
        tools_technologies=parsed_resume.skills,
        experience=experience,
        projects=[project.name or project.description or "" for project in parsed_resume.projects if project.name or project.description],
        education=[f"{item.degree or ''} {item.institution or ''}".strip() for item in parsed_resume.education],
        certifications=[item.name or "" for item in parsed_resume.certifications if item.name],
        raw_text=parsed_resume.summary,
    )
