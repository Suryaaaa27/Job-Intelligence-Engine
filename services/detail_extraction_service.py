from scraper.detail.hays_detail_scraper import HaysDetailScraper


class DetailExtractionService:

    def __init__(self):

        self.scrapers = {

            "Hays": HaysDetailScraper()

        }

    def enrich(self, jobs):

        enriched = []

        for job in jobs:

            scraper = self.scrapers.get(

                job.source

            )

            if scraper:

                job = scraper.extract(job)

            enriched.append(job)

        return enriched