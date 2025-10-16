import os

from crewai import Agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools import search_jobs

load_dotenv()

# Verify API key is set from .env file
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

llm = ChatOpenAI(model="gpt-4.1-2025-04-14")


def create_agents(resume_content: str = ""):
    """
    Create all AI agents with enhanced capabilities

    Args:
        resume_content: Parsed resume content for personalized recommendations

    Returns:
        Dictionary containing all agents
    """
    resume_context = (
        f"\n\nCandidate's Resume Content:\n{resume_content}" if resume_content else ""
    )

    job_searcher_agent = Agent(
        role="Senior Job Search Specialist",
        goal="Find the most relevant job opportunities that match the candidate's profile and specified criteria",
        backstory=f"""You are an expert job search specialist with extensive experience in 
        identifying high-quality job opportunities. You excel at understanding both job requirements 
        and candidate profiles to find the perfect matches.{resume_context}""",
        verbose=True,
        llm=llm,
        allow_delegation=True,
        tools=[search_jobs],
    )

    skills_development_agent = Agent(
        role="Personalized Skills Development Advisor",
        goal="Analyze job requirements against the candidate's current skills and provide targeted development recommendations",
        backstory=f"""You are a seasoned career development expert who specializes in 
        identifying skill gaps by comparing job requirements with candidate backgrounds. 
        You create personalized learning paths based on individual experience and career goals.{resume_context}""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
    )

    interview_preparation_coach = Agent(
        role="Personalized Interview Preparation Expert",
        goal="Prepare candidates for interviews by leveraging their specific background and experience",
        backstory=f"""You are a professional interview coach who creates personalized interview 
        strategies. You help candidates highlight their unique strengths and address potential 
        weaknesses based on their specific background and target roles.{resume_context}""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
    )

    career_advisor = Agent(
        role="Personalized Career Strategy Advisor",
        goal="Provide strategic career advice tailored to the candidate's specific background and goals",
        backstory=f"""You are a senior career strategist who creates personalized career 
        advancement plans. You understand how to position candidates based on their unique 
        background, optimize their personal brand, and create targeted networking strategies.{resume_context}""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
    )

    return {
        "job_searcher": job_searcher_agent,
        "skills_development": skills_development_agent,
        "interview_prep": interview_preparation_coach,
        "career_advisor": career_advisor,
    }
