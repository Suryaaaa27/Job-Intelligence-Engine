from pipeline.resume_pipeline import ResumePipeline
from pipeline.matching_pipeline import MatchingPipeline

from services.ats_analyzer import ATSAnalyzer
from services.resume_optimizer import ResumeOptimizer

from schemas.resume_schema import StructuredJD

resume = ResumePipeline.execute("data/resume.pdf")

jd = StructuredJD(
    job_id="TEST-001",
    title="Machine Learning Engineer",

    company="OpenAI",
    location="Remote",

    required_skills=[
        "Python",
        "Machine Learning",
        "FastAPI",
        "Git",
    ],

    preferred_skills=[
        "Docker",
        "MongoDB",
    ],

    tools_technologies=[
        "VS Code",
    ],

    certifications=[],

    min_experience_years=1,

    education_requirements=[
        "Bachelor's Degree",
    ],

    responsibilities=[
        "Develop APIs",
        "Build ML models",
    ],

    qualifications=[
        "Problem Solving",
    ],
)

match = MatchingPipeline.execute(
    resume,
    jd,
)

ats_analyzer = ATSAnalyzer()

ats = ats_analyzer.analyze(
    resume,
    jd,
    match,
)

optimizer = ResumeOptimizer()

optimization = optimizer.optimize(
    resume,
    jd,
    match,
    ats,
)

print("=" * 80)
print("MATCH SCORE:", match.match_score)
print("ATS SCORE:", ats.overall_score)
print("=" * 80)

print("\nRecommendations:")
for r in ats.recommendations:
    print("-", r)

print("\nPriority Actions:")
for p in optimization.priority_actions:
    print("-", p)