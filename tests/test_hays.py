from scraper.hays_scraper import HaysScraper

scraper = HaysScraper()

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