import html
import re
import time
import requests
from bs4 import BeautifulSoup
from scraper.base_scraper import BaseScraper
from scraper.models import Job
from utils.logger import JobLogger


class LinkedInScraper(BaseScraper):
    def __init__(self):
        self.logger = JobLogger.get_logger()

    def scrape_jobs(self, query):
        jobs = []
        self.logger.info(f"Searching LinkedIn Public Feed for: {query}")

        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={requests.utils.quote(query)}&start=0"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://www.linkedin.com/jobs"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"[LinkedIn] Feed responded with status: {response.status_code}")
                return jobs

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("li")

            self.logger.info(f"[LinkedIn] Found {len(cards)} public job listings. Safely extracting data...")

            for card in cards:
                title_el = card.find("h3", class_="base-search-card__title")
                company_el = card.find("h4", class_="base-search-card__subtitle")
                location_el = card.find("span", class_="job-search-card__location")
                link_el = card.find("a", class_="base-card__full-link")

                if title_el and company_el:
                    title = title_el.get_text(strip=True)
                    company = company_el.get_text(strip=True)
                    location = location_el.get_text(strip=True) if location_el else "Remote / USA"
                    raw_url = link_el["href"].split("?")[0] if link_el else "https://www.linkedin.com/jobs"

                    # Parse unique Job ID from the trackback link
                    job_id_match = re.search(r'-(\d+)$|/view/(\d+)', raw_url)
                    job_id = job_id_match.group(1) or job_id_match.group(2) if job_id_match else None

                    job_obj = Job(
                        job_title=title,
                        company_name=company,
                        location=location,
                        job_url=raw_url,
                        apply_url=raw_url,
                        source_platform="LinkedIn"
                    )

                    # --- SAFE DESCRIPTION HANDLING ---
                    if job_id:
                        try:
                            # 3-Second human delay to completely stop the Connection Timeout errors
                            time.sleep(3)

                            detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                            detail_resp = requests.get(detail_url, headers=headers, timeout=5)

                            if detail_resp.status_code == 200:
                                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                                desc_el = detail_soup.find("div", class_="description__text") or detail_soup.find(
                                    "section", class_="show-more-less-html")

                                if desc_el:
                                    clean_text = re.sub(r'<[^>]*>', ' ', str(desc_el))
                                    clean_text = html.unescape(clean_text)
                                    job_obj.description = " ".join(clean_text.split())
                                else:
                                    job_obj.description = f"Position at {company}. View full requirements and apply directly via LinkedIn."
                            else:
                                job_obj.description = f"Position at {company}. View full requirements and apply directly via LinkedIn."
                        except Exception as detail_err:
                            self.logger.warning(f"Could not reach full details for {job_id} safely: {detail_err}")
                            job_obj.description = f"Position at {company}. View full requirements and apply directly via LinkedIn."
                    else:
                        job_obj.description = f"Position at {company}. View full requirements and apply directly via LinkedIn."

                    jobs.append(job_obj)
                    self.logger.info(f"[LinkedIn] Successfully processed: {title} ({company})")

        except Exception as e:
            self.logger.error(f"LinkedIn framework exception: {e}")

        return jobs

    def extract_job_details(self, page, job):
        return job