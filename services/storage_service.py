from storage.job_repository import JobRepository


class StorageService:

    def __init__(self):

        self.repository = JobRepository()

    def save(self, jobs):

        self.repository.save(jobs)

    def load(self):

        return self.repository.load()