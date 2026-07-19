from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from services.resume_optimizer.jd_parser import build_structured_jd
from services.resume_optimizer.service import optimize_resume_for_job_with_ats
from compare_cv_jd import build_structured_resume


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def select_job_from_report(raw_jobs: list[dict[str, Any]], report: list[dict[str, Any]]) -> dict[str, Any]:
    if not report:
        raise ValueError("No entries found in cv_jd_match_report.json")

    top_entry = max(report, key=lambda item: item.get("match_score", 0))
    index = top_entry.get("index")
    if index is None:
        raise ValueError("The match report does not include an 'index' field")
    if not 0 <= index < len(raw_jobs):
        raise ValueError(f"Job index {index} is out of range for {len(raw_jobs)} jobs")
    return raw_jobs[index]


def main() -> None:
    resume_path = Path("data/CV.json")
    jd_path = Path("data/machine_learning_engineer_20260711_200219.json")
    report_path = Path("data/cv_jd_match_report.json")
    output_path = Path("data/optimized_resume_output.json")

    raw_resume = load_json(resume_path)
    raw_jobs = load_json(jd_path)
    report = load_json(report_path)

    resume = build_structured_resume(raw_resume)
    if not raw_jobs:
        raise ValueError(f"No jobs found in {jd_path}")

    selected_job = select_job_from_report(raw_jobs, report)
    structured_job = build_structured_jd(selected_job)

    optimized = optimize_resume_for_job_with_ats(structured_job, resume)
    output_path.write_text(optimized.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Generated optimized resume output at {output_path}")
    print(f"Optimized for: {structured_job.title} at {structured_job.company}")


if __name__ == "__main__":
    main()
