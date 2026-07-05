class ScraperUtils:

    @staticmethod
    def deduplicate(jobs):

        unique = []

        seen = set()

        for job in jobs:

            key = (

                job.job_title.lower(),

                job.company_name.lower(),

                job.location.lower()

            )

            if key not in seen:

                seen.add(key)

                unique.append(job)

        return unique