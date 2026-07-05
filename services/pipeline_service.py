from services.search_service import SearchService
from services.scraping_service import ScrapingService
from services.classification_service import ClassificationService
from services.storage_service import StorageService

from utils.logger import JobLogger


class PipelineService:

    def __init__(self):

        self.logger = JobLogger.get_logger()

        self.search_service = SearchService()

        self.scraping_service = ScrapingService()

        self.classification_service = ClassificationService()

        self.storage_service = StorageService()

    def run(self, role):

        self.logger.info(f"Pipeline Started : {role}")

        queries = self.search_service.get_queries(role)

        all_jobs = []

        for query in queries:

            self.logger.info(f"Searching : {query}")

            jobs = self.scraping_service.search_jobs(query)

            all_jobs.extend(jobs)

        self.logger.info(f"{len(all_jobs)} Jobs Collected")

        jobs = self.classification_service.classify(all_jobs)

        self.storage_service.save(jobs)

        self.logger.info("Pipeline Finished")

        return jobs