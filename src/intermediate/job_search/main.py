#!/usr/bin/env python3
"""
Enhanced CrewAI Job Search Agent System with Resume Analysis
A comprehensive AI-powered job search automation system that analyzes your resume
for personalized recommendations using CrewAI framework.

Required .env file format:
OPENAI_API_KEY=your_openai_api_key_here
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_API_KEY=your_adzuna_api_key_here

Installation:
pip install crewai langchain langchain-openai requests python-dotenv PyPDF2 pdfplumber
"""

import json
import os
from datetime import datetime

import pdfplumber
import PyPDF2
from agents import create_agents, llm
from crewai import Crew, Process
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tasks import create_tasks

# Load environment variables from .env file
load_dotenv()


class EnhancedJobSearchAgentSystem:
    """Enhanced Job Search Agent System with Resume Analysis"""

    def __init__(self, resume_path: str = None):
        """
        Initialize the Enhanced Job Search Agent System

        Args:
            resume_path: Path to the resume PDF file for personalized analysis
        """
        self.resume_path = resume_path
        self.resume_content = ""

        # Parse resume if provided
        if resume_path:
            self.parse_resume()

        # Create agents and tasks
        self.agents = create_agents(self.resume_content)
        self.tasks = create_tasks(self.agents, self.resume_content)
        self.setup_crew()

    def parse_resume(self):
        """Parse the resume and store content for agent context"""
        if self.resume_path:
            print(f"📄 Parsing resume from: {self.resume_path}")
            self.resume_content = self._parse_resume_direct(self.resume_path)
            if "✅ Resume parsed successfully!" in self.resume_content:
                print("✅ Resume parsed and ready for analysis!")
            else:
                print("❌ Resume parsing failed. Proceeding without resume context.")
                self.resume_content = ""

    def _parse_resume_direct(self, file_path: str) -> str:
        """Direct resume parsing function without tool decorator"""
        if not os.path.exists(file_path):
            return f"Error: Resume file not found at {file_path}. Please check the file path."

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

    def setup_crew(self):
        """Initialize the CrewAI crew"""
        self.crew = Crew(
            agents=[
                self.agents["job_searcher"],
                self.agents["skills_development"],
                self.agents["interview_prep"],
                self.agents["career_advisor"],
            ],
            tasks=[
                self.tasks["job_search"],
                self.tasks["skills_analysis"],
                self.tasks["interview_prep"],
                self.tasks["career_strategy"],
            ],
            process=Process.hierarchical,
            manager_llm=llm,
            verbose=True,
        )

    def search_jobs(self, role: str, location: str, num_results: int = 5):
        """
        Execute the personalized job search process

        Args:
            role: Job title or role to search for
            location: Geographic location for job search
            num_results: Number of job results to return (default: 5)

        Returns:
            Complete personalized analysis and recommendations from all agents
        """
        print(f"🚀 Starting PERSONALIZED job search for '{role}' in '{location}'...")
        if self.resume_content:
            print("📄 Using resume content for personalized recommendations")
        else:
            print("⚠️  No resume provided - using general recommendations")

        print("📝 This process will:")
        print("   1. Search for relevant job openings")
        print("   2. Compare job requirements with your background")
        print("   3. Create personalized skill development plan")
        print("   4. Prepare customized interview strategies")
        print("   5. Generate targeted career optimization plan")
        print("   6. Provide actionable next steps")
        print("\n" + "=" * 50)

        # Clear previous output file
        with open("task_output.txt", "w") as file:
            file.write(f"PERSONALIZED Job Search Analysis Report\n")
            file.write(f"Role: {role}\n")
            file.write(f"Location: {location}\n")
            file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Resume Analyzed: {'Yes' if self.resume_content else 'No'}\n")
            file.write("=" * 50 + "\n\n")

        # Update the job search task with specific parameters
        search_params = json.dumps(
            {"role": role, "location": location, "num_results": num_results}
        )

        self.tasks[
            "job_search"
        ].description = f"""Search for current job openings for the {role} role in {location} 
        using the Job Search tool. Find {num_results} relevant positions that would be suitable for the candidate's background.
        Use this exact input: {search_params}"""

        try:
            # Execute the crew
            result = self.crew.kickoff()

            print("\n" + "=" * 50)
            print("✅ Personalized job search analysis complete!")
            print("📄 Detailed results saved to 'task_output.txt'")
            if self.resume_content:
                print(
                    "🎯 All recommendations are tailored to your specific background!"
                )
            print("=" * 50)

            return result

        except Exception as e:
            print(f"❌ Error during job search execution: {e}")
            return None


def main():
    """Main function to run the enhanced job search system"""

    print("🔧 Enhanced Job Search System Setup:")
    print("✅ Loading configuration from .env file...")
    print(
        "📦 Required packages: pip install crewai langchain langchain-openai requests python-dotenv PyPDF2 pdfplumber"
    )
    print("\n" + "=" * 50)

    try:
        # Resume file path - using 'resume.pdf' as default
        resume_path = "src/intermediate/job_search/resume.pdf"

        # Check if resume file exists
        if os.path.exists(resume_path):
            print(f"📄 Found resume file: {resume_path}")
            job_search_system = EnhancedJobSearchAgentSystem(resume_path=resume_path)
        else:
            print(f"⚠️  Resume file not found at: {resume_path}")
            print("💡 Proceeding without resume analysis (general recommendations)")
            print(
                "💡 To use resume analysis, place your resume.pdf in the project directory"
            )
            job_search_system = EnhancedJobSearchAgentSystem()

        # Example usage - CUSTOMIZE THESE PARAMETERS
        role = "Senior Data Scientist"
        location = "New York"
        num_results = 5

        # Execute personalized job search
        result = job_search_system.search_jobs(
            role=role, location=location, num_results=num_results
        )

        if result:
            print("\n📊 Final Summary:")
            print(result)

    except ValueError as e:
        print(f"❌ .env Configuration Error: {e}")
        print("💡 Make sure your .env file exists and contains all required API keys")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    main()
