import sys
import os

# 1. Get the directory where run_engine.py is sitting
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Force Python to add this directory to its search path before doing anything else
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# NOW you can safely do your imports, and Python will find them every single time
import json
import time
from scraper.unified_scraper import UnifiedScraper
from preprocessing.cleaner import clean_job


def main():
    target_roles = [
        "Software Engineer",
        "Data Analyst",
        "Product Manager",
        "DevOps Engineer",
        "Data Scientist"
    ]

    output_file = "data/processed_jobs.json"
    scraper_runner = UnifiedScraper()

    for index, query in enumerate(target_roles, start=1):
        print(f"\n=======================================================")
        print(f"PROCESSING ROLE {index}/{len(target_roles)}: {query}")
        print(f"=======================================================")

        print(f"--- 1. Running Live Scrapers for '{query}' ---")
        raw_listings = scraper_runner.scrape_jobs(query)

        print(f"\n--- 2. Processing and Cleaning {len(raw_listings)} New Records ---")
        cleaned_jobs = [clean_job(job) for job in raw_listings]

        # --- 3. Historical Master Archiving (Yesterday's Basic Logic) ---
        existing_jobs = []
        if os.path.exists(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    existing_jobs = json.load(f)
                    print(f"-> Loaded {len(existing_jobs)} existing jobs from master archive.")
            except Exception as e:
                print(f"-> Starting fresh archive: {e}")

        # Basic duplication prevention by checking unique URLs
        existing_urls = {job.get("url") for job in existing_jobs if job.get("url")}

        new_count = 0
        for job in cleaned_jobs:
            if job.get("url") not in existing_urls:
                existing_jobs.append(job)
                new_count += 1

        print(f"-> Added {new_count} new jobs.")

        # Save back out
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(existing_jobs, f, indent=4, ensure_ascii=False)

        if index < len(target_roles):
            time.sleep(5)


if __name__ == "__main__":
    main()