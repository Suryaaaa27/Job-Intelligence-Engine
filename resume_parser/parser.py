"""
Resume Parsing Engine
======================
Entry point for converting a PDF/DOCX resume into the Standard Resume Schema JSON.
"""

import argparse
import json
import os
import sys

try:
    from .schema import ResumeSchema, ParseWarning, Experience, Project, Education, Certification
    from .extractors.pdf_extractor import extract_lines_from_pdf
    from .extractors.docx_extractor import extract_lines_from_docx
    from .section_splitter import split_into_sections
    from .field_extractors import (
        extract_contact_info,
        extract_summary,
        extract_skills,
        extract_experience,
        extract_projects,
        extract_education,
        extract_certifications,
    )
except ImportError:  # pragma: no cover - support direct script execution
    from schema import ResumeSchema, ParseWarning, Experience, Project, Education, Certification
    from extractors.pdf_extractor import extract_lines_from_pdf
    from extractors.docx_extractor import extract_lines_from_docx
    from section_splitter import split_into_sections
    from field_extractors import (
        extract_contact_info,
        extract_summary,
        extract_skills,
        extract_experience,
        extract_projects,
        extract_education,
        extract_certifications,
    )

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".json"}


def _load_resume_from_json(file_path: str) -> ResumeSchema:
    with open(file_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    contact = payload.get("contact_info") or {}
    resume = ResumeSchema(source_file=os.path.basename(file_path), source_file_type="json")
    resume.contact_info.full_name = contact.get("full_name")
    resume.contact_info.email = contact.get("email")
    resume.contact_info.phone = contact.get("phone")
    resume.contact_info.location = contact.get("location")
    resume.contact_info.linkedin = contact.get("linkedin")
    resume.contact_info.github = contact.get("github")
    resume.contact_info.portfolio = contact.get("portfolio")
    resume.summary = payload.get("summary")
    resume.skills = payload.get("skills", [])

    for entry in payload.get("experience", []):
        resume.experience.append(
            Experience(
                job_title=entry.get("job_title"),
                company=entry.get("company"),
                location=entry.get("location"),
                start_date=entry.get("start_date"),
                end_date=entry.get("end_date"),
                is_current=bool(entry.get("is_current")),
                bullets=entry.get("bullets", []),
                raw_text=entry.get("raw_text"),
            )
        )

    for entry in payload.get("projects", []):
        resume.projects.append(
            Project(
                name=entry.get("name"),
                description=entry.get("description"),
                technologies=entry.get("technologies", []),
                bullets=entry.get("bullets", []),
                link=entry.get("link"),
                raw_text=entry.get("raw_text"),
            )
        )

    for entry in payload.get("education", []):
        resume.education.append(
            Education(
                degree=entry.get("degree"),
                institution=entry.get("institution"),
                location=entry.get("location"),
                start_date=entry.get("start_date"),
                end_date=entry.get("end_date"),
                gpa=entry.get("gpa"),
                raw_text=entry.get("raw_text"),
            )
        )

    for entry in payload.get("certifications", []):
        resume.certifications.append(
            Certification(
                name=entry.get("name"),
                issuer=entry.get("issuer"),
                date=entry.get("date"),
                raw_text=entry.get("raw_text"),
            )
        )

    return resume


def parse_resume(file_path: str) -> ResumeSchema:
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported types: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    if ext == ".json":
        return _load_resume_from_json(file_path)

    if ext == ".pdf":
        lines = extract_lines_from_pdf(file_path)
        file_type = "pdf"
    else:
        lines = extract_lines_from_docx(file_path)
        file_type = "docx"

    resume = ResumeSchema(source_file=os.path.basename(file_path), source_file_type=file_type)

    if not lines:
        resume.warnings.append(
            ParseWarning(
                section="document",
                message="No extractable text found. File may be an image-based scan; OCR would be required.",
            )
        )
        return resume

    sections = split_into_sections(lines)
    resume.raw_sections = {k: "\n".join(v) for k, v in sections.items()}

    preamble = sections.get("preamble", [])
    resume.contact_info = extract_contact_info(preamble)

    if "summary" in sections:
        resume.summary = extract_summary(sections["summary"])
    else:
        leftover = [
            line for line in preamble if line != resume.contact_info.full_name and line != resume.contact_info.location and len(line.split()) > 6
        ]
        if leftover:
            resume.summary = " ".join(leftover)
        else:
            resume.warnings.append(
                ParseWarning(section="summary", message="No Summary/Objective section detected.")
            )

    if "skills" in sections:
        resume.skills = extract_skills(sections["skills"])
    else:
        resume.warnings.append(ParseWarning(section="skills", message="No Skills section detected."))

    if "experience" in sections:
        resume.experience = extract_experience(sections["experience"])
    else:
        resume.warnings.append(ParseWarning(section="experience", message="No Experience section detected."))

    if "projects" in sections:
        resume.projects = extract_projects(sections["projects"])

    if "education" in sections:
        resume.education = extract_education(sections["education"])
    else:
        resume.warnings.append(ParseWarning(section="education", message="No Education section detected."))

    if "certifications" in sections:
        resume.certifications = extract_certifications(sections["certifications"])

    return resume


def main():
    parser = argparse.ArgumentParser(description="Parse a resume (PDF/DOCX) into the Standard Resume Schema JSON.")
    parser.add_argument("file_path", help="Path to a .pdf or .docx resume file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("-o", "--output", help="Write JSON output to this file instead of stdout")
    args = parser.parse_args()

    resume = parse_resume(args.file_path)
    output_dict = resume.to_dict()
    indent = 2 if args.pretty else None
    json_str = json.dumps(output_dict, indent=indent, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(json_str)
        print(f"Wrote parsed resume JSON to {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
