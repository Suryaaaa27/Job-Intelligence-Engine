from abc import ABC, abstractmethod
from typing import List

from scraper.models import Job


class BaseScraper(ABC):

    @abstractmethod
    def scrape_jobs(self, query: str) -> List[Job]:
        """
        Search a platform and return standardized Job objects.
        """
        pass

    @abstractmethod
    def extract_job_details(self, page, job: Job) -> Job:
        """
        Enrich a Job object with full job details.
        """
        pass