from resume.parser.parser import parse_resume
from resume.parser.adapter import parse_resume_to_structured_resume


class ResumeService:
    """Service responsible for parsing resumes into the standard schema."""

    @staticmethod
    def parse(file_path: str):
        parsed_resume = parse_resume(file_path)
        return parse_resume_to_structured_resume(parsed_resume)