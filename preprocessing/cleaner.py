import re
from datetime import datetime

def clean_text(text):
    if not text: return ""
    text = re.sub(r"<.*?>", "", text)  # Strip HTML tags
    return " ".join(text.split()).strip()

def standardize_location(location):
    if not location or location.lower() in ["remote", "anywhere", "work from home", "wfh"]:
        return "Remote"
    return ", ".join([p.strip().title() for part in location.split(",")])

def standardize_date(date_str):
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return " ".join(str(date_str).split()).strip()


def clean_job(job_obj):
    # Safely extract from dictionary or object attributes, supporting both schemas
    def get_val(obj, keys, default=""):
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            val = obj.get(key, None) if isinstance(obj, dict) else getattr(obj, key, None)
            if val:  # Return the first truthy value found
                return val
        return default

    return {
        # Check standard name first, then fallback to scraper alternate name
        "title": clean_text(get_val(job_obj, ["title", "job_title"], "Unknown Title")),
        "company": clean_text(get_val(job_obj, ["company", "company_name"], "Unknown Company")),
        "description": clean_text(get_val(job_obj, "description", "")),
        "source": clean_text(get_val(job_obj, ["source", "source_platform"], "Hays")),
        "url": clean_text(get_val(job_obj, ["url", "job_url"], "")),
        "location": standardize_location(get_val(job_obj, "location", "")),
        "posted_date": standardize_date(get_val(job_obj, "posted_date", "")),
        "role_predictions": get_val(job_obj, "role_predictions", []),
        "extracted_skills": get_val(job_obj, "extracted_skills", []),
        "relevance_scores": get_val(job_obj, "relevance_scores", {})
    }
