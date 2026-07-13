import json
from dataclasses import asdict

from scraper.hays_scraper import HaysScraper


scraper = HaysScraper()

jobs = scraper.scrape_jobs(
    "Machine Learning Engineer"
)

print()
print(f"TOTAL JOBS : {len(jobs)}")
print()


# ============================================================
# FULL UNIFIED JOB INSPECTION
# ============================================================

if jobs:

    print("=" * 80)
    print("FULL UNIFIED JOB OBJECT")
    print("=" * 80)

    first_job = jobs[0]

    print(
        json.dumps(
            asdict(first_job),
            indent=4,
            ensure_ascii=False,
            default=str
        )
    )

    print("=" * 80)

else:

    print("NO JOBS FOUND")


# ============================================================
# SHORT JOB SUMMARY
# ============================================================

print()
print("JOB SUMMARY")
print()

for index, job in enumerate(jobs, start=1):

    print("=" * 60)

    print(f"JOB #{index}")

    print(f"Title    : {job.job_title}")

    print(f"Company  : {job.company_name}")

    print(f"Location : {job.location}")

    print(f"Source   : {job.source_platform}")