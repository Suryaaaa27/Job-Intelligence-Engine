import json

from scraper.hays_scraper import HaysScraper
from preprocessing.cleaner import clean_job
from analysis.job_detail_extractor import JobDetailExtractor
from storage.job_repository import JobRepository


def main():

    print()
    print("=" * 80)
    print("REPOSITORY INTEGRATION TEST")
    print("=" * 80)

    scraper = HaysScraper()

    repository = JobRepository()

    detail_extractor = JobDetailExtractor()

    # ============================================================
    # STEP 1 — SCRAPE REAL HAYS JOBS
    # ============================================================

    jobs = scraper.scrape_jobs(
        "Machine Learning Engineer"
    )

    if not jobs:

        print("NO JOBS FOUND")

        return

    raw_job = jobs[0]

    print()
    print("RAW JOB")
    print("-" * 80)

    print(
        raw_job.job_title
    )

    # ============================================================
    # STEP 2 — CLEAN JOB
    # ============================================================

    cleaned_job = clean_job(
        raw_job
    )

    # ============================================================
    # STEP 3 — ENRICH JOB
    # ============================================================

    enriched_job = detail_extractor.enrich(
        cleaned_job
    )

    print()
    print("ENRICHED JOB")
    print("-" * 80)

    print(
        json.dumps(
            enriched_job,
            indent=4,
            ensure_ascii=False,
            default=str
        )
    )

    # ============================================================
    # STEP 4 — NORMALIZE FOR MONGODB
    # ============================================================

    normalized_job = repository._normalize_job(
        enriched_job
    )

    print()
    print("NORMALIZED MONGODB DOCUMENT")
    print("-" * 80)

    print(
        json.dumps(
            normalized_job,
            indent=4,
            ensure_ascii=False,
            default=str
        )
    )

    # ============================================================
    # STEP 5 — SAVE ONE JOB
    # ============================================================

    result = repository.save_jobs(
        [
            enriched_job
        ]
    )

    print()
    print("SAVE RESULT")
    print("-" * 80)

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # ============================================================
    # STEP 6 — VERIFY MONGODB DOCUMENT
    # ============================================================

    saved_job = repository.collection.find_one(
        {
            "job_hash": normalized_job[
                "job_hash"
            ]
        }
    )

    print()
    print("MONGODB SAVED DOCUMENT")
    print("-" * 80)

    if saved_job:

        saved_job["_id"] = str(
            saved_job["_id"]
        )

        print(
            json.dumps(
                saved_job,
                indent=4,
                ensure_ascii=False,
                default=str
            )
        )

    else:

        print(
            "DOCUMENT NOT FOUND"
        )

    print()
    print("=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":

    main()