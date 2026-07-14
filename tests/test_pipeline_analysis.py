import json

from pipeline.scraping_pipeline import ScrapingPipeline
from scraper.hays_scraper import HaysScraper

print()

print("=" * 80)

print(
    "PIPELINE JD ANALYSIS INTEGRATION TEST"
)

print("=" * 80)


# ============================================================
# INITIALIZE PIPELINE
# ============================================================

pipeline = ScrapingPipeline()


# ============================================================
# SCRAPE REAL JOBS
# ============================================================

print()

print(
    "Scraping real Hays jobs..."
)


hays_scraper = HaysScraper()

raw_jobs = (
    hays_scraper.scrape_jobs(
        "Machine Learning Engineer"
    )
)


assert raw_jobs

print(
    f"✓ Scraped {len(raw_jobs)} jobs"
)


# ============================================================
# LIMIT TEST BATCH
# ============================================================

test_jobs = raw_jobs[:3]


print(
    f"✓ Limited integration test to "
    f"{len(test_jobs)} jobs"
)


# ============================================================
# CLEAN JOBS
# ============================================================

cleaned_jobs = [

    pipeline._job_to_dict(
        job
    )

    for job in test_jobs

]


from preprocessing.cleaner import clean_job


cleaned_jobs = [

    clean_job(
        job
    )

    for job in cleaned_jobs

]


assert len(cleaned_jobs) == 3


print(
    "✓ Cleaning stage passed"
)


# ============================================================
# DETAIL EXTRACTION
# ============================================================

(
    enriched_jobs,
    enrichment_failures

) = pipeline.enrich_jobs(
    cleaned_jobs
)


assert len(enriched_jobs) == 3


print(
    f"✓ Detail extraction passed "
    f"({enrichment_failures} failures)"
)


# ============================================================
# CLASSIFICATION
# ============================================================

classified_jobs = (
    pipeline.classifier.classify(
        enriched_jobs
    )
)


assert len(classified_jobs) == 3


print(
    "✓ Classification stage passed"
)


# ============================================================
# JD ANALYSIS
# ============================================================

(
    analyzed_jobs,
    analysis_failures

) = pipeline.analyze_jobs(
    classified_jobs
)


assert len(analyzed_jobs) == 3


print(
    f"✓ JD analysis stage passed "
    f"({analysis_failures} failures)"
)


# ============================================================
# VALIDATE ANALYSIS OBJECTS
# ============================================================

for index, job in enumerate(
    analyzed_jobs,
    start=1
):

    analysis = job.get(
        "analysis"
    )

    assert analysis

    assert (
        "required_experience"
        in analysis
    )

    assert (
        "required_skills"
        in analysis
    )

    assert (
        "preferred_skills"
        in analysis
    )

    assert (
        "ats_keywords"
        in analysis
    )

    assert (
        "seniority"
        in analysis
    )

    assert (
        "analysis_completeness_score"
        in analysis
    )

    print(
        f"✓ Job {index} analysis "
        f"schema validated"
    )


# ============================================================
# DISPLAY ANALYZED JOB
# ============================================================

print()

print("=" * 80)

print(
    "SAMPLE ANALYZED JOB"
)

print("=" * 80)


print(
    json.dumps(
        analyzed_jobs[0],
        indent=4,
        ensure_ascii=False,
        default=str
    )
)


# ============================================================
# STORE IN MONGODB
# ============================================================

result = (
    pipeline.repository.save_jobs(
        analyzed_jobs
    )
)


print()

print("=" * 80)

print(
    "MONGODB SAVE RESULT"
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
# VALIDATE DATABASE STATISTICS
# ============================================================

statistics = (
    pipeline.repository.get_statistics()
)


print()

print("=" * 80)

print(
    "DATABASE STATISTICS"
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
    statistics.get(
        "analyzed_jobs",
        0
    )
    >= 1
)


print(
    "✓ MongoDB analyzed job "
    "statistics validated"
)


# ============================================================
# FINAL RESULT
# ============================================================

print()

print("=" * 80)

print(
    "FULL PIPELINE JD ANALYSIS TEST PASSED"
)

print("=" * 80)


pipeline.repository.close()