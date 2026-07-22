from services.resume_matcher import ResumeMatcher
from services.ats_analyzer import ATSAnalyzer

from tests.test_resume_matcher import resume, jd

match = ResumeMatcher.match(
    resume=resume,
    jd=jd,
)

report = ATSAnalyzer.analyze(
    resume=resume,
    jd=jd,
    match_result=match,
)

print(report.model_dump_json(indent=2))