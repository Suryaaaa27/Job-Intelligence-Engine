import argparse
import sys
import os

from resume_renderer.data_adapter import load_optimized_json, normalize_resume_data
from resume_renderer.html_renderer import render_html
from resume_renderer.pdf_generator import generate_pdf_from_html

def main():
    parser = argparse.ArgumentParser(description="Render optimized resume JSON into HTML and PDF.")
    parser.add_argument("input_json", help="Path to the optimized resume JSON file.")
    parser.add_argument("--template", default="general.html", help="Template name to use (default: general.html)")
    parser.add_argument("--outdir", default="output", help="Output directory for generated files (default: output)")
    
    args = parser.parse_args()
    
    input_filepath = args.input_json
    if not os.path.exists(input_filepath):
        print(f"Error: Input JSON file not found at '{input_filepath}'", file=sys.stderr)
        sys.exit(1)
        
    outdir = args.outdir
    if not os.path.exists(outdir):
        try:
            os.makedirs(outdir)
        except Exception as e:
            print(f"Error: Could not create output directory '{outdir}': {e}", file=sys.stderr)
            sys.exit(1)

    print(f"Loading data from {input_filepath}...")
    try:
        raw_data = load_optimized_json(input_filepath)
        normalized_data = normalize_resume_data(raw_data)
    except Exception as e:
        print(f"Error: Failed to load or normalize JSON data: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Rendering HTML using template '{args.template}'...")
    try:
        html_content = render_html(normalized_data, template_name=args.template)
    except Exception as e:
        print(f"Error: HTML rendering failed: {e}", file=sys.stderr)
        sys.exit(1)
        
    html_out_path = os.path.join(outdir, "optimized_resume.html")
    try:
        with open(html_out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML successfully written to: {html_out_path}")
    except Exception as e:
        print(f"Error: Failed to write HTML output: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("Generating PDF...")
    pdf_out_path = os.path.join(outdir, "optimized_resume.pdf")
    try:
        generate_pdf_from_html(html_content, pdf_out_path)
        print(f"PDF successfully written to: {pdf_out_path}")
    except Exception as e:
        print(f"Error: PDF generation failed: {e}", file=sys.stderr)
        sys.exit(1)

    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
