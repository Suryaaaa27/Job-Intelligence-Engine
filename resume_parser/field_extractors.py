"""
Field-level extractors for resume sections.
"""

import re

try:
    from .schema import ContactInfo, Experience, Project, Education, Certification
    from .skills_db import find_skills_in_text
except ImportError:  # pragma: no cover - support direct script execution
    from schema import ContactInfo, Experience, Project, Education, Certification
    from skills_db import find_skills_in_text

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/\S+", re.IGNORECASE)
GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/\S+", re.IGNORECASE)
GENERIC_URL_RE = re.compile(r"(https?://)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(\/\S*)?")

DATE_RANGE_RE = re.compile(
    r"(?P<start>(?:[A-Za-z]{3,9}\.??\s+\d{4})|\d{1,2}/\d{4}|\d{4})"
    r"\s*(?:-|–|—|to)\s*"
    r"(?P<end>(?:[A-Za-z]{3,9}\.??\s+\d{4})|\d{1,2}/\d{4}|\d{4}|[Pp]resent|[Cc]urrent)",
    re.IGNORECASE,
)


def extract_contact_info(preamble_lines: list) -> ContactInfo:
    contact = ContactInfo()
    full_text = " ".join(preamble_lines)

    email_match = EMAIL_RE.search(full_text)
    if email_match:
        contact.email = email_match.group(0)

    phone_match = PHONE_RE.search(full_text)
    if phone_match:
        contact.phone = phone_match.group(0).strip()

    linkedin_match = LINKEDIN_RE.search(full_text)
    if linkedin_match:
        contact.linkedin = linkedin_match.group(0)

    github_match = GITHUB_RE.search(full_text)
    if github_match:
        contact.github = github_match.group(0)

    for line in preamble_lines[:3]:
        if EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        if LINKEDIN_RE.search(line) or GITHUB_RE.search(line):
            continue
        words = line.split()
        if 1 <= len(words) <= 5 and all(w[0].isupper() or not w[0].isalpha() for w in words if w):
            contact.full_name = line.strip()
            break

    for line in preamble_lines[:6]:
        if line == contact.full_name:
            continue
        if "," in line and not any(ch.isdigit() for ch in line) and len(line.split()) <= 6:
            if not EMAIL_RE.search(line) and not LINKEDIN_RE.search(line):
                contact.location = line.strip()
                break

    return contact


def extract_summary(summary_lines: list) -> str:
    if not summary_lines:
        return None
    return " ".join(summary_lines).strip()


def extract_skills(skills_lines: list) -> list:
    if not skills_lines:
        return []

    cleaned = []
    for line in skills_lines:
        delabeled = re.sub(r"^[A-Za-z][A-Za-z /]{0,30}:\s*", "", line)
        tokens = re.split(r"[,•|/]|\s{2,}", delabeled)
        cleaned.extend(t.strip() for t in tokens if t.strip() and len(t.strip()) <= 40)

    seen = set()
    result = []
    for token in cleaned:
        key = token.lower()
        if key not in seen:
            seen.add(key)
            result.append(token)

    full_text = " ".join(skills_lines)
    for skill in find_skills_in_text(full_text):
        if skill not in seen:
            seen.add(skill)
            result.append(skill)

    return result

LABEL_LINE_RE = re.compile(r"^\s*(GPA|Phone|Email|Location)\b", re.IGNORECASE)


def _is_date_only_line(line: str) -> bool:
    stripped = line.strip()
    match = DATE_RANGE_RE.fullmatch(stripped)
    return match is not None


def _merge_standalone_date_lines(lines: list) -> list:
    merged = []
    i = 0
    while i < len(lines):
        if _is_date_only_line(lines[i]) and i + 1 < len(lines):
            merged.append(f"{lines[i]} | {lines[i + 1]}")
            i += 2
        else:
            merged.append(lines[i])
            i += 1
    return merged


def _looks_like_entry_header(line: str) -> bool:
    if LABEL_LINE_RE.match(line):
        return False
    if DATE_RANGE_RE.search(line):
        remainder = DATE_RANGE_RE.sub("", line).strip(" |,-–—")
        if LABEL_LINE_RE.match(remainder):
            return False
        return True
    if line.strip().startswith(("•", "-", "*", "◦")):
        return False
    words = [w for w in line.split() if any(ch.isalpha() for ch in w)]
    if not words or len(words) > 8:
        return False
    capitalized = sum(1 for w in words if w[:1].isupper())
    return len(words) >= 2 and capitalized >= len(words) - 1


