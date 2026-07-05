from scraper.hays_scraper import HaysScraper
# from scraper.linkedin_scraper import LinkedInScraper
# from scraper.greenhouse_scraper import GreenhouseScraper
from scraper.scraper_factory import ScraperFactory

class UnifiedScraper:

    def __init__(self):

        self.scrapers = ScraperFactory.get_scrapers()

    def scrape_jobs(self, query):

        jobs = []

        for scraper in self.scrapers:

            try:

                results = scraper.scrape_jobs(query)

                jobs.extend(results)

            except Exception as e:

                print(
                    f"{scraper.__class__.__name__}: {e}"
                )

        return jobs