import os

from agents import issue_investigator, log_analyzer, solution_specialist
from crewai import Task

# Create output directory for task results
os.makedirs("task_outputs", exist_ok=True)

# Task 1: Analyze log file to identify issues
analyze_logs_task = Task(
    description="""Analyze the log file at {log_file_path} to identify and extract specific issues.
    
    Your analysis should:
    1. Read through the entire log file carefully
    2. Identify all ERROR, CRITICAL, and WARNING messages
    3. Extract the main issue or failure pattern
    4. Determine the timeline of events leading to the failure
    5. Identify the root cause from the log entries
    
    Focus on finding the primary issue that needs to be resolved.""",
    expected_output="""A detailed analysis report containing:
    - Primary issue description (clear and concise)
    - Key error messages and codes
    - Timeline of failure events
    - Root cause analysis based on log evidence
    - Relevant technical context and affected components""",
    agent=log_analyzer,
    output_file="src/intermediate/devops/task_outputs/log_analysis.md",
)

# Task 2: Investigate the identified issue online
investigate_issue_task = Task(
    description="""Based on the log analysis findings, investigate the identified issue online.
    
    Your investigation should:
    1. Search for similar errors and issues in documentation and forums
    2. Find official documentation related to the error
    3. Look for community solutions and best practices
    4. Identify common causes and scenarios for this type of issue
    5. Gather information about proven fixes and workarounds
    
    Focus on finding reliable, well-documented solutions.""",
    expected_output="""A comprehensive investigation report including:
    - Similar issues found online with references
    - Official documentation links and explanations
    - Common causes ranked by likelihood
    - Community-verified solutions and workarounds
    - Best practices to prevent similar issues""",
    agent=issue_investigator,
    context=[analyze_logs_task],
    output_file="src/intermediate/devops/task_outputs/investigation_report.md",
)

# Task 3: Provide actionable solution
provide_solution_task = Task(
    description="""Based on the log analysis and investigation findings, provide a complete solution.
    
    Your solution should:
    1. Create a step-by-step remediation plan
    2. Include specific commands and configurations
    3. Provide verification steps to confirm the fix
    4. Suggest monitoring and prevention measures
    5. Include rollback procedures if needed
    
    Ensure all solutions are practical and well-tested.""",
    expected_output="""A detailed remediation plan with:
    - Primary solution with step-by-step commands
    - Configuration changes required (if any)
    - Verification and testing procedures
    - Alternative solutions (if applicable)
    - Prevention strategies and monitoring recommendations
    - Rollback plan in case of issues
    - Links to official documentation and references""",
    agent=solution_specialist,
    context=[analyze_logs_task, investigate_issue_task],
    output_file="src/intermediate/devops/task_outputs/solution_plan.md",
)
