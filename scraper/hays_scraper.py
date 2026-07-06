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
        self.logger.info(f"Searching Hays Browser Engine for: {query}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Changed to True for clean background processing
            page = browser.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
            except Exception as e:
                self.logger.warning(f"Bypassing slower analytic payloads: {e}")

            page.wait_for_timeout(7000)
            cards = page.locator("lib-sb-job-card")
            total = cards.count()
            self.logger.info(f"Found {total} layout cards on screen.")

            for i in range(total):
                try:
                    card = cards.nth(i)

                    # --- FIX 1: Prevent 30-Second Infinite Layout Hangs ---
                    try:
                        card.scroll_into_view_if_needed(timeout=2000)
                    except Exception:
                        self.logger.warning(f"[Hays] Card {i} obscured or lazy-loading. Attempting fast capture.")

                    page.wait_for_timeout(300)

                    # --- FIX 2: Safe Text Extraction ---
                    title_loc = card.locator("h4")
                    loc_span = card.locator("li").first

                    if title_loc.count() == 0:
                        continue

                    title = title_loc.inner_text().strip()
                    location = loc_span.inner_text().strip() if loc_span.count() > 0 else "Remote / Global"

                    key = (title.lower(), location.lower())
                    if key in seen:
                        continue
                    seen.add(key)

                    # --- FIX 3: Force Click Shifting Panels Safely ---
                    try:
                        card.click(force=True, timeout=3000)
                        page.wait_for_timeout(1000)
                    except Exception as click_err:
                        self.logger.warning(f"Could not click card panel index {i}: {click_err}")
                        continue

                    description = ""
                    # Check both visible and structural DOM containers
                    for selector in ["div.job-description", "div.rte.text-black", ".job-details-content",
                                     "lib-job-details"]:
                        try:
                            el = page.locator(selector).first
                            if el.count() > 0:
                                text = el.inner_text().strip()
                                if text:
                                    description = text
                                    break
                        except:
                            continue

                    if not description:
                        description = f"Position at {title}. View full details and apply directly on Hays portal."

                    job_obj = Job(
                        job_title=title,
                        company_name="Hays Recruiting",
                        location=location,
                        job_url=page.url,
                        apply_url=page.url,
                        source_platform="Hays"
                    )
                    job_obj.description = description
                    jobs.append(job_obj)
                    self.logger.info(f"[Hays] Successfully processed: {title}")

                    # Break early to save memory resources if you hit a massive page
                    if len(jobs) >= 15:
                        self.logger.info("[Hays] Captured optimization sample batch. Proceeding.")
                        break

                except Exception as e:
                    self.logger.error(f"Error processing card index {i}: {e}")

            browser.close()
        return jobs