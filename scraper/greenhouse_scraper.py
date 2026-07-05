from scraper.base_scraper import BaseScraper

class GreenhouseScraper(BaseScraper):

    def scrape_jobs(self, query):
        raise NotImplementedError("Coming Soon")

    def extract_job_details(self, page, job):
        return job