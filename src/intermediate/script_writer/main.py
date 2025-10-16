from agents import content_explorer, script_writer
from crewai import Crew, Process
from tasks import create_a_script, get_details


def main():

    # Define the crew with agents and tasks in sequential process
    crew = Crew(
        agents=[content_explorer, script_writer],
        tasks=[get_details, create_a_script],
        verbose=True,
        process=Process.sequential,
    )

    crew.kickoff(inputs={"topic": "AI Agents in the year 2025"})


if __name__ == "__main__":
    main()
