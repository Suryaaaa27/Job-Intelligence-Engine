from abc import ABC, abstractmethod


class BaseDetailScraper(ABC):

    @abstractmethod
    def extract(self, job):

        """
        Accepts Job object

        Returns enriched Job object
        """

        pass