from scraper.models import Job


def remove_duplicates(jobs: list[dict]):

    unique_jobs = []
    seen = set()

    for job in jobs:

        job_url = job.get("job_url", "")

        if job_url:
            key = ("url", job_url.lower())
        else:
            key = (
                job.get("company_name", "").lower(),
                job.get("job_title", "").lower(),
                job.get("location", "").lower()
            )

        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs
