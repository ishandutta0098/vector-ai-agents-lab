"""
This script creates an agent that can detect conflicts in a text using CrewAI.
"""

import os

from crewai import Agent, Crew, Task
from crewai.llm import LLM
from dotenv import load_dotenv

load_dotenv()

# Create an instance of OpenAI's LLM
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def create_agent() -> Agent:
    """
    Create an agent that can detect conflicts in a text
    Returns:
        An agent that can detect conflicts in a text
    """

    llm = LLM(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=4000,
        timeout=120,
    )

    # Define your agent with OpenAI LLM
    agent = Agent(
        role="Critical Thinker",
        goal="Analyse the text and identify if any conflicting information within",
        llm=llm,
        backstory=(
            "You are a critical thinker who understands details very well and expert negotiator. \
            You can identify conflicting statements, information in given text"
        ),
    )

    return agent


def create_task(agent: Agent) -> Task:
    """
    Create a task that can detect conflicts in a text
    Args:
        agent: The agent that can detect conflicts in a text
    Returns:
        A task that can detect conflicts in a text
    """

    task = Task(
        description=(
            "Find if there are any conflicting statement / information in text. \n Text : \n{text}"
        ),
        expected_output="Respond with 'conflict' / 'no conflict'",
        agent=agent,
    )
    return task


def create_crew(agent: Agent, task: Task) -> Crew:
    """
    Create a crew that can detect conflicts in a text
    Args:
        agent: The agent that can detect conflicts in a text
        task: The task that the agent needs to complete
    Returns:
        A crew that can detect conflicts in a text
    """
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    return crew


def main():
    agent = create_agent()
    task = create_task(agent)
    crew = create_crew(agent, task)

    Text = "After a long day at office, I was going back home in the late evening. Then, I met my friend on the way to office."
    # Text = "I love to travel to new places and explore the culture and food of the place."
    # Text = "I went to the library to study, but I forgot to bring my books and studied all of them."
    # Text = "She said she has never been to Paris, yet she described the Eiffel Tower in great detail from her last trip."

    crew.kickoff(inputs={"text": Text})


if __name__ == "__main__":
    main()
