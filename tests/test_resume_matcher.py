from services.resume_matcher import ResumeMatcher
from schemas.resume_schema import StructuredResume, StructuredJD

resume = StructuredResume(
    skills=[
        "Python",
        "Machine Learning",
        "Flask",
    ]
)

jd = StructuredJD(
    job_id="1",
    title="AI Engineer",
    required_skills=[
        "Python",
        "Machine Learning",
        "Docker",
    ],
    preferred_skills=[
        "Flask",
        "MongoDB",
    ],
)

result = ResumeMatcher.match(
    resume,
    jd,
)

print(result.model_dump_json(indent=2))