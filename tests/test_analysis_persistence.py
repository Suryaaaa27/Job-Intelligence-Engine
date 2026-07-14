import json

from analysis.analyzer import JDAnalyzer

from storage.job_repository import JobRepository


print()

print("=" * 80)

print(
    "JD ANALYSIS PERSISTENCE TEST"
)

print("=" * 80)


# ============================================================
# TEST JOB
# ============================================================

job = {

    "job_id": "ANALYZER_TEST_001",

    "title": (
        "Machine Learning Engineer"
    ),

    "company": "Hays",

    "description": (
        "Required Skills and Experience:\n"
        "Must have 5+ years of experience "
        "in Python, TensorFlow and SQL.\n"
        "Nice to have:\n"
        "Experience with Docker and AWS "
        "is a plus.\n"
        "Responsibilities:\n"
        "- Build machine learning pipelines\n"
        "- Develop RAG systems\n"
        "Bachelor degree in Computer Science.\n"
        "Hybrid working available."
    ),

    "source": "Hays",

    "url": (
        "https://example.com/"
        "analysis-persistence-test"
    ),

    "application_url": (
        "https://example.com/"
        "analysis-persistence-test/apply"
    ),

    "location": "Sheffield",

    "country": "GB",

    "city": "Sheffield",

    "workplace_type": "Hybrid",

    "employment_type": "Contractor",

    "skills": [

        "Python",

        "TensorFlow",

        "SQL",

        "Docker",

        "AWS"

    ],

    "responsibilities": [

        "Build machine learning pipelines",

        "Develop RAG systems"

    ],

    "experience": "5+ years"

}


# ============================================================
# INITIALIZE ANALYZER
# ============================================================

analyzer = JDAnalyzer()


# ============================================================
# ANALYZE JOB
# ============================================================

analysis = analyzer.analyze(
    job
)


print()

print("=" * 80)

print(
    "ANALYZER OUTPUT"
)

print("=" * 80)


print(
    json.dumps(
        analysis,
        indent=4,
        ensure_ascii=False,
        default=str
    )
)


# ============================================================
# ATTACH ANALYSIS TO JOB
# ============================================================

job[
    "analysis"
] = analysis


# ============================================================
# INITIALIZE REPOSITORY
# ============================================================

repository = JobRepository()


# ============================================================
# SAVE ANALYZED JOB
# ============================================================

result = repository.save_jobs(
    [
        job
    ]
)


print()

print("=" * 80)

print(
    "REPOSITORY SAVE RESULT"
)

print("=" * 80)


print(
    json.dumps(
        result,
        indent=4,
        default=str
    )
)


# ============================================================
# RETRIEVE ANALYSIS
# ============================================================

stored_analysis = (
    repository.get_analysis(
        "ANALYZER_TEST_001"
    )
)


print()

print("=" * 80)

print(
    "STORED ANALYSIS"
)

print("=" * 80)


print(
    json.dumps(
        stored_analysis,
        indent=4,
        ensure_ascii=False,
        default=str
    )
)


# ============================================================
# VALIDATION
# ============================================================

print()

print("=" * 80)

print(
    "VALIDATING ANALYSIS PERSISTENCE"
)

print("=" * 80)


assert stored_analysis is not None

print(
    "✓ Analysis stored in MongoDB"
)


assert (
    stored_analysis[
        "required_experience"
    ]
    == "5+ years"
)

print(
    "✓ Experience persisted"
)


assert (
    stored_analysis[
        "required_education"
    ]
    == "Bachelor's Degree"
)

print(
    "✓ Education persisted"
)


assert (
    stored_analysis[
        "seniority"
    ]
    == "Senior"
)

print(
    "✓ Seniority persisted"
)


assert (
    "Python"
    in stored_analysis[
        "required_skills"
    ]
)

print(
    "✓ Required skills persisted"
)


assert (
    "Docker"
    in stored_analysis[
        "preferred_skills"
    ]
)

print(
    "✓ Preferred skills persisted"
)


assert (
    "Machine Learning Engineer"
    in stored_analysis[
        "ats_keywords"
    ]
)

print(
    "✓ ATS keywords persisted"
)


assert (
    stored_analysis[
        "analysis_completeness_score"
    ]
    > 0
)

print(
    "✓ Completeness score persisted"
)


# ============================================================
# STATISTICS
# ============================================================

statistics = (
    repository.get_statistics()
)


print()

print("=" * 80)

print(
    "REPOSITORY STATISTICS"
)

print("=" * 80)


print(
    json.dumps(
        statistics,
        indent=4,
        default=str
    )
)


assert (
    statistics[
        "analyzed_jobs"
    ]
    >= 1
)

print(
    "✓ Analyzed job statistics passed"
)


# ============================================================
# FINAL RESULT
# ============================================================

print()

print("=" * 80)

print(
    "ALL ANALYSIS PERSISTENCE TESTS PASSED"
)

print("=" * 80)


repository.close()