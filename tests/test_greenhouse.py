from scraper.greenhouse_scraper import GreenhouseScraper

scraper = GreenhouseScraper()

jobs = scraper.scrape_jobs("AI")

print()

print(f"TOTAL JOBS : {len(jobs)}")

print()

for job in jobs[:20]:

    print("=" * 60)

    print(job.job_title)

    print(job.job_url)