from scraper.hays_scraper import HaysScraper
from search.query_manager import QueryManager
from storage.job_repository import JobRepository
from utils.logger import JobLogger


class JobPipeline:

    def __init__(self):

        self.logger = JobLogger.get_logger()

        self.scraper = HaysScraper()

        self.query_manager = QueryManager()

        self.repository = JobRepository()

    def run(self, role):

        self.logger.info(

            f"Starting pipeline for {role}"

        )

        jobs = []

        queries = self.query_manager.get_queries(

            role

        )

        for query in queries:

            self.logger.info(

                f"Searching: {query}"

            )

            result = self.scraper.scrape_jobs(

                query

            )

            jobs.extend(result)

        self.logger.info(

            f"Collected {len(jobs)} jobs"

        )

        self.repository.save(jobs)

        self.logger.info(

            "Pipeline Finished"

        )

        return jobs