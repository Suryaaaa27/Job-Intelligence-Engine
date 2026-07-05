from scraper.hays_scraper import HaysScraper


class ScrapingService:

    def __init__(self):

        self.scraper = HaysScraper()

    def search_jobs(self, query):

        return self.scraper.scrape_jobs(query)