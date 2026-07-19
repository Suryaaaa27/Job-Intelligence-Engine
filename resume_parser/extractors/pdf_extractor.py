"""Extracts raw text from PDF resumes."""

try:
    import pdfplumber
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    pdfplumber = None


def extract_text_from_pdf(file_path: str) -> str:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is required to parse PDF resumes. Install resume_parser/requirements.txt")

    text_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n\n".join(text_chunks)


def extract_lines_from_pdf(file_path: str) -> list:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is required to parse PDF resumes. Install resume_parser/requirements.txt")

    lines = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            for line in page_text.split("\n"):
                stripped = line.strip()
                if stripped:
                    lines.append(stripped)
    return lines
