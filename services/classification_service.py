from taxonomy.role_manager import RoleManager


class ClassificationService:

    def __init__(self):

        self.role_manager = RoleManager()

    def classify(self, jobs):

        for job in jobs:

            result = self.role_manager.classify_job(
                job.title,
                job.description
            )

            job.predicted_role = result["predicted_role"]

        return jobs