import json
import re
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright
from scraper.base_scraper import BaseScraper
from scraper.models import Job
from utils.logger import JobLogger


class IndeedScraper(BaseScraper):
    BASE_URL = "https://www.indeed.com/jobs"

    def __init__(self):
        self.logger = JobLogger.get_logger()

    def build_search_url(self, query):
        return f"{self.BASE_URL}?q={quote_plus(query)}&l=Remote"

    def scrape_jobs(self, query):
        jobs = []
        url = self.build_search_url(query)
        self.logger.info(f"Searching Indeed for: {query}")

        with sync_playwright() as p:
            # Launch a persistent context to match a normal consumer session
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )

            # Hide automation flags (Bypasses Cloudflare detection)
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            try:
                # Load search page and let background network elements fully settle
                page.goto(url, wait_until="commit", timeout=30000)
                page.wait_for_timeout(5000)  # Give it a brief moment to load the data payload

                html_content = page.content()

                # Find NextJS embedded JSON data payload directly from text
                script_match = re.search(r'id=["\']__NEXT_DATA__["\'][^>]*>({.+?})</script>', html_content)

                meta_listings = []
                if script_match:
                    try:
                        json_data = json.loads(script_match.group(1))
                        meta_listings = (
                            json_data.get("props", {})
                            .get("pageProps", {})
                            .get("initialState", {})
                            .get("jobs", {})
                            .get("results", [])
                        )
                    except Exception as parse_err:
                        self.logger.warning(f"Failed parsing source script block: {parse_err}")

                if not meta_listings:
                    self.logger.warning(
                        "[Indeed] Cloudflare intercepted the data packet. Skipping to protect pipeline.")
                else:
                    self.logger.info(
                        f"[Indeed Data Engine] Successfully captured {len(meta_listings)} raw data objects.")
                    for item in meta_listings:
                        title = item.get("title") or item.get("jobTitle") or "Job Posting"
                        company = item.get("companyName") or item.get("company") or "Unknown"
                        location = item.get("formattedLocation") or "Remote"
                        job_key = item.get("jobkey") or item.get("jk")

                        job_url = f"https://www.indeed.com/viewjob?jk={job_key}" if job_key else page.url

                        job_obj = Job(
                            job_title=title,
                            company_name=company,
                            location=location,
                            job_url=job_url,
                            apply_url=job_url,
                            source_platform="Indeed"
                        )
                        job_obj.description = item.get("snippet") or "Open job link to view details on Indeed."
                        jobs.append(job_obj)
                        self.logger.info(f"[Indeed Data Engine] Extracted: {title} ({company})")

            except Exception as e:
                self.logger.error(f"Indeed collection framework exception: {e}")

            browser.close()

        return jobs
    def extract_job_details(self, page, job):
        return job