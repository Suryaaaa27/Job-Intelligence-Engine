from scraper.hays_scraper import HaysScraper
from scraper.greenhouse_scraper import GreenhouseScraper


class ScraperFactory:

    @staticmethod
    def get_scrapers():

        return [

            HaysScraper(),

            GreenhouseScraper()

        ]