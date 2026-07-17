import re
from datetime import datetime


# ============================================================
# BASIC TEXT CLEANING
# ============================================================

def clean_text(text):

    if text is None:

        return ""

    text = re.sub(
        r"<.*?>",
        "",
        str(text)
    )

    return " ".join(
        text.split()
    ).strip()


# ============================================================
# LOCATION STANDARDIZATION
# ============================================================

def standardize_location(location):

    if not location:

        return ""

    location = str(
        location
    ).strip()

    if location.lower() in [
        "remote",
        "anywhere",
        "work from home",
        "wfh"
    ]:

        return "Remote"

    return ", ".join(

        part.strip().title()

        for part in location.split(",")

        if part.strip()

    )


# ============================================================
# DATE STANDARDIZATION
# ============================================================

def standardize_date(date_str):

    if not date_str:

        return ""

    date_str = str(
        date_str
    ).strip()

    formats = (

        "%Y-%m-%d",

        "%d/%m/%Y",

        "%m/%d/%Y",

        "%B %d, %Y"

    )

    for fmt in formats:

        try:

            return datetime.strptime(
                date_str,
                fmt
            ).strftime(
                "%Y-%m-%d"
            )

        except ValueError:

            continue

    return " ".join(
        date_str.split()
    ).strip()


# ============================================================
# DESCRIPTION CLEANING
# ============================================================

def clean_description(text):
    """
    Clean job descriptions while preserving section structure
    and meaningful line breaks.
    """

    if not text:

        return ""

    text = re.sub(
        r"<[^>]+>",
        "",
        str(text)
    )

    lines = []

    for line in text.splitlines():

        line = re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        if line:

            lines.append(
                line
            )

    return "\n".join(
        lines
    )


# ============================================================
# SAFE FIELD ACCESS
# ============================================================

def get_job_value(
    job_obj,
    keys,
    default=None
):

    if isinstance(
        keys,
        str
    ):

        keys = [
            keys
        ]

    for key in keys:

        if isinstance(
            job_obj,
            dict
        ):

            value = job_obj.get(
                key
            )

        else:

            value = getattr(
                job_obj,
                key,
                None
            )

        if value is not None:

            if isinstance(
                value,
                str
            ):

                if value.strip():

                    return value

            else:

                return value

    return default


# ============================================================
# SALARY EXTRACTION
# ============================================================

def extract_salary(text):

    if not text:

        return {

            "min_salary": None,

            "max_salary": None,

            "currency": None

        }

    currency_map = {

        "$": "USD",

        "£": "GBP",

        "€": "EUR",

        "usd": "USD",

        "gbp": "GBP",

        "eur": "EUR"

    }

    currency = None

    text_lower = str(
        text
    ).lower()

    for symbol, name in currency_map.items():

        if symbol in text_lower:

            currency = name

            break

    cleaned_text = re.sub(
        r"(?<=\d),(?=\d)",
        "",
        str(text)
    )

    range_regex = (
        r"(?:[\$£€]|USD|GBP|EUR)?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(k|K)?\s*"
        r"(?:-|to)\s*"
        r"(?:[\$£€]|USD|GBP|EUR)?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(k|K)?\b"
    )

    match = re.search(
        range_regex,
        cleaned_text,
        re.IGNORECASE
    )

    if match:

        try:

            min_value = float(
                match.group(1)
            )

            max_value = float(
                match.group(3)
            )

            if match.group(2):

                min_value *= 1000

            if match.group(4):

                max_value *= 1000

            if (
                min_value > 0
                and max_value > 0
            ):

                return {

                    "min_salary": min_value,

                    "max_salary": max_value,

                    "currency": currency

                }

        except (
            TypeError,
            ValueError
        ):

            pass

    single_regex = (
        r"(?:[\$£€]|USD|GBP|EUR)\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(k|K)?\b"
    )

    match = re.search(
        single_regex,
        cleaned_text,
        re.IGNORECASE
    )

    if match:

        try:

            value = float(
                match.group(1)
            )

            if match.group(2):

                value *= 1000

            if value > 0:

                return {

                    "min_salary": value,

                    "max_salary": value,

                    "currency": currency

                }

        except (
            TypeError,
            ValueError
        ):

            pass

    return {

        "min_salary": None,

        "max_salary": None,

        "currency": currency

    }


# ============================================================
# JOB TYPE INFERENCE
# ============================================================

def standardize_job_type(
    title,
    description
):
    """
    Infer employment type only when authoritative scraper
    metadata is unavailable.
    """

    combined = (
        f"{title} {description}"
    ).lower()

    if (
        "part-time" in combined
        or "part time" in combined
    ):

        return "Part-time"

    if (
        "contract" in combined
        or "contractor" in combined
        or "freelance" in combined
    ):

        return "Contract"

    if (
        "internship" in combined
        or re.search(
            r"\bintern\b",
            combined
        )
    ):

        return "Internship"

    if (
        "temporary" in combined
        or re.search(
            r"\btemp\b",
            combined
        )
    ):

        return "Temporary"

    return ""


# ============================================================
# JOB CLEANING
# ============================================================

