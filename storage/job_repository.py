import sqlite3
import os
import hashlib
from dataclasses import asdict, is_dataclass

# Resolve project root from this file's location so DB path is always correct
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
        """Convert a dict or a dataclass into a standardized flat dict for SQLite insert."""
        if isinstance(job, dict):
            data = job
            predicted_role = data.get("predicted_role") or data.get("role") or "Unknown"
            match_score = data.get("match_score") or data.get("relevance_score") or 0.0
        else:
            # For objects, retrieve dynamic attributes directly before asdict strips them
            predicted_role = getattr(job, "predicted_role", getattr(job, "role", "Unknown")) or "Unknown"
            match_score = getattr(job, "match_score", getattr(job, "relevance_score", 0.0)) or 0.0
            data = asdict(job) if is_dataclass(job) else job.__dict__

        title = data.get("title") or data.get("job_title") or "Unknown Title"
        company = data.get("company") or data.get("company_name") or "Unknown Company"
        location = data.get("location") or ""
        url = data.get("url") or data.get("job_url") or ""

        # Generate a unique URL for jobs that share search-page URLs or have no URL
        if not url or "job-search" in url or "?q=" in url:
            h = hashlib.md5(f"{title}-{company}-{location}".encode("utf-8")).hexdigest()[:12]
            url = f"urn:job:{h}" if not url else f"{url}#jid-{h}"

        return {
            "title": title,
            "company": company,
            "description": data.get("description") or "",
            "source": data.get("source") or data.get("source_platform") or "Unknown",
            "url": url,
            "location": location,
            "posted_date": data.get("posted_date") or "",
            "predicted_role": predicted_role,
            "match_score": match_score,
            "min_salary": data.get("min_salary"),
            "max_salary": data.get("max_salary"),
            "currency": data.get("currency"),
            "job_type": data.get("job_type") or data.get("employment_type") or "Unknown"
        }

    def save(self, jobs):
        if not isinstance(jobs, list):
            jobs = [jobs]

        normalized_jobs = [self._normalize_job(job) for job in jobs]

        conn = self._get_connection()
        try:
            for job in normalized_jobs:
                # Use INSERT OR REPLACE to update existing entries by URL
                conn.execute("""
                    INSERT OR REPLACE INTO jobs (
                        title, company, description, source, url, location, 
                        posted_date, predicted_role, match_score, 
                        min_salary, max_salary, currency, job_type
                    ) VALUES (
                        :title, :company, :description, :source, :url, :location, 
                        :posted_date, :predicted_role, :match_score, 
                        :min_salary, :max_salary, :currency, :job_type
                    )
                """, job)
            conn.commit()
        finally:
            conn.close()

    def get_by_id(self, job_id):
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def load(self, role=None, limit=100):
        conn = self._get_connection()
        try:
            if role:
                cursor = conn.execute(
                    "SELECT * FROM jobs WHERE predicted_role = ? ORDER BY id DESC LIMIT ?",
                    (role, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM jobs ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def search(self, role=None, source=None, location=None, job_type=None, min_salary=None, offset=0, limit=20):
        conn = self._get_connection()
        try:
            query = "SELECT * FROM jobs WHERE 1=1"
            params = []

            if role:
                query += " AND predicted_role = ?"
                params.append(role)
            if source:
                query += " AND source = ?"
                params.append(source)
            if location:
                query += " AND location LIKE ?"
                params.append(f"%{location}%")
            if job_type:
                query += " AND job_type = ?"
                params.append(job_type)
            if min_salary is not None:
                query += " AND max_salary >= ?"
                params.append(min_salary)

            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_stats(self):
        conn = self._get_connection()
        try:
            stats = {}
            
            # Total jobs
            stats["total_jobs"] = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
            
            # Roles distribution
            roles = conn.execute("SELECT predicted_role, COUNT(*) as count FROM jobs GROUP BY predicted_role").fetchall()
            stats["roles_distribution"] = {row["predicted_role"]: row["count"] for row in roles}
            
            # Platform distribution
            platforms = conn.execute("SELECT source, COUNT(*) as count FROM jobs GROUP BY source").fetchall()
            stats["platforms_distribution"] = {row["source"]: row["count"] for row in platforms}
            
            # Job type distribution
            job_types = conn.execute("SELECT job_type, COUNT(*) as count FROM jobs GROUP BY job_type").fetchall()
            stats["job_types_distribution"] = {row["job_type"]: row["count"] for row in job_types}
            
            # Average salary per role (where salary data is available)
            salaries = conn.execute("""
                SELECT predicted_role, AVG((min_salary + max_salary)/2) as avg_sal 
                FROM jobs 
                WHERE min_salary IS NOT NULL AND max_salary IS NOT NULL
                GROUP BY predicted_role
            """).fetchall()
            stats["average_salary"] = {row["predicted_role"]: round(row["avg_sal"], 2) for row in salaries}
            
            return stats
        finally:
            conn.close()