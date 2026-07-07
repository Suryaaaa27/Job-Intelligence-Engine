import re
from datetime import datetime

def clean_text(text):
    if not text: return ""
    text = re.sub(r"<.*?>", "", text)  # Strip HTML tags
    return " ".join(text.split()).strip()

def standardize_location(location):
    if not location or location.lower() in ["remote", "anywhere", "work from home", "wfh"]:
        return "Remote"
    return ", ".join([part.strip().title() for part in location.split(",")])

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

    desc = clean_text(get_val(job_obj, "description", ""))
    title = clean_text(get_val(job_obj, ["title", "job_title"], "Unknown Title"))
    
    salary_info = extract_salary(desc)
    job_type = standardize_job_type(title, desc)

    return {
        # Check standard name first, then fallback to scraper alternate name
        "title": title,
        "company": clean_text(get_val(job_obj, ["company", "company_name"], "Unknown Company")),
        "description": desc,
        "source": clean_text(get_val(job_obj, ["source", "source_platform"], "Unknown")),
        "url": clean_text(get_val(job_obj, ["url", "job_url"], "")),
        "location": standardize_location(get_val(job_obj, "location", "")),
        "posted_date": standardize_date(get_val(job_obj, "posted_date", "")),
        "role_predictions": get_val(job_obj, "role_predictions", []),
        "extracted_skills": get_val(job_obj, "extracted_skills", []),
        "relevance_scores": get_val(job_obj, "relevance_scores", {}),
        "min_salary": salary_info["min_salary"],
        "max_salary": salary_info["max_salary"],
        "currency": salary_info["currency"],
        "job_type": job_type
    }


def extract_salary(text):
    if not text:
        return {"min_salary": None, "max_salary": None, "currency": None}
    
    currency_map = {"$": "USD", "£": "GBP", "€": "EUR", "usd": "USD", "gbp": "GBP", "eur": "EUR"}
    currency = None
    
    for sym, name in currency_map.items():
        if sym in text.lower():
            currency = name
            break
            
    # Clean commas in numeric substrings for easier matching (e.g. 100,000 -> 100000)
    cleaned_text = re.sub(r'(?<=\d),(?=\d)', '', text)
    
    # Range check: e.g. $80k - $120k or 80000 - 120000
    range_regex = r'(?:[\$£€]|USD|GBP|EUR)?\s*(\d+)\s*(k|K)?\s*(?:-|to)\s*(?:[\$£€]|USD|GBP|EUR)?\s*(\d+)\s*(k|K)?\b'
    match = re.search(range_regex, cleaned_text)
    if match:
        try:
            min_val = int(match.group(1))
            max_val = int(match.group(3))
            if match.group(2) and match.group(2).lower() == 'k':
                min_val *= 1000
            elif min_val < 1000:
                if match.group(4) and match.group(4).lower() == 'k':
                    min_val *= 1000
            if match.group(4) and match.group(4).lower() == 'k':
                max_val *= 1000
                
            if min_val > 1000:
                return {"min_salary": min_val, "max_salary": max_val, "currency": currency}
        except ValueError:
            pass

    # Single check: e.g. $120,000 or $120k
    single_regex = r'(?:[\$£€]|USD|GBP|EUR)\s*(\d+)\s*(k|K)?\b'
    match = re.search(single_regex, cleaned_text)
    if match:
        try:
            val = int(match.group(1))
            if match.group(2) and match.group(2).lower() == 'k':
                val *= 1000
            if val > 1000:
                return {"min_salary": val, "max_salary": val, "currency": currency}
        except ValueError:
            pass
            
    return {"min_salary": None, "max_salary": None, "currency": currency}


def standardize_job_type(title, description):
    combined = f"{title} {description}".lower()
    if "part-time" in combined or "part time" in combined:
        return "Part-time"
    elif "contract" in combined or "contractor" in combined or "freelance" in combined:
        return "Contract"
    elif "intern" in combined or "internship" in combined:
        return "Internship"
    elif "remote" in combined or "work from home" in combined or "wfh" in combined:
        return "Remote"
    else:
        return "Full-time"

