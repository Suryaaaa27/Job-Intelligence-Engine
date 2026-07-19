# Resume Renderer

This module handles rendering an optimized resume JSON into both HTML and PDF formats suitable for Applicant Tracking Systems (ATS).

## Components

- **data_adapter.py**: Normalizes the raw JSON input from the pipeline and merges optimized fields.
- **html_renderer.py**: Utilizes Jinja2 templates to convert the normalized data into an ATS-friendly HTML format.
- **pdf_generator.py**: Converts the rendered HTML into an A4, text-selectable PDF using Playwright Chromium.
- **main.py**: The central orchestration script to execute the complete rendering pipeline.

## Templates

Templates are stored in the `templates/` directory. The default is `general.html`, which provides a clean, single-column, standard ATS-friendly structure. 
More templates can be added by simply creating new `.html` files in the `templates` directory and updating the template selection logic if needed.

## Setup & Usage

Ensure dependencies are installed:
```bash
pip install -r ../requirements.txt
playwright install chromium
```

To run the pipeline on an optimized resume JSON:
```bash
python -m resume_renderer.main data/optimized_resume_output.json
```

```How to use them
You can now use any of these templates by passing the --template flag to the CLI. For example:

To use the modern template:
``
bash

python -m resume_renderer.main data/optimized_resume_output.json --template modern.html

To use the compact template:

bash


python -m resume_renderer.main data/optimized_resume_output.json --template compact.html
To use the classic template:

bash


python -m resume_renderer.main data/optimized_resume_output.json --template classic.html
The output will automatically be saved to output/optimized_resume.html and output/optimized_resume.pdf just like before, but rendered with your chosen design.