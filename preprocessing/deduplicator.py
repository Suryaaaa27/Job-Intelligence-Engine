from scraper.models import Job


def remove_duplicates(jobs: list[Job]):

    unique_jobs = []
    seen = set()

    for job in jobs:

        # First preference: unique job URL
        if job.job_url:
            key = ("url", job.job_url.lower())

        # Fallback
        else:
            key = (
                job.company_name.lower(),
                job.job_title.lower(),
                job.location.lower()
            )

        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs
