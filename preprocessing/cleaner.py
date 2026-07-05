import re


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"<.*?>", "", text)

    text = re.sub(r"\s+", " ", text)

    text = text.strip()

    return text


def clean_job(job):
    job["title"] = clean_text(job.get("title", ""))
    job["description"] = clean_text(job.get("description", ""))

    return job