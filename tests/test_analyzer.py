import json

from analysis.analyzer import JDAnalyzer


def build_test_job():

    return {

        "title": "Machine Learning Engineer",

        "company": "Hays",

        "description": (
            "Required Skills and Experience:\n"
            "Must have 5+ years of experience "
            "in Python, TensorFlow and SQL.\n"
            "Nice to have:\n"
            "Experience with Docker and AWS is a plus.\n"
            "Responsibilities:\n"
            "- Build machine learning pipelines\n"
            "- Develop RAG systems\n"
            "Bachelor degree in Computer Science.\n"
            "Hybrid working available."
        ),

        "location": "Sheffield",

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


def run_test():

    print()

    print("=" * 80)

    print("JD ANALYZER TEST")

    print("=" * 80)

    analyzer = JDAnalyzer()

    job = build_test_job()

    result = analyzer.analyze(
        job
    )

    print()

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

    print()

    print("=" * 80)

    print("VALIDATING ANALYZER OUTPUT")

    print("=" * 80)

    assert (
        result["required_experience"]
        == "5+ years"
    )

    assert (
        result["required_education"]
        == "Bachelor's Degree"
    )

    assert (
        result["seniority"]
        == "Senior"
    )

    assert (
        "Python"
        in result["extracted_skills"]
    )

    assert (
        "TensorFlow"
        in result["extracted_skills"]
    )

    assert (
        "SQL"
        in result["required_skills"]
    )

    assert (
        "Docker"
        in result["preferred_skills"]
    )

    assert (
        "AWS"
        in result["preferred_skills"]
    )

    assert (
        "Build machine learning pipelines"
        in result["responsibilities"]
    )

    assert (
        "Develop RAG systems"
        in result["responsibilities"]
    )

    assert (
        result[
            "analysis_completeness_score"
        ] >= 80
    )

    assert isinstance(
        result["ats_keywords"],
        list
    )

    assert isinstance(
        result["tools_and_technologies"],
        list
    )

    assert isinstance(
        result["reasoning"],
        list
    )

    print()

    print(
        "✓ Experience extraction passed"
    )

    print(
        "✓ Education extraction passed"
    )

    print(
        "✓ Seniority detection passed"
    )

    print(
        "✓ Skill extraction passed"
    )

    print(
        "✓ Required skill classification passed"
    )

    print(
        "✓ Preferred skill classification passed"
    )

    print(
        "✓ Responsibility preservation passed"
    )

    print(
        "✓ Completeness scoring passed"
    )

    print(
        "✓ Analyzer schema validation passed"
    )

    print()

    print("=" * 80)

    print(
        "ALL ANALYZER TESTS PASSED"
    )

    print("=" * 80)


if __name__ == "__main__":

    run_test()