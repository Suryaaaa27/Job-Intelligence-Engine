from scraper.unified_scraper import UnifiedScraper

scraper = UnifiedScraper()

jobs = scraper.scrape_jobs(
    "Machine Learning Engineer"
)

print()

print(f"TOTAL JOBS : {len(jobs)}")

print()

for job in jobs:

    print("=" * 60)

    print(job.job_title)

    print(job.location)

    print(job.source_platform)