def _group_lines_into_entries(lines: list) -> list:
    lines = _merge_standalone_date_lines(lines)
    entries = []
    current = []
    for line in lines:
        if _looks_like_entry_header(line) and current:
            entries.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        entries.append(current)
    return entries


def extract_experience(experience_lines: list) -> list:
    entries = _group_lines_into_entries(experience_lines)
    results = []
    for entry_lines in entries:
        exp = Experience()
        header_line = entry_lines[0]

        date_match = DATE_RANGE_RE.search(header_line)
        if date_match:
            exp.start_date = date_match.group("start")
            end = date_match.group("end")
            if end.lower() in ("present", "current"):
                exp.is_current = True
                exp.end_date = "Present"
            else:
                exp.end_date = end
            header_line = DATE_RANGE_RE.sub("", header_line).strip(" ,|-–—")

        parts = re.split(r"\s*(?:,|@|\bat\b|-|–|—|\|)\s*", header_line, maxsplit=1)
        if len(parts) == 2:
            exp.job_title, exp.company = parts[0].strip(), parts[1].strip()
        elif header_line.strip():
            exp.job_title = header_line.strip()

        bullets = [line.lstrip("•-*◦ ").strip() for line in entry_lines[1:] if line.strip()]
        exp.bullets = bullets
        exp.raw_text = "\n".join(entry_lines)
        results.append(exp)
    return results


def extract_projects(project_lines: list) -> list:
    entries = _group_lines_into_entries(project_lines)
    results = []
    for entry_lines in entries:
        proj = Project()
        header_line = entry_lines[0]
        url_match = GENERIC_URL_RE.search(header_line)
        if url_match:
            proj.link = url_match.group(0)
            header_line = GENERIC_URL_RE.sub("", header_line).strip(" ,|-–—")

        parts = header_line.split("|")
        proj.name = parts[0].strip() if parts else header_line.strip()
        if len(parts) > 1:
            proj.technologies = [t.strip() for t in parts[1].split(",") if t.strip()]

        bullets = [line.lstrip("•-*◦ ").strip() for line in entry_lines[1:] if line.strip()]
        proj.bullets = bullets
        if not proj.technologies:
            proj.technologies = find_skills_in_text(" ".join(entry_lines))
        proj.description = " ".join(bullets) if bullets else None
        proj.raw_text = "\n".join(entry_lines)
        results.append(proj)
    return results

GPA_RE = re.compile(r"\bGPA\b\s*[:\-]?\s*([\d.]+\s*/?\s*[\d.]*)", re.IGNORECASE)


def extract_education(education_lines: list) -> list:
    entries = _group_lines_into_entries(education_lines)
    results = []
    for entry_lines in entries:
        edu = Education()
        header_line = entry_lines[0]
        full_text = " ".join(entry_lines)

        date_match = DATE_RANGE_RE.search(full_text)
        if date_match:
            edu.start_date = date_match.group("start")
            edu.end_date = date_match.group("end")

        gpa_match = GPA_RE.search(full_text)
        if gpa_match:
            edu.gpa = gpa_match.group(1).strip()

        header_clean = DATE_RANGE_RE.sub("", header_line).strip(" ,|-–—")
        parts = re.split(r"\s*[,|]\s*", header_clean, maxsplit=1)
        if len(parts) == 2:
            edu.degree = parts[0].strip()
            edu.institution = parts[1].strip(" ,|-–—")
        elif header_clean.strip():
            edu.institution = header_clean.strip()

        edu.raw_text = "\n".join(entry_lines)
        results.append(edu)
    return results


def extract_certifications(cert_lines: list) -> list:
    results = []
    for line in cert_lines:
        if not line.strip():
            continue
        cert = Certification()
        date_match = DATE_RANGE_RE.search(line) or re.search(r"\b(19|20)\d{2}\b", line)
        if date_match:
            cert.date = date_match.group(0)
        line_no_date = DATE_RANGE_RE.sub("", line).strip(" ,|-–—")
        if line_no_date:
            cert.name = line_no_date
        cert.raw_text = line
        results.append(cert)
    return results
