from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright
from scraper.models import Job
from utils.logger import JobLogger


class HaysScraper:
    BASE_URL = "https://www.hays.com/job-search"
    MAX_JOBS_PER_QUERY = 15  # Configurable batch size per search query

    def __init__(self, max_jobs_per_query=None):
        self.logger = JobLogger.get_logger()
        if max_jobs_per_query is not None:
            self.MAX_JOBS_PER_QUERY = max_jobs_per_query

    def build_search_url(self, query):
        return f"{self.BASE_URL}?q={quote_plus(query)}"

    def scrape_jobs(self, query):
        jobs = []
        seen = set()
        url = self.build_search_url(query)
        self.logger.info(f"Searching Hays Browser Engine for: {query}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
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

                    # Prevent 30-second infinite layout hangs
                    try:
                        card.scroll_into_view_if_needed(timeout=2000)
                    except Exception:
                        self.logger.warning(f"[Hays] Card {i} obscured or lazy-loading. Attempting fast capture.")

                    page.wait_for_timeout(300)

                    # Safe text extraction
                    title_loc = card.locator("h4")
                    loc_span = card.locator("li").first

                    if title_loc.count() == 0:
                        continue

                    title = title_loc.inner_text().strip()
                    location = loc_span.inner_text().strip() if loc_span.count() > 0 else ""

                    key = (title.lower(), location.lower())
                    if key in seen:
                        continue
                    seen.add(key)

                    # Try to extract company name from the card DOM
                    company = "Unknown Company"
                    for company_sel in ["span.company-name", "p.company", "span.hays-company", ".company-name"]:
                        try:
                            comp_el = card.locator(company_sel).first
                            if comp_el.count() > 0:
                                comp_text = comp_el.inner_text().strip()
                                if comp_text:
                                    company = comp_text
                                    break
                        except Exception:
                            continue

                    # Try to extract the actual job detail URL from the card's link
                    job_detail_url = ""
                    try:
                        link_el = card.locator("a[href]").first
                        if link_el.count() > 0:
                            href = link_el.get_attribute("href")
                            if href:
                                if href.startswith("/"):
                                    job_detail_url = f"https://www.hays.com{href}"
                                elif href.startswith("http"):
                                    job_detail_url = href
                    except Exception:
                        pass

                    # Force click shifting panels safely
                    try:
                        card.click(force=True, timeout=3000)
                        page.wait_for_timeout(1000)
                    except Exception as click_err:
                        self.logger.warning(f"Could not click card panel index {i}: {click_err}")
                        continue

                    # If we didn't get URL from the card, use the current page URL after click
                    if not job_detail_url:
                        job_detail_url = page.url

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
                        except Exception:
                            continue

                    job_obj = Job(
                        job_title=title,
                        company_name=company,
                        location=location,
                        job_url=job_detail_url,
                        apply_url=job_detail_url,
                        source_platform="Hays"
                    )
                    job_obj.description = description
                    jobs.append(job_obj)
                    self.logger.info(f"[Hays] Successfully processed: {title}")

                    # Configurable batch limit
                    if len(jobs) >= self.MAX_JOBS_PER_QUERY:
                        self.logger.info(f"[Hays] Reached batch limit ({self.MAX_JOBS_PER_QUERY}). Proceeding.")
                        break

                except Exception as e:
                    self.logger.error(f"Error processing card index {i}: {e}")

            browser.close()
        return jobs