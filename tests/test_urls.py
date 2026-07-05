from scraper.hays_scraper import HaysScraper

scraper = HaysScraper()

jobs = scraper.scrape_jobs(
    "Machine Learning Engineer"
)

for job in jobs:

    print("=" * 60)

    print(job.title)

    print(job.application_url)