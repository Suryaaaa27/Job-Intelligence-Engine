import json
import re
from typing import Dict, Any, List

def load_optimized_json(filepath: str) -> Dict[str, Any]:
    """Loads the optimized JSON from the given filepath."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_links(text: str) -> List[Dict[str, str]]:
    """Extracts emails and URLs from text and returns a list of dictionaries with link info."""
    links = []
    if not text:
        return links
        
    # Extract email
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, text)
    for email in emails:
        links.append({"text": email, "url": f"mailto:{email}", "type": "email"})
        
    # Extract URLs (basic matching)
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(?:com|org|net|io|me|co)(?:/[^\s]*)?)'
    urls = re.findall(url_pattern, text)
    for url in urls:
        # Don't double-add if it overlaps with an email domain
        if any(url in email for email in emails):
            continue
        # Avoid picking up plain domain ends like "CA | contact@..." -> avoid matching random stuff
        # We will do a simple check. If it doesn't have http/www, and doesn't look like a profile, it might be a false positive
        href = url if url.startswith("http") else f"https://{url}"
        links.append({"text": url, "url": href, "type": "link"})
        
    return links

def normalize_resume_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes the raw optimized resume JSON into a structured dictionary
    suitable for Jinja2 ATS template rendering.
    """
    original_resume = raw_data.get("original_resume", {})
    
    candidate_name = raw_data.get("candidate_name") or original_resume.get("candidate_name") or "Professional"
    summary = raw_data.get("optimized_summary", "")
    
    # Contact info logic
    contact_dict = original_resume.get("contact_info", {})
    contact_text = original_resume.get("summary", "") if not summary else original_resume.get("summary", "")
    if contact_text == summary:
        contact_text = ""
        
    contact_links = []
    
    if contact_dict:
        # Build structured contact text and links
        parts = []
        if contact_dict.get("phone"):
            parts.append(contact_dict["phone"])
        if contact_dict.get("location"):
            parts.append(contact_dict["location"])
        if contact_dict.get("email"):
            email = contact_dict["email"]
            contact_links.append({"text": email, "url": f"mailto:{email}", "type": "email"})
            parts.append(email)
        if contact_dict.get("linkedin"):
            linkedin = contact_dict["linkedin"]
            url = linkedin if linkedin.startswith("http") else f"https://{linkedin}"
            contact_links.append({"text": linkedin, "url": url, "type": "link"})
            parts.append(linkedin)
        if contact_dict.get("github"):
            github = contact_dict["github"]
            url = github if github.startswith("http") else f"https://{github}"
            contact_links.append({"text": github, "url": url, "type": "link"})
            parts.append(github)
        if contact_dict.get("portfolio"):
            portfolio = contact_dict["portfolio"]
            url = portfolio if portfolio.startswith("http") else f"https://{portfolio}"
            contact_links.append({"text": portfolio, "url": url, "type": "link"})
            parts.append(portfolio)
            
        if parts:
            contact_text = " | ".join(parts)
    else:
        # Fallback to regex extraction if no structured contact info
        contact_links = extract_links(contact_text)
    
    # Sort links by length descending to avoid nested replacements
    contact_links.sort(key=lambda x: len(x["text"]), reverse=True)
    
    # Inject HTML anchor tags into contact_text for hyperlinks
    for link_info in contact_links:
        original_text = link_info["text"]
        url = link_info["url"]
        replacement = f'<a href="{url}" style="color: inherit; text-decoration: none;">{original_text}</a>'
        contact_text = contact_text.replace(original_text, replacement)

    
    # Skills
    skills = original_resume.get("skills", [])
    if not skills:
        skills = original_resume.get("tools_technologies", [])
        
    # Experience
    raw_experience = original_resume.get("experience", [])
    optimized_bullets_map = raw_data.get("optimized_bullets", {})
    
    experience_list = []
    for exp in raw_experience:
        title = exp.get("title", "")
        if not title:
            continue
        company = exp.get("company", "")
        start_date = exp.get("start_date", "")
        end_date = exp.get("end_date", "")
        bullets = optimized_bullets_map.get(title)
        if bullets is None:
            bullets = exp.get("bullets", [])
            
        experience_list.append({
            "title": title,
            "company": company,
            "start_date": start_date,
            "end_date": end_date,
            "bullets": [b for b in bullets if b.strip()]
        })
        
    projects = original_resume.get("projects", [])
    education = original_resume.get("education", [])
    certifications = original_resume.get("certifications", [])

    return {
        "candidate_name": candidate_name,
        "contact_info": contact_text,
        "contact_links": contact_links,
        "summary": summary,
        "skills": [s for s in skills if s.strip()],
        "experience": experience_list,
        "projects": projects,
        "education": education,
        "certifications": certifications
    }
