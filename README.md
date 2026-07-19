# Job Intelligence Engine

A lightweight end-to-end pipeline for:
- scraping and filtering jobs,
- parsing resumes,
- matching a resume against a job description,
- and generating ATS-friendly resume suggestions.

## Quick start

1. Install dependencies

```bash
pip install -r requirements.txt
pip install -r resume_parser/requirements.txt
```

2. Run the CV parser and save the output as CV.json in the data folder

```bash
python -m resume_parser.parser path/to/resume.pdf --pretty -o data/CV.json
```

If you are using a DOCX file, use:

```bash
python -m resume_parser.parser path/to/resume.docx --pretty -o data/CV.json
```

This creates the parsed CV JSON required by the rest of the pipeline.

3. Clean the JD for duplis and run the JD comparison step

```bash
python main.py

python compare_cv_jd.py
```

This takes the CV JSON from the data folder, combines it with the job data, and converts everything into structured match-ready data.

4. Generate the optimized CV output

Set your Gemini API key first:

```powershell
$env:GOOGLE_API_KEY = "YOUR_API_KEY"
```

Then run:

```bash
python generate_optimized_resume.py
```

This produces the final optimized CV JSON output in the data folder.

5. Optional: inspect the generated structured data directly

```python
from services.resume_optimizer.service import load_resume_from_file

resume = load_resume_from_file("path/to/resume.pdf")
```

## Resume parser workflow

The parser follows a simple pipeline:

```text
PDF/DOCX/JSON resume
  -> extractors
  -> section splitter
  -> field extractors
  -> structured resume schema
```

It extracts the following fields:

- contact info: full name, email, phone, LinkedIn, GitHub, location
- summary
- skills
- experience entries with titles, companies, dates, bullets, and raw text
- projects
- education
- certifications
- warnings for sections that could not be detected

## Output schema example

```json
{
  "contact_info": {
    "full_name": "Ada Lovelace",
    "email": "ada@example.com",
    "phone": null,
    "location": null,
    "linkedin": null,
    "github": null,
    "portfolio": null
  },
  "summary": "Software engineer with Python and ML experience.",
  "skills": ["Python", "Machine Learning"],
  "experience": [
    {
      "job_title": "Software Engineer",
      "company": "Acme",
      "start_date": "2023",
      "end_date": "Present",
      "is_current": true,
      "bullets": ["Built ML features"],
      "raw_text": "..."
    }
  ],
  "projects": [],
  "education": [],
  "certifications": [],
  "raw_sections": {},
  "warnings": [],
  "source_file": "resume.pdf",
  "source_file_type": "pdf"
}
```

## Notes and limitations

- The parser works with PDF, DOCX, and JSON resume inputs.
- Resume optimization uses Gemini, so the GOOGLE_API_KEY environment variable is required for that step.
- If needed, you can override the default model with RESUME_OPTIMIZER_MODEL.
- Parsing is heuristic rather than ML-based, so complex layouts, scanned PDFs, and unusual section headers may need manual review.

## Main folders

- data/: sample jobs, resumes, and generated outputs
- preprocessing/: cleaning and deduplication
- filtering/: scoring and role classification
- resume_parser/: PDF/DOCX resume parsing
- services/resume_optimizer/: matching, ATS scoring, and resume optimization
- tests/: regression and integration checks

