import os

from crewai import Agent
from crewai.llm import LLM
from dotenv import load_dotenv

load_dotenv()

from tools import exa_search_tool, log_reader_tool

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm = LLM(
    model="gpt-4o",
    temperature=0.1,
    max_tokens=4000,
    timeout=120,  # 2 minutes timeout
)


def system_template_devops():
    """Custom system template for DevOps agents"""
    return """You are an expert DevOps engineer with extensive experience in:
    - Infrastructure automation and orchestration
    - Container technologies (Docker, Kubernetes)
    - CI/CD pipelines and deployment strategies
    - Monitoring, logging, and observability
    - Cloud platforms (AWS, GCP, Azure)
    - Security best practices and compliance
    
    Always provide:
    1. Detailed technical analysis
    2. Step-by-step solutions
    3. Best practices and recommendations
    4. Risk assessment and mitigation strategies
    5. References to official documentation
    
    Focus on practical, production-ready solutions."""


# Agent 1: Log Analyzer - Analyzes log files to identify issues
log_analyzer = Agent(
    role="DevOps Log Analyzer",
    goal="Analyze log files to identify and extract specific issues, errors, and failure patterns",
    llm=llm,
    backstory="""You are a senior DevOps engineer with 10 years of experience in 
    analyzing production logs and identifying critical issues. You excel at parsing 
    through complex log files, identifying error patterns, extracting relevant error 
    messages, and determining the root cause of failures from log data.""",
    tools=[log_reader_tool],
    verbose=True,
    max_iter=3,
    max_rpm=10,  # Rate limiting: max 10 requests per minute
    memory=True,  # Enable memory for learning from previous analyses
    system_template=system_template_devops(),
    max_execution_time=300,  # 5 minutes max execution time
    respect_context_window=True,  # Respect model's context window
)

# Agent 2: Issue Investigator - Searches for solutions online
issue_investigator = Agent(
    role="DevOps Issue Investigator",
    goal="Investigate identified issues by searching documentation, forums, and known solutions online",
    llm=llm,
    backstory="""You are a DevOps troubleshooting specialist who excels at quickly 
    finding solutions to technical problems. You know how to search effectively for 
    similar issues, identify reliable sources, and gather comprehensive information 
    about error patterns and their solutions.""",
    tools=[exa_search_tool],
    verbose=True,
    max_iter=5,
    max_rpm=15,  # Higher rate limit for search operations
    memory=True,  # Remember previous search patterns and results
    system_template=system_template_devops(),
    max_execution_time=600,  # 10 minutes for thorough investigation
    respect_context_window=True,
)

# Agent 3: Solution Specialist - Provides actionable solutions
solution_specialist = Agent(
    role="DevOps Solution Specialist",
    goal="Provide clear, actionable solutions with step-by-step instructions based on investigation findings",
    llm=llm,
    backstory="""You are a DevOps solutions architect who specializes in creating 
    reliable, step-by-step remediation plans for infrastructure and deployment issues. 
    You always provide official documentation references, tested solutions, and 
    preventive measures to avoid future occurrences.""",
    verbose=True,
    max_iter=4,
    max_rpm=8,  # Conservative rate limit for solution generation
    memory=True,  # Remember successful solutions for similar issues
    system_template=system_template_devops(),
    max_execution_time=450,  # 7.5 minutes for comprehensive solutions
    respect_context_window=True,
)
