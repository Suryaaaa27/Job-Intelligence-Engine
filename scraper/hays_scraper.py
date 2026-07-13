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

    def _get_custom_field(
        self,
        api_job,
        field_name,
        field_group="nonFilterableCustomFields"
    ):

        fields = api_job.get(
            field_group
        )

        if not isinstance(fields, dict):

            return None

        field = fields.get(
            field_name
        )

        if not isinstance(field, dict):

            return None

        values = field.get(
            "values"
        )

        if not isinstance(values, list):

            return None

        if not values:

            return None

        return values[0]

    def _get_any_custom_field(
        self,
        api_job,
        field_name
    ):

        value = self._get_custom_field(
            api_job,
            field_name,
            "nonFilterableCustomFields"
        )

        if value is not None:

            return value

        return self._get_custom_field(
            api_job,
            field_name,
            "filterableCustomFields"
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

        if min_salary is None:

            min_salary = self._get_any_custom_field(
                api_job,
                "xminSalary"
            )

        if max_salary is None:

            max_salary = self._get_any_custom_field(
                api_job,
                "xmaxSalary"
            )

        if not currency:

            currency = self._get_any_custom_field(
                api_job,
                "SalaryCurrency"
            )

        try:

            if min_salary is not None:

                min_salary = float(
                    min_salary
                )

        except (
            TypeError,
            ValueError
        ):

            min_salary = None

        try:

            if max_salary is not None:

                max_salary = float(
                    max_salary
                )

        except (
            TypeError,
            ValueError
        ):

            max_salary = None

        return (
            min_salary,
            max_salary,
            currency
        )

    def _build_salary(
        self,
        api_job,
        min_salary,
        max_salary,
        currency
    ):

        salary_description = (
            self._get_any_custom_field(
                api_job,
                "xSalaryDescription"
            )
        )

        if salary_description:

            return str(
                salary_description
            ).strip()

        compensation_type = (
            self._get_any_custom_field(
                api_job,
                "CompensationType"
            )
        )

        if (
            min_salary is None
            and max_salary is None
        ):

            return ""

        salary_parts = []

        if currency:

            salary_parts.append(
                str(currency)
            )

        if (
            min_salary is not None
            and max_salary is not None
        ):

            if min_salary == max_salary:

                salary_parts.append(
                    f"{min_salary:g}"
                )

            else:

                salary_parts.append(
                    f"{min_salary:g} - "
                    f"{max_salary:g}"
                )

        elif min_salary is not None:

            salary_parts.append(
                f"From {min_salary:g}"
            )

        elif max_salary is not None:

            salary_parts.append(
                f"Up to {max_salary:g}"
            )

        if compensation_type:

            salary_parts.append(
                f"/ {compensation_type}"
            )

        return " ".join(
            salary_parts
        ).strip()

    def _get_job_title(
        self,
        api_job
    ):

        return (

            api_job.get("title")

            or self._get_any_custom_field(
                api_job,
                "JobTitle"
            )

            or api_job.get("jobTitle")

            or api_job.get("displayName")

            or "Unknown Title"

        )

    def _get_company(
        self,
        api_job
    ):

        hiring_organization = api_job.get(
            "hiringOrganization"
        )

        if isinstance(
            hiring_organization,
            str
        ) and hiring_organization.strip():

            return hiring_organization.strip()

        if isinstance(
            hiring_organization,
            dict
        ):

            company = (

                hiring_organization.get("name")

                or hiring_organization.get(
                    "displayName"
                )

            )

            if company:

                return company

        company_display_name = api_job.get(
            "companyDisplayName"
        )

        if company_display_name:

            return company_display_name

        # Hays companyTitle is an internal distributor
        # identifier such as hays-gcj-v4-pd-online.
        # It is not the employer name.

        return "Hays"

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
        ) and location.strip():

            return location.strip()

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

        custom_location = (
            self._get_any_custom_field(
                api_job,
                "xLocationDescription"
            )
        )

        if custom_location:

            return str(
                custom_location
            ).strip()

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

    def _extract_location_details(
        self,
        api_job
    ):

        country = ""

        state = ""

        city = ""

        geo_locations = api_job.get(
            "geoLocations"
        )

        if (
            isinstance(
                geo_locations,
                list
            )
            and geo_locations
            and isinstance(
                geo_locations[0],
                dict
            )
        ):

            geo = geo_locations[0]

            country = (

                geo.get("countryCode")

                or geo.get(
                    "countryDisplay"
                )

                or ""

            )

            state = (

                geo.get(
                    "adminLevelOneDisplay"
                )

                or ""

            )

            city = (

                geo.get(
                    "cityLevelDisplay"
                )

                or geo.get(
                    "localityDisplay"
                )

                or ""

            )

        if not country:

            country = (
                self._get_any_custom_field(
                    api_job,
                    "LocationDescriptionLevel3"
                )
                or ""
            )

        if not state:

            state = (
                self._get_any_custom_field(
                    api_job,
                    "LocationDescriptionLevel4"
                )
                or ""
            )

        if not city:

            city = (
                self._get_any_custom_field(
                    api_job,
                    "LocationDescriptionLevel6"
                )

                or self._get_any_custom_field(
                    api_job,
                    "LocationDescriptionLevel5"
                )

                or api_job.get("location")

                or ""
            )

        return (
            str(country).strip(),
            str(state).strip(),
            str(city).strip()
        )

    def _get_job_id(
        self,
        api_job
    ):

        job_id = self._get_any_custom_field(
            api_job,
            "JobId"
        )

        if job_id:

            return str(
                job_id
            ).strip()

        record_id = self._get_any_custom_field(
            api_job,
            "RecordID"
        )

        if record_id:

            return str(
                record_id
            ).strip()

        job_name = api_job.get(
            "name"
        )

        if job_name:

            return str(
                job_name
            ).rsplit(
                "/",
                1
            )[-1]

        return ""

    def _get_job_url(
        self,
        api_job
    ):

        return (

            api_job.get(
                "jobRequisitionId"
            )

            or api_job.get(
                "trackingUrl"
            )

            or api_job.get(
                "jobReferenceUrl"
            )

            or api_job.get(
                "jobUrl"
            )

            or api_job.get(
                "url"
            )

            or ""

        )

    def _get_apply_url(
        self,
        api_job
    ):

        return (

            api_job.get(
                "applicationUrl"
            )

            or self._get_job_url(
                api_job
            )

        )

    def _get_employment_type(
        self,
        api_job
    ):

        employment_types = api_job.get(
            "employmentTypes"
        )

        if (
            isinstance(
                employment_types,
                list
            )
            and employment_types
        ):

            employment_type = str(
                employment_types[0]
            )

            return (
                employment_type
                .replace(
                    "_",
                    " "
                )
                .title()
            )

        job_type = self._get_any_custom_field(
            api_job,
            "xjobType"
        )

        job_type_mapping = {

            "P": "Full Time",

            "C": "Contractor",

            "T": "Temporary",

            "PT": "Part Time"

        }

        if job_type:

            return job_type_mapping.get(

                str(job_type).upper(),

                str(job_type)

            )

        full_time = self._get_any_custom_field(
            api_job,
            "FullTime"
        )

        part_time = self._get_any_custom_field(
            api_job,
            "PartTime"
        )

        if str(full_time).lower() == "true":

            return "Full Time"

        if str(part_time).lower() == "true":

            return "Part Time"

        return ""

    def _get_workplace_type(
        self,
        api_job
    ):

        allow_telecommute = api_job.get(
            "allowTelecommute"
        )

        if allow_telecommute is True:

            return "Remote"

        flexible_working = (
            self._get_any_custom_field(
                api_job,
                "FlexibleWorking"
            )
        )

        description = str(
            api_job.get(
                "description"
            )
            or ""
        ).lower()

        location = str(
            api_job.get(
                "location"
            )
            or ""
        ).lower()

        if (
            "remote" in location
            or "fully remote" in description
            or "100% remote" in description
            or "uk (remote)" in description
        ):

            return "Remote"

        if (
            "hybrid" in description
            or str(
                flexible_working
            ).lower() == "true"
        ):

            return "Hybrid"

        if (
            "onsite" in description
            or "on-site" in description
        ):

            return "On-site"

        return "Unknown"

    def _extract_skills(
        self,
        api_job
    ):

        skills = []

        skill_text = (
            self._get_any_custom_field(
                api_job,
                "xDescription"
            )
        )

        if not skill_text:

            skill_text = (
                self._get_any_custom_field(
                    api_job,
                    "SearchTextSnippet"
                )
            )

        if skill_text:

            for skill in str(
                skill_text
            ).split(","):

                cleaned_skill = skill.strip()

                if cleaned_skill:

                    skills.append(
                        cleaned_skill
                    )

        return list(
            dict.fromkeys(
                skills
            )
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

        (
            country,
            state,
            city

        ) = self._extract_location_details(
            api_job
        )

        job_id = self._get_job_id(
            api_job
        )

        job_url = self._get_job_url(
            api_job
        )

        apply_url = self._get_apply_url(
            api_job
        )

        description = (
            api_job.get("description")
            or ""
        )

        posted_date = self._extract_date(

            api_job.get("publishDate")

            or api_job.get("createDate")

            or api_job.get("startDate")

        )

        (
            min_salary,
            max_salary,
            currency

        ) = self._extract_compensation(
            api_job
        )

        salary = self._build_salary(

            api_job,

            min_salary,

            max_salary,

            currency

        )

        employment_type = (
            self._get_employment_type(
                api_job
            )
        )

        workplace_type = (
            self._get_workplace_type(
                api_job
            )
        )

        skills = self._extract_skills(
            api_job
        )

        job = Job(

            job_id=job_id,

            job_title=title,

            company_name=company,

            source_platform="Hays",

            location=location,

            country=country,

            state=state,

            city=city,

            workplace_type=workplace_type,

            employment_type=employment_type,

            salary=salary,

            posted_date=posted_date,

            job_url=job_url,

            apply_url=apply_url,

            description=description,

            skills=skills

        )

        # Compatibility with the current repository
        # and future MongoDB schema.

        job.min_salary = min_salary

        job.max_salary = max_salary

        job.currency = currency

        job.benefits = (
            api_job.get("benefits")
            or []
        )

        job.department = (
            api_job.get("department")
            or ""
        )

        job.responsibilities = (
            api_job.get("responsibilities")
            or ""
        )

        job.qualifications = (
            api_job.get("qualifications")
            or []
        )

        job.summary = (
            api_job.get("summary")
            or ""
        )

        job.salary_frequency = (
            self._get_any_custom_field(
                api_job,
                "CompensationType"
            )
            or ""
        )

        return job

    def _generate_job_key(
        self,
        job
    ):

        job_id = (
            getattr(
                job,
                "job_id",
                ""
            )
            or ""
        ).strip().lower()

        if job_id:

            return (
                "job_id",
                job_id
            )

        job_url = (
            getattr(
                job,
                "job_url",
                ""
            )
            or ""
        ).strip().lower()

        if job_url:

            return (
                "job_url",
                job_url
            )

        return (

            "job_fields",

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