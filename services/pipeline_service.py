from services.search_service import SearchService
from services.scraping_service import ScrapingService
from services.classification_service import ClassificationService
from services.storage_service import StorageService
from preprocessing.cleaner import clean_job
from preprocessing.deduplicator import remove_duplicates

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

        self.logger.info(f"{len(all_jobs)} raw jobs collected")

        # Stage 1: Clean all raw scraped jobs (HTML strip, salary extraction, job type detection)
        all_jobs = [clean_job(job) for job in all_jobs]
        self.logger.info(f"{len(all_jobs)} jobs after cleaning")

        # Stage 2: Deduplicate (fuzzy title + description Jaccard matching)
        all_jobs = remove_duplicates(all_jobs)
        self.logger.info(f"{len(all_jobs)} unique jobs after deduplication")

        # Stage 3: Classify roles
        jobs = self.classification_service.classify(all_jobs)

        # Stage 4: Persist to database
        self.storage_service.save(jobs)

        self.logger.info(f"Pipeline Finished — {len(jobs)} jobs saved")

        return jobs