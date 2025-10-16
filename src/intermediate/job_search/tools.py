import json
import os

import pdfplumber
import PyPDF2
import requests
from crewai.tools import tool


@tool("Resume Parser Tool")
def parse_resume(file_path: str) -> str:
    """
    Parse resume PDF and extract text content.

    Args:
        file_path: Path to the resume PDF file

    Returns
        Extracted text content from the resume
    """
    if not os.path.exists(file_path):
        return (
            f"Error: Resume file not found at {file_path}. Please check the file path."
        )

    try:
        # Try using pdfplumber first (better text extraction)
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            if text.strip():
                return f"✅ Resume parsed successfully!\n\nResume Content:\n{text}"
    except Exception as e:
        print(f"pdfplumber failed: {e}, trying PyPDF2...")

    try:
        # Fallback to PyPDF2
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            if text.strip():
                return f"✅ Resume parsed successfully!\n\nResume Content:\n{text}"
            else:
                return "Error: Could not extract text from PDF. The file might be image-based or corrupted."

    except Exception as e:
        return f"Error: Failed to parse resume PDF. {str(e)}"


@tool("Job Search Tool")
def search_jobs(input_json: str) -> str:
    """
    Search for job listings using the Adzuna API.

    Args:
        input_json: JSON string with schema {'role': '<role>', 'location': '<location>', 'num_results': <number>}

    Returns:
        Formatted string of job listings
    """
    try:
        # Check if required environment variables are loaded
        required_vars = ["OPENAI_API_KEY", "ADZUNA_APP_ID", "ADZUNA_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            error_msg = "❌ Missing required environment variables in .env file:\n"
            for var in missing_vars:
                error_msg += f"   - {var}\n"
            error_msg += "\n📝 Create a .env file in your project directory with:\n"
            error_msg += "OPENAI_API_KEY=your_openai_api_key_here\n"
            error_msg += "ADZUNA_APP_ID=your_adzuna_app_id_here\n"
            error_msg += "ADZUNA_API_KEY=your_adzuna_api_key_here"
            return error_msg

        input_data = json.loads(input_json)
        role = input_data["role"]
        location = input_data["location"]
        num_results = input_data.get("num_results", 5)
    except (json.JSONDecodeError, KeyError) as e:
        return """Error: The tool accepts input in JSON format with the 
                following schema: {'role': '<role>', 'location': '<location>', 'num_results': <number>}. 
                Ensure to format the input accordingly."""

    app_id = os.getenv("ADZUNA_APP_ID")
    api_key = os.getenv("ADZUNA_API_KEY")

    if not app_id or not api_key:
        return "Error: Please set ADZUNA_APP_ID and ADZUNA_API_KEY in your .env file."

    base_url = "http://api.adzuna.com/v1/api/jobs"
    url = f"{base_url}/us/search/1"

    params = {
        "app_id": app_id,
        "app_key": api_key,
        "results_per_page": num_results,
        "what": role,
        "where": location,
        "content-type": "application/json",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        jobs_data = response.json()

        job_listings = []
        for job in jobs_data.get("results", []):
            job_details = {
                "title": job.get("title", "N/A"),
                "company": job.get("company", {}).get("display_name", "N/A"),
                "location": job.get("location", {}).get("display_name", "N/A"),
                "salary": job.get("salary_min", "Not specified"),
                "description": (
                    job.get("description", "")[:300] + "..."
                    if job.get("description")
                    else "No description"
                ),
                "url": job.get("redirect_url", "N/A"),
            }

            formatted_job = f"""
Title: {job_details['title']}
Company: {job_details['company']}
Location: {job_details['location']}
Salary: {job_details['salary']}
Description: {job_details['description']}
URL: {job_details['url']}
---"""
            job_listings.append(formatted_job)

        return (
            "\n".join(job_listings)
            if job_listings
            else "No jobs found for the specified criteria."
        )

    except requests.exceptions.HTTPError as err:
        return f"HTTP Error: {err}"
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
