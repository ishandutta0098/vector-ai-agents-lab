import os

from agents import issue_investigator, log_analyzer, solution_specialist
from crewai import Crew, Process
from tasks import analyze_logs_task, investigate_issue_task, provide_solution_task

os.environ["CREWAI_STORAGE_DIR"] = "src/intermediate/devops/crewai_memory"

# Enhanced DevOps crew with advanced configuration
devops_crew = Crew(
    agents=[log_analyzer, issue_investigator, solution_specialist],
    tasks=[analyze_logs_task, investigate_issue_task, provide_solution_task],
    verbose=True,
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=30,
)

if __name__ == "__main__":
    print("🚀 Starting Enhanced DevOps Issue Analysis...")

    # Scenario 1: Analyze Kubernetes deployment error
    print("\n📋 Scenario 1: Kubernetes Deployment Analysis")
    result = devops_crew.kickoff(
        inputs={
            "log_file_path": "src/intermediate/devops/logs/kubernetes_deployment_error.txt"
        }
    )

    # Scenario 2: Analyze database connection error
    print("\n📋 Scenario 2: Database Connection Analysis")
    result = devops_crew.kickoff(inputs={"log_file_path": "src/intermediate/devops/logs/database_connection_error.txt"})

    print("\n🎉 DevOps analysis completed!")
