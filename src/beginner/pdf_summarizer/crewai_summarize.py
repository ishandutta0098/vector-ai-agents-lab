"""
This script creates an agent that can summarize a PDF file using CrewAI the PDFSearchTool.

Resources:
https://docs.crewai.com/en/tools/file-document/pdfsearchtool#pdf-rag-search
"""

from crewai import Agent, Crew, Task
from crewai_tools import PDFSearchTool


def create_agent(query: str, pdf_path: str) -> Agent:
    """
    Create an agent that can summarize a PDF file
    Args:
        query: The query to search the PDF file
        pdf_path: The path to the PDF file
    Returns:
        An agent that can summarize the PDF file
    """

    pdf_search_tool = PDFSearchTool(
        query=query,
        pdf=pdf_path,
    )

    agent = Agent(
        role="PDF Summarizer",
        goal="Given a PDF file, summarize the content",
        backstory="You are a helpful assistant that summarizes PDF files",
        verbose=True,
        llm="gpt-4o-mini",
        max_iter=1,
        max_retry_limit=2,
        respect_context_window=True,
        reasoning=False,
        tools=[pdf_search_tool],
    )

    return agent


def create_task(agent: Agent) -> Task:
    """
    Create a task that can summarize a PDF file
    Args:
        agent: The agent that can summarize the PDF file
    Returns:
        A task that can summarize the PDF file
    """

    description = "You are an expert assistant specializing in reading and summarizing PDF documents. \
            Your task is to carefully analyze the provided PDF file, extract the most important points, \
            and generate a clear, concise, and accurate summary. Focus on identifying the main ideas, key arguments, \
            and any significant findings or conclusions presented in the document. Avoid copying text verbatim; instead, \
            paraphrase the content in your own words to ensure clarity and coherence. If the document contains sections, \
            figures, or tables that are crucial to understanding the overall message, include brief explanations of their relevance. \
            Your summary should be accessible to someone who has not read the original PDF, providing them with a comprehensive understanding \
            of its core content and purpose"

    task = Task(
        description=description,
        expected_output="A summary of the PDF file",
        agent=agent,
    )
    return task


def create_crew(agent: Agent, task: Task) -> Crew:
    """
    Create a crew that can summarize a PDF file
    Args:
        agent: The agent that can summarize the PDF file
        task: The task that the agent needs to complete
    Returns:
        A crew that can summarize the PDF file
    """

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )

    return crew


def main():
    agent = create_agent(
        query="What is the main idea of the paper?",
        pdf_path="../../../assets/transformers.pdf",
    )
    task = create_task(agent)
    crew = create_crew(agent, task)
    crew.kickoff()


if __name__ == "__main__":
    main()
