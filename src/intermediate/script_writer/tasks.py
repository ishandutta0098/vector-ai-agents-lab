from agents import content_explorer, script_writer
from crewai import Task

# Task to gather Latest information
get_details = Task(
    description="Get latest, trending, interesting information and news about {topic}",
    expected_output="Latest news, interesting information and trivia about {topic}",
    agent=content_explorer,
)

## Task to create script.
create_a_script = Task(
    description="Considering the given details in time order make an interesting conversation",
    expected_output="A humorous conversation connecting key details",
    agent=script_writer,
    context=[get_details],
    output_file="src/intermediate/script_writer/task_outputs/script.txt",
)
