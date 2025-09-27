"""
This script creates an agent that can scrape a website using CrewAI the ScrapeWebsiteTool.

Resources:
https://docs.crewai.com/en/tools/web-scraping/scrapewebsitetool
"""

from crewai import Agent, Crew, Task
from crewai_tools import ScrapeWebsiteTool


def create_agent(website_url: str) -> Agent:
    """
    Create an agent that can scrape a website
    Args:
        website_url: The URL of the website to scrape
    Returns:
        An agent that can scrape the website
    """

    scrape_website_tool = ScrapeWebsiteTool(website_url=website_url)

    agent = Agent(
        role="Website Scraper",
        goal="Given a website, scrape the content",
        backstory="You are a helpful assistant that scrapes websites",
        verbose=True,
        llm="gpt-4o-mini",
        max_iter=1,
        max_retry_limit=2,
        respect_context_window=True,
        reasoning=False,
        tools=[scrape_website_tool],
    )

    return agent


def create_task(agent: Agent) -> Task:
    """
    Create a task that can scrape a website
    Args:
        agent: The agent that can scrape the website
    Returns:
        A task that can scrape the website
    """

    description = "You are an expert assistant specializing in web data extraction and analysis. \
        Your task is to thoroughly scrape the provided website, identify and extract the most relevant and valuable information, \
        and present a clear, concise, and well-organized summary of the website's content. Focus on capturing the main topics, key sections, \
        important data points, and any notable features or insights presented on the site. Avoid copying large blocks of text verbatim; instead, \
        paraphrase and synthesize the information to ensure clarity and coherence. If the website contains structured data such as tables, lists, \
        or infographics, summarize their contents and explain their significance. Your summary should be accessible to someone who has not visited \
        the website, providing them with a comprehensive understanding of its purpose, structure, and core content."

    task = Task(
        description=description,
        expected_output="A summary of the website's content",
        agent=agent,
    )
    return task


def create_crew(agent: Agent, task: Task) -> Crew:
    """
    Create a crew that can scrape a website
    Args:
        agent: The agent that can scrape the website
        task: The task that the agent needs to complete
    Returns:
        A crew that can scrape the website
    """

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )

    return crew


def main():
    agent = create_agent(
        website_url="https://www.crewai.com/",
    )
    task = create_task(agent)
    crew = create_crew(agent, task)
    crew.kickoff()


if __name__ == "__main__":
    main()
