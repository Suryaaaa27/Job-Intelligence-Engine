import os
import tempfile
from playwright.sync_api import sync_playwright

def generate_pdf_from_html(html_content: str, output_pdf_path: str) -> None:
    """
    Takes an HTML string and generates an A4 PDF using Playwright Chromium.
    Saves the resulting PDF to output_pdf_path.
    """
    
    # We write the HTML to a temporary file so Playwright can navigate to it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp_file:
        tmp_file.write(html_content)
        tmp_filepath = tmp_file.name

    try:
        with sync_playwright() as p:
            # Launch chromium in headless mode
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to the temporary HTML file
            page.goto(f"file:///{os.path.abspath(tmp_filepath)}")
            
            # Wait for any potential rendering (e.g. fonts), 
            # though our CSS is embedded so it should be fast
            page.wait_for_load_state("networkidle")
            
            # Generate the PDF
            page.pdf(
                path=output_pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "0in", "right": "0in", "bottom": "0in", "left": "0in"} # Margins handled in CSS @page
            )
            
            browser.close()
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)
