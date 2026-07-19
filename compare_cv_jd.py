import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.resume_schemas import ResumeExperienceEntry, StructuredJD, StructuredResume
from services.resume_optimizer.jd_parser import build_structured_jd
from services.resume_optimizer.matcher import calculate_match
from services.resume_optimizer.ats_scoring import build_ats_report

COMMON_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "golang",
    "go",
    "c++",
    "c#",
    "sql",
    "postgresql",
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "spark",
    "hadoop",
    "docker",
    "kubernetes",
    "terraform",
    "aws",
    "gcp",
    "google cloud",
    "azure",
    "fastapi",
    "flask",
    "django",
    "react",
    "next.js",
    "node.js",
    "express",
    "graphql",
    "git",
    "rest api",
    "rest",
    "microservices",
    "machine learning",
    "deep learning",
    "data science",
    "natural language processing",
    "nlp",
    "computer vision",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "scipy",
    "keras",
    "transformers",
    "airflow",
    "ci/cd",
    "jenkins",
    "spark",
    "pyspark",
    "mlops",
    "data engineering",
    "big data",
    "statistical modeling",
    "cloud computing",
    "data analytics",
    "computer vision",
    "nlp",
]


def load_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_skill_term(skill: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]", "", skill.lower()).strip()


def extract_skills_from_text(text: str) -> list[str]:
    text = text.lower()
    found = []

    for skill in COMMON_SKILLS:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text) and skill not in found:
            found.append(skill)

    return found


def normalize_text_field(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return " ".join(str(v).strip() for v in value.values() if v)
    if isinstance(value, list):
        return " ".join(str(v).strip() for v in value if v)
    return str(value)


def build_structured_resume(raw_resume: dict[str, Any]) -> StructuredResume:
    experience_entries: list[ResumeExperienceEntry] = []

    for item in raw_resume.get("experience", []):
        experience_entries.append(
            ResumeExperienceEntry(
                title=item.get("title") or item.get("job_title") or "",
                company=item.get("company"),
                start_date=item.get("start_date"),
                end_date=item.get("end_date"),
                bullets=item.get("bullets", []),
            )
        )

    skills = raw_resume.get("skills", []) or []
    tools = raw_resume.get("tools_technologies", []) or skills
    education = raw_resume.get("education", [])
    certifications = raw_resume.get("certifications", [])

    raw_text_parts = [raw_resume.get("summary", "")]
    raw_text_parts.extend([e.raw_text for e in experience_entries if getattr(e, "raw_text", None)])
    raw_text_parts.extend([item.get("raw_text") or normalize_text_field(item) if isinstance(item, dict) else str(item) for item in education])
    raw_text_parts.extend([item.get("raw_text") or normalize_text_field(item) if isinstance(item, dict) else str(item) for item in certifications])

    return StructuredResume(
        candidate_name=raw_resume.get("contact_info", {}).get("full_name")
        or raw_resume.get("candidate_name"),
        contact_info=raw_resume.get("contact_info", {}),
        summary=raw_resume.get("summary"),
        skills=skills,
        tools_technologies=tools,
        experience=experience_entries,
        education=education,
        certifications=certifications,
        total_experience_years=raw_resume.get("total_experience_years"),
        raw_text=" ".join([part for part in raw_text_parts if part]),
    )


def build_structured_jd(job: dict[str, Any]) -> StructuredJD:
    title = job.get("job_title") or job.get("title") or ""
    description = job.get("description", "") or ""
    name = job.get("company_name") or job.get("company")
    raw_text = "\n".join([title, company_text := name or "", description])

    extracted_skills = extract_skills_from_text(raw_text)
    required_skills = extracted_skills[:10]
    preferred_skills = extracted_skills[10:20]

    return StructuredJD(
        job_id=job.get("job_id", ""),
        title=title,
        company=name,
        location=job.get("location"),
        employment_type=job.get("employment_type") or job.get("workplace_type"),
        salary_range=job.get("salary"),
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        tools_technologies=extracted_skills,
        min_experience_years=None,
        education_requirements=job.get("education_requirements", []),
        responsibilities=job.get("responsibilities", []),
        qualifications=job.get("qualifications", []),
        raw_text=description,
    )


def compare_resume_to_jd(resume_path: Path, jd_path: Path) -> list[dict[str, Any]]:
    raw_resume = load_json_file(resume_path)
    raw_jobs = load_json_file(jd_path)

    resume = build_structured_resume(raw_resume)
    results = []

    for index, raw_job in enumerate(raw_jobs):
        jd = build_structured_jd(raw_job)
        match_result = calculate_match(jd, resume)

        result = match_result.model_dump()
        ats_report = build_ats_report(jd, resume)
        result.update(
            {
                "index": index,
                "job_title": jd.title,
                "company": jd.company,
                "location": jd.location,
                "job_url": raw_job.get("job_url"),
                "description": raw_job.get("description", "")[:300],
                "ats_report": ats_report.model_dump(),
            }
        )
        results.append(result)

    return sorted(results, key=lambda item: item["match_score"], reverse=True)


def save_report(report: list[dict[str, Any]], path: Path) -> None:
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    resume_path = Path("data/CV.json")
    jd_path = Path("data/filtered_jobs.json")
    report_path = Path("data/cv_jd_match_report.json")

    report = compare_resume_to_jd(resume_path, jd_path)
    save_report(report, report_path)

    print(f"Compared resume '{resume_path.name}' against {len(report)} job postings.")
    print("Top 5 matches:")
    for item in report[:5]:
        print(
            f"{item['match_score']}% — {item['job_title']} @ {item['company']} ({item['location']})"
        )
    print(f"Saved full report to {report_path}")
