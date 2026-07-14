import hashlib
from dataclasses import asdict, is_dataclass
from datetime import datetime

from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError


class JobRepository:

    def __init__(
        self,
        mongo_uri="mongodb://127.0.0.1:27017",
        database_name="job_intelligence_engine",
        collection_name="jobs"
    ):

        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.collection_name = collection_name

        self.client = MongoClient(
            self.mongo_uri,
            serverSelectionTimeoutMS=5000
        )

        self.database = self.client[
            self.database_name
        ]

        self.collection = self.database[
            self.collection_name
        ]

        self._verify_connection()
        self._init_indexes()

    # ==========================================================
    # CONNECTION
    # ==========================================================

    def _verify_connection(self):

        self.client.admin.command(
            "ping"
        )

    # ==========================================================
    # INDEX INITIALIZATION
    # ==========================================================

    def _init_indexes(self):

        existing_indexes = (
            self.collection.index_information()
        )

        indexed_fields = {}

        for index_name, index_info in (
            existing_indexes.items()
        ):

            key_definition = tuple(
                index_info.get(
                    "key",
                    []
                )
            )

            indexed_fields[
                key_definition
            ] = {
                "name": index_name,
                "unique": index_info.get(
                    "unique",
                    False
                ),
                "sparse": index_info.get(
                    "sparse",
                    False
                )
            }

        required_indexes = [

            {
                "keys": (
                    ("job_hash", ASCENDING),
                ),
                "name": "job_hash_index",
                "unique": True
            },

            {
                "keys": (
                    ("title", ASCENDING),
                ),
                "name": "title_1"
            },

            {
                "keys": (
                    ("company", ASCENDING),
                ),
                "name": "company_1"
            },

            {
                "keys": (
                    ("source", ASCENDING),
                ),
                "name": "source_1"
            },

            {
                "keys": (
                    ("location", ASCENDING),
                ),
                "name": "location_1"
            },

            {
                "keys": (
                    ("predicted_role", ASCENDING),
                ),
                "name": "predicted_role_1"
            },

            {
                "keys": (
                    ("posted_date", ASCENDING),
                ),
                "name": "posted_date_index"
            }

        ]

        for index_config in required_indexes:

            keys = index_config[
                "keys"
            ]

            if keys in indexed_fields:
                continue

            create_options = {
                "name": index_config[
                    "name"
                ]
            }

            if index_config.get(
                "unique"
            ):

                create_options[
                    "unique"
                ] = True

            self.collection.create_index(
                list(keys),
                **create_options
            )

    # ==========================================================
    # JOB HASH
    # ==========================================================

    def _generate_job_hash(
        self,
        title,
        company,
        location,
        source,
        url
    ):

        fingerprint = "|".join(
            [
                str(title or "")
                .strip()
                .lower(),

                str(company or "")
                .strip()
                .lower(),

                str(location or "")
                .strip()
                .lower(),

                str(source or "")
                .strip()
                .lower(),

                str(url or "")
                .strip()
                .lower()
            ]
        )

        return hashlib.sha256(
            fingerprint.encode(
                "utf-8"
            )
        ).hexdigest()

    # ==========================================================
    # SAFE LIST NORMALIZATION
    # ==========================================================

    def _normalize_list(self, value):

        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        if isinstance(value, set):
            return list(value)

        if isinstance(value, str):

            value = value.strip()

            if not value:
                return []

            return [
                value
            ]

        return [
            value
        ]

    # ==========================================================
    # JOB NORMALIZATION
    # ==========================================================

    def _normalize_job(self, job):

        if is_dataclass(job):

            data = asdict(job)

        elif isinstance(job, dict):

            data = job.copy()

        else:

            data = job.__dict__.copy()

        # ======================================================
        # DOMAIN MODEL → PERSISTENCE MODEL
        # ======================================================

        title = (
            data.get("title")
            or data.get("job_title")
            or ""
        )

        company = (
            data.get("company")
            or data.get("company_name")
            or ""
        )

        source = (
            data.get("source")
            or data.get("source_platform")
            or ""
        )

        url = (
            data.get("url")
            or data.get("job_url")
            or ""
        )

        application_url = (
            data.get("application_url")
            or data.get("apply_url")
            or url
        )

        location = (
            data.get("location")
            or ""
        )

        job_id = (
            data.get("job_id")
            or ""
        )

        employment_type = (
            data.get("employment_type")
            or data.get("job_type")
            or ""
        )

        salary_period = (
            data.get("salary_period")
            or data.get("salary_frequency")
            or ""
        )

        skills = self._normalize_list(
            data.get("skills")
            or data.get(
                "extracted_skills"
            )
        )

        responsibilities = (
            self._normalize_list(
                data.get(
                    "responsibilities"
                )
            )
        )

        education = self._normalize_list(
            data.get("education")
        )

        requirements = self._normalize_list(
            data.get("requirements")
        )

        benefits = self._normalize_list(
            data.get("benefits")
        )

        # ======================================================
        # JOB HASH
        # ======================================================

        job_hash = (
            data.get("job_hash")
            or self._generate_job_hash(
                title,
                company,
                location,
                source,
                url
            )
        )

        now = datetime.utcnow()

        # ======================================================
        # FINAL MONGODB DOCUMENT
        # ======================================================

        return {

            "job_hash": job_hash,

            "job_id": str(job_id),

            "title": title,

            "company": company,

            "company_website": (
                data.get(
                    "company_website"
                )
                or ""
            ),

            "description": (
                data.get("description")
                or ""
            ),

            "source": source,

            "url": url,

            "application_url": application_url,

            "location": location,

            "country": (
                data.get("country")
                or ""
            ),

            "state": (
                data.get("state")
                or ""
            ),

            "city": (
                data.get("city")
                or ""
            ),

            "workplace_type": (
                data.get(
                    "workplace_type"
                )
                or ""
            ),

            "employment_type": employment_type,

            # Backward compatibility
            "job_type": employment_type,

            "salary": (
                data.get("salary")
                or ""
            ),

            "min_salary": (
                data.get("min_salary")
            ),

            "max_salary": (
                data.get("max_salary")
            ),

            "currency": (
                data.get("currency")
            ),

            "salary_period": salary_period,

            "posted_date": (
                data.get("posted_date")
                or ""
            ),

            "skills": skills,

            "responsibilities": responsibilities,

            "experience": (
                data.get("experience")
                or ""
            ),

            "education": education,

            "requirements": requirements,

            "benefits": benefits,

            "predicted_role": (
                data.get(
                    "predicted_role"
                )
            ),

            "role_predictions": (
                self._normalize_list(
                    data.get(
                        "role_predictions"
                    )
                )
            ),

            "match_score": (
                data.get("match_score")
            ),

            "relevance_scores": (
                data.get(
                    "relevance_scores"
                )
                or {}
            ),

            "scrape_session": (
                data.get(
                    "scrape_session"
                )
                or ""
            ),

            "created_at": (
                data.get("created_at")
                or now
            ),

            "updated_at": now

        }

    # ==========================================================
    # VALUE QUALITY CHECK
    # ==========================================================

    def _has_meaningful_value(self, value):

        if value is None:
            return False

        if isinstance(value, str):

            return bool(
                value.strip()
            )

        if isinstance(
            value,
            (
                list,
                tuple,
                set,
                dict
            )
        ):

            return bool(value)

        return True

    # ==========================================================
    # BUILD SAFE ENRICHMENT UPDATE
    # ==========================================================

    def _build_enrichment_update(
        self,
        existing_job,
        incoming_job
    ):

        update_fields = {}

        protected_fields = {
            "_id",
            "job_hash",
            "created_at"
        }

        for field, incoming_value in (
            incoming_job.items()
        ):

            if field in protected_fields:
                continue

            if field == "updated_at":
                continue

            existing_value = (
                existing_job.get(field)
            )

            incoming_has_value = (
                self._has_meaningful_value(
                    incoming_value
                )
            )

            existing_has_value = (
                self._has_meaningful_value(
                    existing_value
                )
            )

            # Never overwrite useful data with empty data.
            if not incoming_has_value:
                continue

            # Fill missing fields.
            if not existing_has_value:

                update_fields[
                    field
                ] = incoming_value

                continue

            # Replace changed scalar values with fresher data.
            if isinstance(
                incoming_value,
                (
                    str,
                    int,
                    float,
                    bool
                )
            ):

                if incoming_value != existing_value:

                    update_fields[
                        field
                    ] = incoming_value

                continue

            # Merge list values instead of destroying existing data.
            if isinstance(
                incoming_value,
                list
            ):

                existing_list = (
                    existing_value
                    if isinstance(
                        existing_value,
                        list
                    )
                    else []
                )

                merged_values = list(
                    dict.fromkeys(
                        existing_list
                        + incoming_value
                    )
                )

                if merged_values != existing_list:

                    update_fields[
                        field
                    ] = merged_values

                continue

            # Update dictionaries only when the incoming dictionary differs.
            if isinstance(
                incoming_value,
                dict
            ):

                existing_dict = (
                    existing_value
                    if isinstance(
                        existing_value,
                        dict
                    )
                    else {}
                )

                merged_dict = {
                    **existing_dict,
                    **incoming_value
                }

                if merged_dict != existing_dict:

                    update_fields[
                        field
                    ] = merged_dict

        return update_fields

    # ==========================================================
    # SAVE JOBS
    # ==========================================================

    def save_jobs(self, jobs):

        inserted = 0
        updated = 0
        duplicates = 0

        for job in jobs:

            normalized_job = (
                self._normalize_job(job)
            )

            job_hash = normalized_job[
                "job_hash"
            ]

            existing_job = (
                self.collection.find_one(
                    {
                        "job_hash": job_hash
                    }
                )
            )

            # ==================================================
            # NEW JOB
            # ==================================================

            if existing_job is None:

                try:

                    self.collection.insert_one(
                        normalized_job
                    )

                    inserted += 1

                except DuplicateKeyError:

                    # Another process may have inserted the job
                    # between find_one() and insert_one().
                    existing_job = (
                        self.collection.find_one(
                            {
                                "job_hash": job_hash
                            }
                        )
                    )

                    if existing_job is None:

                        duplicates += 1
                        continue

                    update_fields = (
                        self._build_enrichment_update(
                            existing_job,
                            normalized_job
                        )
                    )

                    if update_fields:

                        update_fields[
                            "updated_at"
                        ] = datetime.utcnow()

                        self.collection.update_one(
                            {
                                "_id": existing_job[
                                    "_id"
                                ]
                            },
                            {
                                "$set": update_fields
                            }
                        )

                        updated += 1

                    else:

                        duplicates += 1

                continue

            # ==================================================
            # EXISTING JOB — SAFE ENRICHMENT
            # ==================================================

            update_fields = (
                self._build_enrichment_update(
                    existing_job,
                    normalized_job
                )
            )

            if not update_fields:

                duplicates += 1
                continue

            update_fields[
                "updated_at"
            ] = datetime.utcnow()

            result = self.collection.update_one(
                {
                    "_id": existing_job[
                        "_id"
                    ]
                },
                {
                    "$set": update_fields
                }
            )

            if result.modified_count > 0:

                updated += 1

            else:

                duplicates += 1

        return {

            "inserted": inserted,

            "updated": updated,

            "duplicates": duplicates

        }

    # ==========================================================
    # BACKWARD COMPATIBILITY
    # ==========================================================

    def save(self, jobs):

        if isinstance(jobs, list):

            return self.save_jobs(
                jobs
            )

        return self.save_jobs(
            [
                jobs
            ]
        )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def get_statistics(self):

        total_jobs = (
            self.collection.count_documents({})
        )

        return {
            "total_jobs": total_jobs
        }

    def get_stats(self):

        return self.get_statistics()

    # ==========================================================
    # JOB RETRIEVAL
    # ==========================================================

    def get_by_id(self, job_id):

        job = self.collection.find_one(
            {
                "job_id": str(job_id)
            }
        )

        if job:

            job["_id"] = str(
                job["_id"]
            )

        return job

    def load(self):

        jobs = []

        cursor = self.collection.find({})

        for job in cursor:

            job["_id"] = str(
                job["_id"]
            )

            jobs.append(job)

        return jobs

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def close(self):

        self.client.close()

    def __del__(self):

        try:

            self.close()

        except Exception:

            pass