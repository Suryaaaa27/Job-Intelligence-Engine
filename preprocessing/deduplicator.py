def remove_duplicates(jobs):

    unique_jobs = []
    seen = set()

    for job in jobs:

        key = (

         job.title.lower(),

         job.location.lower()
        )

        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs