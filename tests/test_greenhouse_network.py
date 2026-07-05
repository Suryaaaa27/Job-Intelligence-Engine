from playwright.sync_api import sync_playwright


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    def handle_response(response):

        url = response.url

        if "graphql" in url.lower() or "api" in url.lower():

            print("\n=====================")
            print(response.status)
            print(url)

    page.on("response", handle_response)

    page.goto(
        "https://my.greenhouse.io/jobs?query=AI",
        wait_until="networkidle"
    )

    page.wait_for_timeout(10000)

    browser.close()