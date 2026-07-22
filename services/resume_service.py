from resume.parser.parser import parse_resume
from resume.parser.adapter import parse_resume_to_structured_resume

from services.resume_matcher import ResumeMatcher
from services.ats_analyzer import ATSAnalyzer
from services.resume_optimizer import ResumeOptimizer

from schemas.resume_schema import (
    StructuredJD,
    StructuredResume,
    ResumeAnalysisResult,
)


class ResumeService:
    """
    High-level orchestration service for the Resume Intelligence Engine.
    """

    def __init__(self):

        self.matcher = ResumeMatcher()

        self.ats = ATSAnalyzer()

        self.optimizer = ResumeOptimizer()

    @staticmethod
    def parse(
        file_path: str,
    ) -> StructuredResume:

        parsed = parse_resume(file_path)

        return parse_resume_to_structured_resume(parsed)

    def analyze(
        self,
        resume_path: str,
        jd: StructuredJD,
    ) -> ResumeAnalysisResult:

        # ----------------------------------------
        # Parse
        # ----------------------------------------

        resume = self.parse(resume_path)

        # ----------------------------------------
        # Match
        # ----------------------------------------

        match_result = self.matcher.match(
            resume,
            jd,
        )

        # ----------------------------------------
        # ATS
        # ----------------------------------------

        ats_report = self.ats.analyze(
            resume,
            jd,
            match_result,
        )

        # ----------------------------------------
        # Optimizer
        # ----------------------------------------

        optimization = self.optimizer.optimize(
            resume,
            jd,
            match_result,
            ats_report,
        )

        # ----------------------------------------
        # Final Response
        # ----------------------------------------

        return ResumeAnalysisResult(
            resume=resume,
            match_result=match_result,
            ats_report=ats_report,
            optimization=optimization,
        )