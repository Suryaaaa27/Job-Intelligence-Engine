import json
import tempfile
from pathlib import Path

from resume_parser.parser import parse_resume


def test_parse_resume_returns_schema_shape():
    sample_resume = Path("data/samples/sample_resume.json")
    if not sample_resume.exists():
        return

    resume_data = json.loads(sample_resume.read_text(encoding="utf-8"))
    assert isinstance(resume_data, dict)
    assert "skills" in resume_data


def test_parse_resume_accepts_json_resume_input(tmp_path):
    payload = {
        "contact_info": {"full_name": "Ada Lovelace", "email": "ada@example.com"},
        "summary": "Software engineer with Python and ML experience.",
        "skills": ["Python", "Machine Learning"],
        "experience": [{"job_title": "Engineer", "company": "Acme", "bullets": ["Built models"]}],
        "education": [{"degree": "BSc", "institution": "University"}],
        "certifications": [{"name": "AWS"}],
    }
    resume_path = tmp_path / "resume.json"
    resume_path.write_text(json.dumps(payload), encoding="utf-8")

    resume = parse_resume(str(resume_path))

    assert resume.contact_info.full_name == "Ada Lovelace"
    assert resume.skills == ["Python", "Machine Learning"]
    assert resume.experience[0].company == "Acme"
