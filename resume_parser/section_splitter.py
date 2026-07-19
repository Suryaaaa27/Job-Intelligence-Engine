"""
Splits raw resume text into sections using header heuristics.
"""

import re

SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "profile", "objective", "career objective", "about me", "about"],
    "skills": ["skills", "technical skills", "core competencies", "skill set", "technologies", "tech stack", "competencies"],
    "experience": ["experience", "work experience", "professional experience", "employment history", "work history", "career history"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "project experience"],
    "education": ["education", "academic background", "educational background", "academics"],
    "certifications": ["certifications", "certificates", "licenses & certifications", "licenses and certifications", "credentials"],
}

ALIAS_TO_SECTION = {}
for canonical, aliases in SECTION_ALIASES.items():
    for alias in aliases:
        ALIAS_TO_SECTION[alias] = canonical


def _normalize_header_candidate(line: str) -> str:
    cleaned = re.sub(r"[:\-–—•|]+$", "", line.strip())
    cleaned = re.sub(r"^[:\-–—•|]+", "", cleaned)
    return cleaned.strip().lower()


def _looks_like_header(line: str) -> bool:
    words = line.strip().split()
    if not words or len(words) > 5:
        return False
    if re.search(r"[.,;]{1}\s", line):
        return False
    return True


def detect_section_for_line(line: str):
    if not _looks_like_header(line):
        return None
    normalized = _normalize_header_candidate(line)
    if normalized in ALIAS_TO_SECTION:
        return ALIAS_TO_SECTION[normalized]
    for alias, canonical in ALIAS_TO_SECTION.items():
        if normalized.startswith(alias):
            return canonical
    return None


def split_into_sections(lines: list) -> dict:
    sections = {"preamble": []}
    current_section = "preamble"

    for line in lines:
        detected = detect_section_for_line(line)
        if detected:
            current_section = detected
            sections.setdefault(current_section, [])
            continue
        sections.setdefault(current_section, []).append(line)

    return sections
