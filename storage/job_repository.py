import sqlite3
import os
import hashlib
from dataclasses import asdict, is_dataclass

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_DB_PATH = os.path.join(_PROJECT_ROOT, "data", "jobs.db")


class JobRepository:

    def __init__(self, db_path=None):

        self.db_path = db_path or _DEFAULT_DB_PATH

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self._init_db()

    def _get_connection(self):

        conn = sqlite3.connect(self.db_path)

        conn.row_factory = sqlite3.Row

        return conn

    def _init_db(self):

        conn = self._get_connection()

        try:

            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    title TEXT,

                    company TEXT,

                    description TEXT,

                    source TEXT,

                    url TEXT UNIQUE,

                    location TEXT,

                    posted_date TEXT,

                    predicted_role TEXT,

                    match_score REAL,

                    min_salary REAL,

                    max_salary REAL,

                    currency TEXT,

                    job_type TEXT,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                )
            """)

            conn.commit()

        finally:

            conn.close()

    def _normalize_job(self, job):

        if is_dataclass(job):

            data = asdict(job)

        elif isinstance(job, dict):

            data = job

        else:

            data = job.__dict__

        title = data.get("title") or data.get("job_title")

        company = data.get("company") or data.get("company_name")

        location = data.get("location", "")

        url = data.get("url") or data.get("job_url")

        if not url:

            h = hashlib.md5(
                f"{title}{company}{location}".encode()
            ).hexdigest()[:12]

            url = f"job://{h}"

        return {

            "title": title,

            "company": company,

            "description": data.get("description", ""),

            "source": data.get("source") or data.get("source_platform"),

            "url": url,

            "location": location,

            "posted_date": data.get("posted_date"),

            "predicted_role": data.get("predicted_role"),

            "match_score": data.get("match_score"),

            "min_salary": data.get("min_salary"),

            "max_salary": data.get("max_salary"),

            "currency": data.get("currency"),

            "job_type": data.get("job_type")

        }

    # ==========================================================
    # New API (Compatible with ScrapingPipeline)
    # ==========================================================

    def save_jobs(self, jobs):

        inserted = 0

        duplicates = 0

        conn = self._get_connection()

        try:

            for job in jobs:

                job = self._normalize_job(job)

                try:

                    conn.execute("""

                        INSERT INTO jobs(

                            title,

                            company,

                            description,

                            source,

                            url,

                            location,

                            posted_date,

                            predicted_role,

                            match_score,

                            min_salary,

                            max_salary,

                            currency,

                            job_type

                        )

                        VALUES(

                            :title,

                            :company,

                            :description,

                            :source,

                            :url,

                            :location,

                            :posted_date,

                            :predicted_role,

                            :match_score,

                            :min_salary,

                            :max_salary,

                            :currency,

                            :job_type

                        )

                    """, job)

                    inserted += 1

                except sqlite3.IntegrityError:

                    duplicates += 1

            conn.commit()

        finally:

            conn.close()

        return {

            "inserted": inserted,

            "duplicates": duplicates

        }

    # ==========================================================
    # Old API (Backward Compatible)
    # ==========================================================

    def save(self, jobs):

        return self.save_jobs(jobs)

    def get_statistics(self):

        conn = self._get_connection()

        total = conn.execute(

            "SELECT COUNT(*) FROM jobs"

        ).fetchone()[0]

        conn.close()

        return {

            "total_jobs": total

        }

    def get_stats(self):

        return self.get_statistics()