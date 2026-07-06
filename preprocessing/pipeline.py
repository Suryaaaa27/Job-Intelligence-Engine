import json
import os
from preprocessing.cleaner import clean_job
from preprocessing.deduplicator import remove_duplicates
from schemas.job_schema import Job


def run_preprocessing_pipeline(input_path, output_path):
    # 1. Load the raw JSON data
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    print(f"Loaded {len(raw_data)} raw jobs.")

    # 2. Clean individual records & map them to your Job objects
    job_objects = []
    for raw_job in raw_data:
        # Standardize and handle missing values
        cleaned_dict = clean_job(raw_job)

        # Instantiate your exact Job schema
        job_obj = Job()
        job_obj.title = cleaned_dict["title"]
        job_obj.company = cleaned_dict["company"]
        job_obj.location = cleaned_dict["location"]
        job_obj.description = cleaned_dict["description"]
        job_obj.source = cleaned_dict["source"]
        job_obj.url = cleaned_dict["url"]
        job_obj.posted_date = cleaned_dict["posted_date"]
        job_obj.role_predictions = cleaned_dict["role_predictions"]
        job_obj.extracted_skills = cleaned_dict["extracted_skills"]
        job_obj.relevance_scores = cleaned_dict["relevance_scores"]

        job_objects.append(job_obj)

    # 3. Deduplicate using the updated structured list
    unique_jobs = remove_duplicates(job_objects)
    print(f"Deduplication complete. Retained {len(unique_jobs)} unique jobs.")

    # 4. Serialize back into standard dictionaries to save out
    output_data = [job.__dict__ for job in unique_jobs]

    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print(f"Successfully saved clean & consistent data to {output_path}")


if __name__ == "__main__":
    # Relative paths starting from the project workspace root
    INPUT_FILE = "data/raw_jobs.json"
    OUTPUT_FILE = "data/processed_jobs.json"
    run_preprocessing_pipeline(INPUT_FILE, OUTPUT_FILE)