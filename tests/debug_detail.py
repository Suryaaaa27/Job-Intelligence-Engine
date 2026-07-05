from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(
        "https://www.hays.com/job-search?q=Machine+Learning+Engineer",
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(5000)

    # Click first job
    page.locator("lib-sb-job-card").first.click()

    page.wait_for_timeout(3000)

    # Save complete HTML after clicking
    with open(
        "data/detail_page.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(page.content())

    print("Saved detail_page.html")

    browser.close()