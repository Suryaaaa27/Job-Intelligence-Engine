1. Every scraper inherits BaseScraper.

2. Every scraper returns List[Job].

3. Never return dictionaries.

4. Never modify the Job model.

5. Use logging.

6. Follow HaysScraper as the reference implementation.

# Run only these:
python -m tests.test_query_manager

python -m tests.test_taxonomy

python -m tests.test_hays

python -m tests.test_unified_scraper

