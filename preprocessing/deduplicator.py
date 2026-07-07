import re
from difflib import SequenceMatcher

def get_job_val(job, key, default=""):
    """Helper to get a value from either a dictionary or object attribute."""
    if isinstance(job, dict):
        return job.get(key, default) or default
    return getattr(job, key, default) or default

def get_tokens(text):
    """Normalize and tokenize text into a set of lowercased alphanumeric words."""
    if not text:
        return set()
    # Replace non-alphanumeric with spaces, lower, split
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    return set(cleaned.split())

def normalize_title(title):
    """Normalize title by removing parentheses/brackets and extra spacing."""
    if not title:
        return ""
    # Remove text in parentheses/brackets, e.g. "ML Engineer (Generative AI)" -> "ML Engineer"
    title_clean = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title.lower())
    return " ".join(title_clean.split()).strip()

def title_similarity(t1, t2):
    """Calculate similarity of normalized titles using SequenceMatcher."""
    n1 = normalize_title(t1)
    n2 = normalize_title(t2)
    return SequenceMatcher(None, n1, n2).ratio()

def remove_duplicates(jobs, threshold=0.85):
    """
    Remove duplicates from list of jobs (which can be dicts or objects).
    Uses a fuzzy matching approach on Normalized Title + Description token overlap.
    """
    unique_jobs = []
    
    for job in jobs:
        title = get_job_val(job, "title", get_job_val(job, "job_title", ""))
        company = get_job_val(job, "company", get_job_val(job, "company_name", ""))
        desc = get_job_val(job, "description", "")
        url = get_job_val(job, "url", get_job_val(job, "job_url", ""))
        
        is_duplicate = False
        
        # Build token set for description
        desc_tokens = get_tokens(desc)
        
        for unique_job in unique_jobs:
            u_title = get_job_val(unique_job, "title", get_job_val(unique_job, "job_title", ""))
            u_company = get_job_val(unique_job, "company", get_job_val(unique_job, "company_name", ""))
            u_desc = get_job_val(unique_job, "description", "")
            u_url = get_job_val(unique_job, "url", get_job_val(unique_job, "job_url", ""))
            
            # 1. Direct URL check
            if url and u_url and url == u_url:
                is_duplicate = True
                break
                
            # 2. Company & Title check (if same company and normalized titles match)
            same_company = company.lower() == u_company.lower() and company != ""
            t_sim = title_similarity(title, u_title)
            
            if same_company and t_sim > 0.85:
                is_duplicate = True
                break
                
            # 3. Fuzzy description overlap (Jaccard) + title similarity
            u_desc_tokens = get_tokens(u_desc)
            if len(desc_tokens) > 0 and len(u_desc_tokens) > 0:
                intersection = desc_tokens.intersection(u_desc_tokens)
                union = desc_tokens.union(u_desc_tokens)
                jaccard = len(intersection) / len(union)
                
                # If descriptions are extremely similar, it's a duplicate
                if jaccard > 0.95:
                    is_duplicate = True
                    break
                # If titles are similar and description content is highly overlapping
                elif t_sim > 0.55 and jaccard > threshold:
                    is_duplicate = True
                    break
                    
        if not is_duplicate:
            unique_jobs.append(job)
            
    return unique_jobs