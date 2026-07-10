from scraper.unified_scraper import UnifiedScraper

from preprocessing.cleaner import clean_job

from services.classification_service import ClassificationService

from storage.job_repository import JobRepository


class ScrapingPipeline:

    def __init__(self):

        self.scraper = UnifiedScraper()

        self.classifier = ClassificationService()

        self.repository = JobRepository()

    def run_query(self, query):

        print("\n" + "=" * 70)

        print(f"Searching : {query}")

        print("=" * 70)

        raw_jobs = self.scraper.scrape_jobs(query)

        print(f"Raw Jobs : {len(raw_jobs)}")

        cleaned_jobs = [

            clean_job(job)

            for job in raw_jobs

        ]

        classified_jobs = self.classifier.classify(

            cleaned_jobs

        )

        result = self.repository.save_jobs(

            classified_jobs

        )

        stats = self.repository.get_statistics()

        print()

        print(f"Inserted   : {result['inserted']}")

        print(f"Duplicates : {result['duplicates']}")

        print(f"Database   : {stats['total_jobs']}")

        print()

        return result

    def run(self, queries):

        total_inserted = 0

        total_duplicates = 0

        for query in queries:

            result = self.run_query(query)

            total_inserted += result["inserted"]

            total_duplicates += result["duplicates"]

        print("\n" + "=" * 70)

        print("SCRAPING SESSION COMPLETED")

        print("=" * 70)

        print(f"Inserted   : {total_inserted}")

        print(f"Duplicates : {total_duplicates}")

        print("=" * 70)