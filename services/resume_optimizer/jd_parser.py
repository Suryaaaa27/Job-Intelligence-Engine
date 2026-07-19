from __future__ import annotations
import re
from typing import Any
from schemas.resume_schemas import StructuredJD

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
    "api",
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
    "data visualization",
    "linux",
    "shell scripting",
    "bash",
    "python 3",
    "pytorch",
    "keras",
    "opencv",
    "sql server",
    "snowflake",
    "airflow",
    "dbt",
    "kafka",
    "spark",
    "tableau",
    "power bi",
    "mlops",
    "site reliability engineering",
    "sre",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "ansible",
    "chef",
    "puppet",
    "gitlab",
    "github",
    "bitbucket",
    "ci/cd",
    "monitoring",
    "prometheus",
    "grafana",
]

EDUCATION_TERMS = [
    "bachelor",
    "master",
    "phd",
    "mba",
    "associate",
    "degree",
    "bachelors",
    "master's",
    "ph.d",
    "doctoral",
]

CERTIFICATION_TERMS = [
    "aws certified",
    "azure certified",
    "google cloud certified",
    "pmp",
    "scrum master",
    "cissp",
    "certified",
    "ccna",
    "ccnp",
    "security+",
    "linux foundation",
    "oracle certified",
    "databricks",
    "tableau certified",
    "google professional",
    "certification",
]

EXPERIENCE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)\s*(?:of\s*)?(?:experience|exp)", re.IGNORECASE)


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]", "", text.lower()).strip()


def _find_terms(text: str, terms: list[str]) -> list[str]:
    normalized = _normalize(text)
    found = []
    for term in terms:
        if term in normalized and term not in found:
            found.append(term)
    return found


def _extract_bullets(text: str) -> list[str]:
    lines = text.splitlines()
    bullets = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("•") or stripped.startswith("-") or stripped.startswith("*"):
            bullets.append(stripped.lstrip("•-* ").strip())
        elif re.match(r"^(?:Responsibilities|Qualifications|Skills|Requirements|Role Description|Job Description)[:\s]", stripped, re.IGNORECASE):
            continue
    return bullets


def _extract_section_lines(text: str, headings: list[str]) -> list[str]:
    normalized = text.replace("\r", "")
    lines = normalized.split("\n")
    results = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if any(re.match(rf"^{re.escape(heading)}[:\s]*$", stripped, re.IGNORECASE) for heading in headings):
            capture = True
            continue
        if capture:
            if not stripped:
                break
            if stripped.startswith("•") or stripped.startswith("-") or stripped.startswith("*"):
                results.append(stripped.lstrip("•-* ").strip())
            elif stripped and not re.match(r"^[A-Z][a-z]+", stripped):
                results.append(stripped)
            elif stripped and not stripped.endswith("."):
                results.append(stripped)
            else:
                continue
    return results


def _extract_experience_years(text: str) -> float | None:
    match = EXPERIENCE_PATTERN.search(text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def _extract_education_requirements(text: str) -> list[str]:
    extracted = []
    for phrase in EDUCATION_TERMS:
        if phrase in text.lower() and phrase not in extracted:
            extracted.append(phrase)
    return extracted


def _extract_certifications(text: str) -> list[str]:
    extracted = []
    for phrase in CERTIFICATION_TERMS:
        if phrase in text.lower() and phrase not in extracted:
            extracted.append(phrase)
    return extracted


def _extract_responsibilities(text: str) -> list[str]:
    blocks = _extract_section_lines(text, ["Responsibilities", "Role Description", "What You Will Do", "What You Will Be Doing"])
    if blocks:
        return blocks
    return _extract_bullets(text)


def _extract_qualifications(text: str) -> list[str]:
    blocks = _extract_section_lines(text, ["Qualifications", "Skills & Requirements", "Requirements", "What We're Looking For"])
    if blocks:
        return blocks
    return _extract_bullets(text)


def build_structured_jd(job: dict[str, Any]) -> StructuredJD:
    title = job.get("job_title") or job.get("title") or ""
    description = job.get("description", "") or ""
    company = job.get("company_name") or job.get("company")
    raw_text = "\n".join([title, company or "", description])

    skills = _find_terms(raw_text, COMMON_SKILLS)
    required_skills = skills[:10]
    preferred_skills = skills[10:20]

    experience_years = _extract_experience_years(raw_text)
    education_requirements = _extract_education_requirements(raw_text)
    certifications = _extract_certifications(raw_text)
    responsibilities = _extract_responsibilities(description)
    qualifications = _extract_qualifications(description)

    return StructuredJD(
        job_id=job.get("job_id") or job.get("job_url", ""),
        title=title,
        company=company,
        location=job.get("location"),
        employment_type=job.get("employment_type") or job.get("workplace_type"),
        salary_range=job.get("salary"),
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        tools_technologies=skills,
        certifications=certifications,
        min_experience_years=experience_years,
        education_requirements=education_requirements,
        responsibilities=responsibilities,
        qualifications=qualifications,
        raw_text=raw_text,
    )