def clean_job(job_obj):
    """
    Normalize and clean a scraped job while preserving canonical
    Job model fields.

    Authoritative scraper metadata always takes precedence over
    heuristic inference.
    """

    raw_description = get_job_value(

        job_obj,

        "description",

        ""

    )

    description = clean_description(
        raw_description
    )

    title = clean_text(

        get_job_value(

            job_obj,

            [
                "title",
                "job_title"
            ],

            "Unknown Title"

        )

    )

    company = clean_text(

        get_job_value(

            job_obj,

            [
                "company",
                "company_name"
            ],

            "Unknown Company"

        )

    )

    source = clean_text(

        get_job_value(

            job_obj,

            [
                "source",
                "source_platform"
            ],

            "Unknown"

        )

    )

    job_url = clean_text(

        get_job_value(

            job_obj,

            [
                "url",
                "job_url"
            ],

            ""

        )

    )

    application_url = clean_text(

        get_job_value(

            job_obj,

            [
                "application_url",
                "apply_url"
            ],

            job_url

        )

    )

    location = standardize_location(

        get_job_value(

            job_obj,

            "location",

            ""

        )

    )

    # ========================================================
    # AUTHORITATIVE SCRAPER METADATA
    # ========================================================

    employment_type = clean_text(

        get_job_value(

            job_obj,

            [
                "employment_type",
                "job_type"
            ],

            ""

        )

    )

    if not employment_type:

        employment_type = standardize_job_type(

            title,

            description

        )

    workplace_type = clean_text(

        get_job_value(

            job_obj,

            "workplace_type",

            ""

        )

    )

    salary = clean_text(

        get_job_value(

            job_obj,

            "salary",

            ""

        )

    )

    existing_min_salary = get_job_value(

        job_obj,

        "min_salary",

        None

    )

    existing_max_salary = get_job_value(

        job_obj,

        "max_salary",

        None

    )

    existing_currency = get_job_value(

        job_obj,

        "currency",

        None

    )

    salary_info = extract_salary(

        salary
        or description

    )

    min_salary = (

        existing_min_salary

        if existing_min_salary is not None

        else salary_info[
            "min_salary"
        ]

    )

    max_salary = (

        existing_max_salary

        if existing_max_salary is not None

        else salary_info[
            "max_salary"
        ]

    )

    currency = (

        existing_currency

        or salary_info[
            "currency"
        ]

    )

    # ========================================================
    # CANONICAL JOB DOCUMENT
    # ========================================================

    return {

        "job_id": clean_text(

            get_job_value(

                job_obj,

                "job_id",

                ""

            )

        ),

        "title": title,

        "company": company,

        "company_website": clean_text(

            get_job_value(

                job_obj,

                "company_website",

                ""

            )

        ),

        "description": description,

        "source": source,

        "url": job_url,

        "application_url": application_url,

        "location": location,

        "country": clean_text(

            get_job_value(

                job_obj,

                "country",

                ""

            )

        ),

        "state": clean_text(

            get_job_value(

                job_obj,

                "state",

                ""

            )

        ),

        "city": clean_text(

            get_job_value(

                job_obj,

                "city",

                ""

            )

        ),

        "workplace_type": workplace_type,

        "employment_type": employment_type,

        "job_type": employment_type,

        "salary": salary,

        "min_salary": min_salary,

        "max_salary": max_salary,

        "currency": currency,

        "salary_period": clean_text(

            get_job_value(

                job_obj,

                [
                    "salary_period",
                    "salary_frequency"
                ],

                ""

            )

        ),

        "posted_date": standardize_date(

            get_job_value(

                job_obj,

                "posted_date",

                ""

            )

        ),

        "skills": get_job_value(

            job_obj,

            "skills",

            []

        ),

        "responsibilities": get_job_value(

            job_obj,

            "responsibilities",

            []

        ),

        "experience": get_job_value(

            job_obj,

            "experience",

            ""

        ),

        "education": get_job_value(

            job_obj,

            "education",

            []

        ),

        "recruiter_name": clean_text(

            get_job_value(

                job_obj,

                "recruiter_name",

                ""

            )

        ),

        "recruiter_phone": clean_text(

            get_job_value(

                job_obj,

                "recruiter_phone",

                ""

            )

        ),

        "recruiter_office": clean_text(

            get_job_value(

                job_obj,

                "recruiter_office",

                ""

            )

        ),

        "requirements": get_job_value(

            job_obj,

            "requirements",

            []

        ),

        "benefits": get_job_value(

            job_obj,

            "benefits",

            []

        ),

        "recruiter_name": get_job_value(

            job_obj,

            "recruiter_name",

            ""

        ),

        "recruiter_email": get_job_value(

            job_obj,

            "recruiter_email",

            ""

        ),

        "recruiter_phone": get_job_value(

            job_obj,

            "recruiter_phone",

            ""

        ),

        "recruiter_office": get_job_value(

            job_obj,

            "recruiter_office",

            ""

        ),

        "predicted_role": get_job_value(

            job_obj,

            "predicted_role",

            None

        ),

        "role_predictions": get_job_value(

            job_obj,

            "role_predictions",

            []

        ),

        "match_score": get_job_value(

            job_obj,

            "match_score",

            None

        ),

        "extracted_skills": get_job_value(

            job_obj,

            "extracted_skills",

            []

        ),

        "relevance_scores": get_job_value(

            job_obj,

            "relevance_scores",

            {}

        ),

        "scrape_session": clean_text(

            get_job_value(

                job_obj,

                "scrape_session",

                ""

            )

        )

    }