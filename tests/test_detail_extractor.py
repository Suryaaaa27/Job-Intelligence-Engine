import json

from scraper.hays_scraper import HaysScraper
from preprocessing.cleaner import clean_job
from analysis.job_detail_extractor import JobDetailExtractor


scraper = HaysScraper()

extractor = JobDetailExtractor()


jobs = scraper.scrape_jobs(
    "Machine Learning Engineer"
)


if not jobs:

    print("NO JOBS FOUND")

    raise SystemExit


raw_job = jobs[0]

cleaned_job = clean_job(
    raw_job
)

enriched_job = extractor.enrich(
    cleaned_job
)


print()
print("=" * 80)
print("DETAIL EXTRACTION RESULT")
print("=" * 80)

print(
    json.dumps(
        enriched_job,
        indent=4,
        ensure_ascii=False,
        default=str,
    )
)

print("=" * 80)