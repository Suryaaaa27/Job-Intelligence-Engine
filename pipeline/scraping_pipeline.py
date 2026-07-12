import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime

from scraper.unified_scraper import UnifiedScraper
from preprocessing.cleaner import clean_job
from services.classification_service import ClassificationService
from storage.job_repository import JobRepository


class ScrapingPipeline:

    def __init__(self):

        self.scraper = UnifiedScraper()

        self.classifier = ClassificationService()

        self.repository = JobRepository()

        self.raw_data_directory = "data/raw"

        os.makedirs(
            self.raw_data_directory,
            exist_ok=True
        )

    def _job_to_dict(self, job):

        if isinstance(job, dict):

            return job

        if is_dataclass(job):

            return asdict(job)

        return job.__dict__.copy()

    def save_raw_jobs(self, jobs, query):

        safe_query = (
            query
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"{safe_query}_{timestamp}.json"
        )

        filepath = os.path.join(
            self.raw_data_directory,
            filename
        )

        raw_data = [

            self._job_to_dict(job)

            for job in jobs

        ]

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                raw_data,
                file,
                indent=4,
                ensure_ascii=False,
                default=str
            )

        print(
            f"Raw Data Saved : {filepath}"
        )

        return filepath

    def run_query(self, query):

        print("\n" + "=" * 70)

        print(f"Searching : {query}")

        print("=" * 70)

        # ==================================================
        # STEP 1 — SCRAPE RAW JOBS
        # ==================================================

        raw_jobs = self.scraper.scrape_jobs(
            query
        )

        print(
            f"Raw Jobs : {len(raw_jobs)}"
        )

        # ==================================================
        # STEP 2 — ARCHIVE RAW SCRAPED DATA
        # ==================================================

        self.save_raw_jobs(
            raw_jobs,
            query
        )

        # ==================================================
        # STEP 3 — CLEAN DATA
        # ==================================================

        cleaned_jobs = [

            clean_job(job)

            for job in raw_jobs

        ]

        print(
            f"Cleaned Jobs : {len(cleaned_jobs)}"
        )

        # ==================================================
        # STEP 4 — CLASSIFY JOBS
        # ==================================================

        classified_jobs = self.classifier.classify(
            cleaned_jobs
        )

        # ==================================================
        # STEP 5 — STORE PROCESSED JOBS
        # ==================================================

        result = self.repository.save_jobs(
            classified_jobs
        )

        stats = self.repository.get_statistics()

        print()

        print(
            f"Inserted   : {result['inserted']}"
        )

        print(
            f"Duplicates : {result['duplicates']}"
        )

        print(
            f"Database   : {stats['total_jobs']}"
        )

        print()

        return result

    def run(self, queries):

        total_inserted = 0

        total_duplicates = 0

        for query in queries:

            result = self.run_query(
                query
            )

            total_inserted += result[
                "inserted"
            ]

            total_duplicates += result[
                "duplicates"
            ]

        print("\n" + "=" * 70)

        print(
            "SCRAPING SESSION COMPLETED"
        )

        print("=" * 70)

        print(
            f"Inserted   : {total_inserted}"
        )

        print(
            f"Duplicates : {total_duplicates}"
        )

        print("=" * 70)