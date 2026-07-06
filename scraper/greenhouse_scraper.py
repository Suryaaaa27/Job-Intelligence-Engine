import html
import re
import requests
from scraper.base_scraper import BaseScraper
from scraper.models import Job
from utils.logger import JobLogger


class GreenhouseScraper(BaseScraper):
    def __init__(self):
        self.logger = JobLogger.get_logger()
        self.target_companies = [
            "airbnb", "figma", "stripe", "hashicorp", "snap",
            "discord", "reddit", "vercel", "paloaltonetworks"
        ]

    def scrape_jobs(self, query):
        jobs = []
        query_lower = query.lower()
        self.logger.info(f"Searching Greenhouse API across {len(self.target_companies)} companies...")

        for company in self.target_companies:
            # Adding ?content=true here pulls down descriptions for EVERY job in one single call!
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code != 200:
                    continue

                listings = response.json().get("jobs", [])
                for item in listings:
                    title = item.get("title", "")
                    if query_lower not in title.lower():
                        continue

                    job_id = item.get("id")
                    job_url = f"https://boards.greenhouse.io/{company}/jobs/{job_id}"
                    location = item.get("location", {}).get("name", "Remote / USA")

                    job_obj = Job(
                        job_title=title,
                        company_name=company.capitalize(),
                        location=location,
                        job_url=job_url,
                        apply_url=job_url,
                        source_platform="Greenhouse"
                    )

                    # --- Grab the content directly from 'item' (No extra API call needed!) ---
                    raw_content = item.get("content", "")

                    if raw_content:
                        clean_text = re.sub(r'<[^>]*>', ' ', raw_content)
                        clean_text = html.unescape(clean_text)
                        job_obj.description = " ".join(clean_text.split())
                    else:
                        job_obj.description = "Full details available on company job board."

                    jobs.append(job_obj)
                    self.logger.info(f"[Greenhouse] Processed: {title} ({company.capitalize()})")
            except Exception as e:
                self.logger.error(f"Greenhouse connection error for {company}: {e}")

        return jobs

    def extract_job_details(self, page, job):
        return job