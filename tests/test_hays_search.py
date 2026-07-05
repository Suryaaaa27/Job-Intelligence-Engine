from scraper.hays_scraper import HaysScraper

scraper = HaysScraper()

jobs = scraper.scrape_jobs(
    "Machine Learning Engineer"
)

print("\nRESULTS\n")

for idx, job in enumerate(jobs, start=1):

    print("=" * 60)

    print(f"Job #{idx}")

    print("Title:", job["title"])

    print("Location:", job["location"])

    print("Source:", job["source"])