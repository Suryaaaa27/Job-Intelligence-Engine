import sys
import os
# Ensure root is visible down inside the scraper package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.hays_scraper import HaysScraper
from scraper.greenhouse_scraper import GreenhouseScraper
from scraper.indeed_scraper import IndeedScraper
from scraper.linkedin_scraper import LinkedInScraper
class UnifiedScraper:
    def __init__(self):
        # Coordinates active targets side-by-side
        self.scrapers = [HaysScraper(), GreenhouseScraper(), IndeedScraper(), LinkedInScraper()]

    def scrape_jobs(self, query):
        jobs = []
        for scraper in self.scrapers:
            try:
                results = scraper.scrape_jobs(query)
                jobs.extend(results)
            except Exception as e:
                print(f"Error executing scraper {scraper.__class__.__name__}: {e}")
        return jobs