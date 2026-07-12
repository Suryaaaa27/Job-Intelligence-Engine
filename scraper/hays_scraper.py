import json
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

from scraper.models import Job
from utils.logger import JobLogger


class HaysScraper:

    BASE_URL = "https://www.hays.co.uk/job-search"

    HAYS_JOBS_API = (
        "https://mapi.hays.com/"
        "jobportalapi/int/s/gb/en/"
        "jobportal/job/browse/v1/getCombinedJobs"
    )

    MAX_PAGES = 100

    def __init__(self, max_pages=None):

        self.logger = JobLogger.get_logger()

        self.max_pages = (
            max_pages
            if max_pages is not None
            else self.MAX_PAGES
        )

    def build_search_url(self, query):

        return (
            f"{self.BASE_URL}"
            f"?q={quote_plus(query)}"
        )

    def _build_payload(
        self,
        query,
        page_token="0"
    ):

        return {

            "facetLocation": "",

            "flexibleWorking": "false",

            "fullTime": "false",

            "industry": [],

            "isSponsored": False,

            "jobType": [],

            "partTime": "false",

            "query": query,

            "locations": "",

            "salMax": "",

            "salMin": "",

            "sortType": "",

            "specialismId": "",

            "subSpecialismId": "",

            "typeOnlyFilter": "",

            "userAgent": "-Desktop",

            "radius": 15,

            "isCrossCountry": False,

            "isResponseCountry": False,

            "responseSiteLocale": "",

            "pageToken": page_token,

            "jobId": "",

            "jobRefrence": "",

            "crossCountryUrl": "",

            "payType": "",

            "type": "search",

            "cookieDomain": ".hays.co.uk"

        }

    def _extract_date(self, date_data):

        if not isinstance(date_data, dict):

            return ""

        year = date_data.get("year")

        month = date_data.get("month")

        day = date_data.get("day")

        if not all([
            year,
            month,
            day
        ]):

            return ""

        return (
            f"{year:04d}-"
            f"{month:02d}-"
            f"{day:02d}"
        )

    def _extract_compensation(
        self,
        api_job
    ):

        min_salary = None

        max_salary = None

        currency = None

        compensation_min = api_job.get(
            "compensationAmountMin"
        )

        compensation_max = api_job.get(
            "compensationAmountMax"
        )

        compensation = api_job.get(
            "compensationAmount"
        )

        if isinstance(
            compensation_min,
            dict
        ):

            min_salary = compensation_min.get(
                "units"
            )

            currency = compensation_min.get(
                "currencyCode"
            )

        if isinstance(
            compensation_max,
            dict
        ):

            max_salary = compensation_max.get(
                "units"
            )

            if not currency:

                currency = compensation_max.get(
                    "currencyCode"
                )

        if isinstance(
            compensation,
            dict
        ):

            amount = compensation.get(
                "units"
            )

            if min_salary is None:

                min_salary = amount

            if max_salary is None:

                max_salary = amount

            if not currency:

                currency = compensation.get(
                    "currencyCode"
                )

        return (
            min_salary,
            max_salary,
            currency
        )

    def _get_job_title(
        self,
        api_job
    ):

        return (

            api_job.get("title")

            or api_job.get("jobTitle")

            or api_job.get("displayName")

            or "Unknown Title"

        )

    def _get_company(
        self,
        api_job
    ):

        return (

            api_job.get("hiringOrganization")

            or api_job.get("companyDisplayName")

            or api_job.get("companyTitle")

            or "Hays"

        )

    def _get_location(
        self,
        api_job
    ):

        location = api_job.get(
            "location"
        )

        if isinstance(
            location,
            str
        ):

            return location

        if isinstance(
            location,
            dict
        ):

            return (

                location.get("displayName")

                or location.get("name")

                or location.get("city")

                or ""

            )

        locations = api_job.get(
            "locations"
        )

        if isinstance(
            locations,
            list
        ) and locations:

            first_location = locations[0]

            if isinstance(
                first_location,
                str
            ):

                return first_location

            if isinstance(
                first_location,
                dict
            ):

                return (

                    first_location.get(
                        "displayName"
                    )

                    or first_location.get(
                        "name"
                    )

                    or first_location.get(
                        "city"
                    )

                    or ""

                )

        return ""

    def _get_job_url(
        self,
        api_job
    ):

        return (

            api_job.get("applicationUrl")

            or api_job.get("jobUrl")

            or api_job.get("url")

            or ""

        )

    def _create_job(
        self,
        api_job
    ):

        title = self._get_job_title(
            api_job
        )

        company = self._get_company(
            api_job
        )

        location = self._get_location(
            api_job
        )

        job_url = self._get_job_url(
            api_job
        )

        description = (
            api_job.get("description")
            or ""
        )

        posted_date = self._extract_date(
            api_job.get("createDate")
        )

        (
            min_salary,
            max_salary,
            currency

        ) = self._extract_compensation(
            api_job
        )

        job = Job(

            job_title=title,

            company_name=company,

            location=location,

            job_url=job_url,

            apply_url=job_url,

            source_platform="Hays"

        )

        job.description = description

        job.posted_date = posted_date

        job.min_salary = min_salary

        job.max_salary = max_salary

        job.currency = currency

        job.benefits = (
            api_job.get("benefits")
            or []
        )

        return job

    def _generate_job_key(
        self,
        job
    ):

        return (

            (
                job.job_url
                or ""
            )
            .strip()
            .lower()

            or (

                (
                    job.job_title
                    or ""
                )
                .strip()
                .lower(),

                (
                    job.company_name
                    or ""
                )
                .strip()
                .lower(),

                (
                    job.location
                    or ""
                )
                .strip()
                .lower()

            )

        )

    def scrape_jobs(
        self,
        query
    ):

        jobs = []

        seen = set()

        seen_tokens = set()

        captured_headers = {}

        search_url = self.build_search_url(
            query
        )

        self.logger.info(
            f"Searching Hays API Engine for: "
            f"{query}"
        )

        with sync_playwright() as playwright:

            browser = (
                playwright
                .chromium
                .launch(
                    headless=True
                )
            )

            page = browser.new_page()

            def capture_api_request(
                request
            ):

                nonlocal captured_headers

                try:

                    if (
                        "getcombinedjobs"
                        not in request.url.lower()
                    ):

                        return

                    captured_headers = dict(
                        request.headers
                    )

                except Exception:

                    pass

            page.on(
                "request",
                capture_api_request
            )

            try:

                page.goto(

                    search_url,

                    wait_until="domcontentloaded",

                    timeout=60000

                )

            except Exception as error:

                self.logger.warning(
                    "[Hays] Initial navigation "
                    f"warning: {error}"
                )

            page.wait_for_timeout(
                7000
            )

            if not captured_headers:

                self.logger.error(
                    "[Hays] Could not capture "
                    "API session headers."
                )

                browser.close()

                return jobs

            safe_headers = {

                key: value

                for key, value
                in captured_headers.items()

                if key.lower() not in {

                    "content-length",

                    "host",

                    "connection"

                }

            }

            page_token = "0"

            page_number = 1

            expected_total = None

            while (
                page_number
                <= self.max_pages
            ):

                if page_token in seen_tokens:

                    self.logger.warning(
                        "[Hays] Repeated page token "
                        "detected. Stopping."
                    )

                    break

                seen_tokens.add(
                    page_token
                )

                self.logger.info(
                    f"[Hays] Fetching API Page "
                    f"{page_number}"
                )

                payload = self._build_payload(

                    query,

                    page_token

                )

                try:

                    response = (
                        page.request.post(

                            self.HAYS_JOBS_API,

                            headers=safe_headers,

                            data=json.dumps(
                                payload
                            ),

                            timeout=60000

                        )
                    )

                except Exception as error:

                    self.logger.error(
                        "[Hays] API request failed: "
                        f"{error}"
                    )

                    break

                if not response.ok:

                    self.logger.error(
                        "[Hays] API returned "
                        f"HTTP {response.status}"
                    )

                    break

                try:

                    response_data = (
                        response.json()
                    )

                except Exception as error:

                    self.logger.error(
                        "[Hays] Invalid API response: "
                        f"{error}"
                    )

                    break

                result = (

                    response_data
                    .get("data", {})
                    .get("result", {})

                )

                api_jobs = result.get(
                    "jobs",
                    []
                )

                next_page_token = result.get(
                    "nextPageToken"
                )

                if expected_total is None:

                    expected_total = (

                        result.get(
                            "pageableCount"
                        )

                        or result.get(
                            "resultCount"
                        )

                    )

                    self.logger.info(
                        "[Hays] API reports "
                        f"{expected_total} jobs"
                    )

                self.logger.info(
                    f"[Hays] Page {page_number} "
                    f"returned {len(api_jobs)} jobs"
                )

                if not api_jobs:

                    self.logger.info(
                        "[Hays] Empty API page. "
                        "Stopping pagination."
                    )

                    break

                inserted_on_page = 0

                for api_job in api_jobs:

                    try:

                        job = self._create_job(
                            api_job
                        )

                        job_key = (
                            self._generate_job_key(
                                job
                            )
                        )

                        if job_key in seen:

                            continue

                        seen.add(
                            job_key
                        )

                        jobs.append(
                            job
                        )

                        inserted_on_page += 1

                    except Exception as error:

                        self.logger.error(
                            "[Hays] Job conversion "
                            f"failed: {error}"
                        )

                self.logger.info(
                    f"[Hays] Page {page_number} "
                    f"added {inserted_on_page} "
                    "unique jobs"
                )

                self.logger.info(
                    "[Hays] Total unique jobs: "
                    f"{len(jobs)}"
                )

                if (
                    expected_total is not None
                    and len(jobs) >= expected_total
                ):

                    self.logger.info(
                        "[Hays] Expected result "
                        "count reached."
                    )

                    break

                if not next_page_token:

                    self.logger.info(
                        "[Hays] No next page token. "
                        "Pagination completed."
                    )

                    break

                page_token = (
                    next_page_token
                )

                page_number += 1

            browser.close()

        self.logger.info(
            "[Hays] API pagination completed."
        )

        self.logger.info(
            "[Hays] Total unique jobs collected: "
            f"{len(jobs)}"
        )

        return jobs