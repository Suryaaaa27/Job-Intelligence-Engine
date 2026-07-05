from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

from scraper.models import Job
from utils.logger import JobLogger


class HaysScraper:

    BASE_URL = "https://www.hays.com/job-search"

    def __init__(self):

        self.logger = JobLogger.get_logger()

    def build_search_url(self, query):

        return f"{self.BASE_URL}?q={quote_plus(query)}"

    def scrape_jobs(self, query):

        jobs = []
        seen = set()

        url = self.build_search_url(query)

        self.logger.info(f"Searching Hays : {query}")

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=False
            )

            page = browser.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(5000)

            cards = page.locator("lib-sb-job-card")

            total = cards.count()

            self.logger.info(
                f"Found {total} cards"
            )

            for i in range(total):

                try:

                    card = cards.nth(i)

                    title = card.locator(
                        "h4"
                    ).inner_text().strip()

                    location = card.locator(
                        "li"
                    ).first.inner_text().strip()

                    href = ""

                    try:

                        anchor = card.locator(
                            "xpath=ancestor::a[1]"
                        )

                        if anchor.count():

                            href = anchor.get_attribute(
                                "href"
                            ) or ""

                    except:

                        pass

                    if href.startswith("/"):

                        href = (
                            "https://www.hays.com"
                            + href
                        )

                    key = (
                        title.lower(),
                        location.lower()
                    )

                    if key in seen:

                        continue

                    seen.add(key)

                    jobs.append(

                        Job(

                            job_title=title,
                            
                            company_name="",

                            location=location,
                            
                            job_url=href,

                            apply_url=href,

                            source_platform="Hays",

                        )

                    )

                except Exception as e:

                    self.logger.error(e)

            browser.close()

        self.logger.info(
            f"Unique Jobs : {len(jobs)}"
        )

        return jobs

    def extract_job_details(self, page, job):

        try:

            page.wait_for_timeout(1500)

            # Title shown in the detail panel
            try:
                job.title = page.locator(
                    "div.job-description h4"
                ).first.inner_text().strip()
            except:
                pass

            # Complete job description
            try:
                job.description = page.locator(
                    "div.rte.text-black"
                ).first.inner_text().strip()
            except:
                pass

        except Exception as e:
            self.logger.error(e)

        return job