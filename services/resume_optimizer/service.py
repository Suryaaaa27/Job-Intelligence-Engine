"""
Box E orchestration - single entry point the rest of the system calls.

Usage:
    from services.resume_optimizer.service import optimize_resume_for_job

    result = optimize_resume_for_job(jd, resume)

This is what a FastAPI route in main.py / a pipeline step would call.
Swapping mock JD data for Box D's real output later requires no changes
here - only the caller that constructs jd changes.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from schemas.resume_schemas import (
    StructuredJD,
    StructuredResume,
    OptimizationResult,
    OptimizedResume,
)
from resume_parser.parser import parse_resume
from resume_parser.adapter import parse_resume_to_structured_resume
from services.resume_optimizer.matcher import calculate_match
from services.resume_optimizer.optimizer import optimize
from services.resume_optimizer.ats_scoring import build_ats_report


def optimize_resume_for_job(jd: StructuredJD, resume: StructuredResume) -> OptimizationResult:
    match_result = calculate_match(jd, resume)
    return optimize(jd, resume, match_result)


def optimize_resume_for_job_with_ats(jd: StructuredJD, resume: StructuredResume) -> OptimizedResume:
    match_result = calculate_match(jd, resume)
    optimization_result = optimize(jd, resume, match_result)
    ats_report = build_ats_report(jd, resume)
    return OptimizedResume(
        candidate_name=resume.candidate_name,
        original_resume=resume,
        target_job=jd,
        match_result=match_result,
        ats_report=ats_report,
        optimization_suggestions=optimization_result.suggestions,
        optimized_summary=optimization_result.tailored_summary,
        optimized_bullets=optimization_result.tailored_bullets,
        generated_for_job_id=jd.job_id,
        generated_for_job_title=jd.title,
    )


def load_jd_from_json(path: str) -> StructuredJD:
    with open(path) as f:
        return StructuredJD(**json.load(f))


def load_resume_from_json(path: str) -> StructuredResume:
    with open(path) as f:
        return StructuredResume(**json.load(f))


def load_resume_from_file(path: str) -> StructuredResume:
    parsed_resume = parse_resume(path)
    return parse_resume_to_structured_resume(parsed_resume)


if __name__ == "__main__":
    jd = load_jd_from_json("data/samples/sample_jd.json")
    resume = load_resume_from_json("data/samples/sample_resume.json")

    match = calculate_match(jd, resume)
    print("=== Match Result ===")
    print(match.model_dump_json(indent=2))

    result = optimize_resume_for_job(jd, resume)
    print("=== Optimization Result ===")
    print(result.model_dump_json(indent=2))
