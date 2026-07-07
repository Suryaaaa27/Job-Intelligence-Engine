from taxonomy.role_manager import RoleManager


class ClassificationService:

    def __init__(self):

        self.role_manager = RoleManager()

    def classify(self, jobs):

        for job in jobs:
            # After cleaning, jobs are dicts. Support both dicts and objects.
            if isinstance(job, dict):
                title = job.get("title") or job.get("job_title") or ""
                desc = job.get("description") or ""
            else:
                title = getattr(job, "title", getattr(job, "job_title", ""))
                desc = getattr(job, "description", "")

            result = self.role_manager.classify_job(title, desc)

            # Store both predicted_role AND match_score
            if isinstance(job, dict):
                job["predicted_role"] = result["predicted_role"]
                job["match_score"] = result["score"]
            else:
                job.predicted_role = result["predicted_role"]
                job.match_score = result["score"]

        return jobs