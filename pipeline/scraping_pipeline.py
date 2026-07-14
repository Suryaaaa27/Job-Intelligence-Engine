import json
import os

from dataclasses import asdict, is_dataclass
from datetime import datetime

from scraper.unified_scraper import UnifiedScraper

from preprocessing.cleaner import clean_job

from services.classification_service import ClassificationService

from storage.job_repository import JobRepository

from analysis.job_detail_extractor import JobDetailExtractor


class ScrapingPipeline:

    def __init__(self):

        self.scraper = UnifiedScraper()

        self.classifier = ClassificationService()

        self.repository = JobRepository()

        self.detail_extractor = JobDetailExtractor()

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

    # ==========================================================
    # JOB DETAIL ENRICHMENT
    # ==========================================================

    def enrich_jobs(self, jobs):

        enriched_jobs = []

        enrichment_failures = 0

        for index, job in enumerate(
            jobs,
            start=1
        ):

            try:

                enriched_job = (
                    self.detail_extractor.enrich(
                        job
                    )
                )

                enriched_jobs.append(
                    enriched_job
                )

            except Exception as error:

                enrichment_failures += 1

                print(
                    f"[Detail Extraction Warning] "
                    f"Job {index} failed: {error}"
                )

                # Preserve cleaned job instead of
                # losing the complete pipeline run
                enriched_jobs.append(
                    job
                )

        return (
            enriched_jobs,
            enrichment_failures
        )

    # ==========================================================
    # RUN SINGLE QUERY
    # ==========================================================

    def run_query(self, query):

        print("\n" + "=" * 70)

        print(
            f"Searching : {query}"
        )

        print("=" * 70)

        # ==================================================
        # STEP 1 — SCRAPE RAW JOBS
        # ==================================================

        raw_jobs = (
            self.scraper.scrape_jobs(
                query
            )
        )

        print()

        print(
            f"Raw Jobs      : {len(raw_jobs)}"
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
            f"Cleaned Jobs  : {len(cleaned_jobs)}"
        )

        # ==================================================
        # STEP 4 — EXTRACT JOB DETAILS
        # ==================================================

        (
            enriched_jobs,
            enrichment_failures
        ) = self.enrich_jobs(
            cleaned_jobs
        )

        print(
            f"Enriched Jobs : {len(enriched_jobs)}"
        )

        print(
            f"Extract Fails : {enrichment_failures}"
        )

        # ==================================================
        # STEP 5 — CLASSIFY JOBS
        # ==================================================

        classified_jobs = (
            self.classifier.classify(
                enriched_jobs
            )
        )

        print(
            f"Classified    : {len(classified_jobs)}"
        )

        # ==================================================
        # STEP 6 — STORE / ENRICH PROCESSED JOBS
        # ==================================================

        result = (
            self.repository.save_jobs(
                classified_jobs
            )
        )

        stats = (
            self.repository.get_statistics()
        )

        inserted = result.get(
            "inserted",
            0
        )

        updated = result.get(
            "updated",
            0
        )

        duplicates = result.get(
            "duplicates",
            0
        )

        print()

        print("-" * 70)

        print(
            f"Inserted      : {inserted}"
        )

        print(
            f"Updated       : {updated}"
        )

        print(
            f"Duplicates    : {duplicates}"
        )

        print(
            f"Database      : {stats['total_jobs']}"
        )

        print("-" * 70)

        print()

        return {

            "inserted": inserted,

            "updated": updated,

            "duplicates": duplicates

        }

    # ==========================================================
    # RUN SCRAPING SESSION
    # ==========================================================

    def run(self, queries):

        total_inserted = 0

        total_updated = 0

        total_duplicates = 0

        failed_queries = 0

        for query in queries:

            try:

                result = self.run_query(
                    query
                )

                total_inserted += result.get(
                    "inserted",
                    0
                )

                total_updated += result.get(
                    "updated",
                    0
                )

                total_duplicates += result.get(
                    "duplicates",
                    0
                )

            except Exception as error:

                failed_queries += 1

                print()

                print(
                    f"[Pipeline Error] "
                    f"Query '{query}' failed: "
                    f"{error}"
                )

                print(
                    "Continuing with next query..."
                )

                print()

        # ==================================================
        # SESSION SUMMARY
        # ==================================================

        print("\n" + "=" * 70)

        print(
            "SCRAPING SESSION COMPLETED"
        )

        print("=" * 70)

        print(
            f"Inserted       : {total_inserted}"
        )

        print(
            f"Updated        : {total_updated}"
        )

        print(
            f"Duplicates     : {total_duplicates}"
        )

        print(
            f"Failed Queries : {failed_queries}"
        )

        print("=" * 70)

        return {

            "inserted": total_inserted,

            "updated": total_updated,

            "duplicates": total_duplicates,

            "failed_queries": failed_queries

        }