"""
Resume optimizer — Box E component.

Uses an LLM (Google Gemini 3.5 Flash) to:
  1. Generate concrete improvement suggestions based on MatchResult gaps
  2. Rewrite/tailor resume bullets and summary to target the JD

Kept separate from matcher.py so scoring stays deterministic and testable,
while tailoring (which genuinely needs generation) is isolated and mockable.
"""

from __future__ import annotations
import json
import os
from typing import Any

from schemas.resume_schemas import (
    StructuredJD,
    StructuredResume,
    MatchResult,
    OptimizationResult,
    OptimizationSuggestion,
)

DEFAULT_MODEL = "gemini-3.5-flash"
FALLBACK_MODELS = ["gemini-3.5-pro", "gemini-1.5", "gemini-1.0"]
MODEL = os.environ.get("RESUME_OPTIMIZER_MODEL", DEFAULT_MODEL)


SUGGESTION_PROMPT = """You are an ATS resume optimization assistant.

Given a job description's required/missing skills and a candidate's resume,
produce a JSON array of improvement suggestions. Each item must have:
  - "category": one of "keyword", "bullet_rewrite", "structure", "experience"
  - "suggestion": a specific, actionable instruction (not generic advice)
  - "priority": "high", "medium", or "low"

Focus on the MISSING required skills first (high priority), then missing
preferred skills (medium), then general resume quality (low).

Missing required skills: {missing_required}
Missing preferred skills: {missing_preferred}
Experience gap (years, negative = candidate exceeds requirement): {experience_gap}

Candidate resume summary: {summary}
Candidate experience bullets: {bullets}

Return ONLY a JSON array, no other text."""


TAILOR_PROMPT = """You are a resume tailoring assistant. Rewrite the candidate's
resume summary and experience bullets to better match the target job description,
naturally incorporating relevant keywords the candidate genuinely has evidence for.

Do NOT fabricate skills or experience the candidate doesn't have.
Keep bullets truthful — only rephrase/reorder/emphasize, don't invent claims.

Job title: {jd_title}
Job required skills: {required_skills}
Job responsibilities: {responsibilities}

Candidate current summary: {summary}
Candidate current experience (JSON): {experience}

Return ONLY a JSON object with this shape:
{{
  "tailored_summary": "...",
  "tailored_bullets": {{ "<job title>": ["bullet1", "bullet2", ...] }}
}}"""


def _configure_gemini() -> tuple[Any, bool]:
    legacy = False
    try:
        import google.genai as genai
    except ModuleNotFoundError:
        try:
            import google.generativeai as genai
            legacy = True
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Gemini resume optimization requires either the google-genai or "
                "google-generativeai package. Install one with: pip install google-genai"
            ) from exc

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "The GOOGLE_API_KEY environment variable is not set. "
            "Set it before running the optimizer, for example: export GOOGLE_API_KEY=your_key"
        )

    if legacy:
        genai.configure(api_key=api_key)
        return genai, legacy

    client = genai.Client(api_key=api_key)
    return client, legacy


def _extract_gemini_text(response: Any) -> str:
    if isinstance(response, str):
        return response
    if hasattr(response, "text") and response.text is not None:
        return response.text
    if hasattr(response, "output") and response.output is not None:
        output = response.output
        if isinstance(output, str):
            return output
        if isinstance(output, dict) and "content" in output:
            return output["content"]
    if hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, "output"):
            return candidate.output
        if hasattr(candidate, "content"):
            return candidate.content
    if hasattr(response, "response") and response.response is not None:
        return str(response.response)
    raise RuntimeError("Unable to extract text from Gemini API response")


def _call_llm(prompt: str) -> str:
    genai, legacy = _configure_gemini()
    model = MODEL

    def _send_with_model(model_name: str):
        if legacy:
            if hasattr(genai, "generate_text"):
                return genai.generate_text(model=model_name, text=prompt, temperature=0.3)
            if hasattr(genai, "responses") and hasattr(genai.responses, "generate"):
                return genai.responses.generate(model=model_name, prompt=prompt, temperature=0.3)
            if hasattr(genai, "TextGeneration") and hasattr(genai.TextGeneration, "create"):
                return genai.TextGeneration.create(model=model_name, prompt=prompt, temperature=0.3)
            raise RuntimeError(
                "Unsupported legacy Gemini client API surface. Ensure google-generativeai is installed and up to date."
            )
        chat = genai.chats.create(model=model_name)
        return chat.send_message(prompt)

    try:
        response = _send_with_model(model)
    except Exception as exc:
        error_text = str(exc)
        if "NOT_FOUND" in error_text or "model" in error_text and "no longer available" in error_text.lower():
            for fallback in FALLBACK_MODELS:
                if fallback == model:
                    continue
                try:
                    response = _send_with_model(fallback)
                    model = fallback
                    break
                except Exception:
                    continue
            else:
                raise RuntimeError(
                    f"Gemini model '{MODEL}' is unavailable and no fallback model succeeded. "
                    "Check your account permissions or set RESUME_OPTIMIZER_MODEL to a supported Gemini model."
                ) from exc
        else:
            raise

    return _extract_gemini_text(response).strip()


def generate_suggestions(jd: StructuredJD, resume: StructuredResume, match: MatchResult) -> list[OptimizationSuggestion]:
    prompt = SUGGESTION_PROMPT.format(
        missing_required=match.missing_required_skills,
        missing_preferred=match.missing_preferred_skills,
        experience_gap=match.experience_gap_years,
        summary=resume.summary or "",
        bullets=[b for exp in resume.experience for b in exp.bullets],
    )
    raw = _call_llm(prompt)
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    items = json.loads(cleaned)
    return [OptimizationSuggestion(**item) for item in items]


def tailor_resume(jd: StructuredJD, resume: StructuredResume) -> tuple[str | None, dict[str, list[str]]]:
    prompt = TAILOR_PROMPT.format(
        jd_title=jd.title,
        required_skills=jd.required_skills,
        responsibilities=jd.responsibilities,
        summary=resume.summary or "",
        experience=json.dumps([e.model_dump() for e in resume.experience]),
    )
    raw = _call_llm(prompt)
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    parsed = json.loads(cleaned)
    return parsed.get("tailored_summary"), parsed.get("tailored_bullets", {})


def optimize(jd: StructuredJD, resume: StructuredResume, match: MatchResult) -> OptimizationResult:
    suggestions = generate_suggestions(jd, resume, match)
    tailored_summary, tailored_bullets = tailor_resume(jd, resume)
    return OptimizationResult(
        match_result=match,
        suggestions=suggestions,
        tailored_summary=tailored_summary,
        tailored_bullets=tailored_bullets,
    )
