import os

from crewai import Agent
from crewai.llm import LLM
from tools import exa_search_tool

os.environ["EXA_API_KEY"] = os.getenv("EXA_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm = LLM(model="gpt-4o", temperature=0.9)

# Agent 1: Content Explorer - Gathers information about the topic from the internet
content_explorer = Agent(
    role="content explorer",
    goal="Gather and provide latest information about the topic from internet",
    llm=llm,
    verbose=True,
    backstory=(
        "You are an expert researcher, who can gather detailed information about a topic.\
                  Gather at least 10 information."
    ),
    tools=[exa_search_tool()],
    cache=True,
    max_iter=5,
)

# Agent 2: Script Writer - Creates a script out of the information
script_writer = Agent(
    role="Script Writer",
    goal="With the details given to you create an interesting conversational script out of it",
    llm=llm,
    verbose=True,
    backstory=(
        "You are an expert in literature. You are very good in creating conversations with the given chain of information.\
        Tell as a script in 200 words."
    ),
)
