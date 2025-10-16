from crewai import Task
from crewai.tasks.task_output import TaskOutput
from tools import search_jobs


def callback_function(output: TaskOutput):
    """Save task output to file"""
    try:
        with open("task_output.txt", "a", encoding="utf-8") as file:
            file.write(f"=== {output.agent} - {output.description} ===\n")
            file.write(f"{output.result}\n\n")
        print(f"✅ Result saved to task_output.txt")
    except Exception as e:
        print(f"❌ Error saving output: {e}")


def create_tasks(agents: dict, resume_content: str = ""):
    """
    Create all tasks for the agents with resume context

    Args:
        agents: Dictionary containing all agents
        resume_content: Parsed resume content for personalized recommendations

    Returns:
        Dictionary containing all tasks
    """

    job_search_task = Task(
        description="""Search for current job openings based on the specified role and location. 
        Use the Job Search tool with the following parameters:
        - Find 5-10 relevant positions
        - Focus on quality over quantity
        - Include detailed job descriptions and requirements
        - Highlight key qualifications and skills needed
        
        Format your search as JSON: {'role': '<role>', 'location': '<location>', 'num_results': <number>}""",
        expected_output="A formatted list of job openings with titles, companies, locations, salaries, descriptions, and URLs",
        agent=agents["job_searcher"],
        tools=[search_jobs],
        callback=callback_function,
    )

    skills_analysis_task = Task(
        description=f"""Analyze the job openings and create a PERSONALIZED skills assessment:
        
        1. Compare the candidate's current skills (from resume) with job requirements
        2. Identify SPECIFIC skill gaps and strengths
        3. Categorize skills as: Already Have, Need to Improve, Need to Learn
        4. Provide targeted recommendations including:
           - Specific courses/certifications for identified gaps
           - How to better highlight existing skills
           - Timeline for skill development based on current level
           - Which skills to prioritize for maximum impact
        5. Create a personalized learning roadmap
        
        {f'Use the candidate resume content for context: {resume_content}' if resume_content else 'No resume provided - provide general recommendations.'}""",
        expected_output="A personalized skills gap analysis with specific recommendations tailored to the candidate's background",
        agent=agents["skills_development"],
        context=[job_search_task],
        callback=callback_function,
    )

    interview_prep_task = Task(
        description=f"""Create a PERSONALIZED interview preparation strategy:
        
        1. Generate role-specific questions tailored to the candidate's background
        2. Create STAR method examples using the candidate's actual experience
        3. Identify potential interview challenges based on resume gaps or career changes
        4. Provide specific talking points to highlight candidate's unique strengths
        5. Address potential concerns employers might have
        6. Create customized salary negotiation strategy based on experience level
        7. Develop elevator pitch based on candidate's background
        
        {f'Base recommendations on candidate resume: {resume_content}' if resume_content else 'Provide general interview preparation advice.'}""",
        expected_output="A personalized interview preparation guide with customized questions, answers, and strategies",
        agent=agents["interview_prep"],
        context=[job_search_task, skills_analysis_task],
        callback=callback_function,
    )

    career_strategy_task = Task(
        description=f"""Develop a PERSONALIZED career strategy plan:
        
        1. Analyze current resume and suggest specific improvements for target roles
        2. Create LinkedIn optimization strategy based on existing profile content
        3. Identify networking opportunities relevant to candidate's industry/background
        4. Suggest specific portfolio projects based on current skills and target roles
        5. Create personal branding strategy that highlights unique value proposition
        6. Develop application strategy tailored to candidate's experience level
        7. Provide specific action items with timeline for career advancement
        
        {f'Base all recommendations on candidate background: {resume_content}' if resume_content else 'Provide general career strategy advice.'}""",
        expected_output="A personalized career strategy plan with specific, actionable recommendations",
        agent=agents["career_advisor"],
        context=[job_search_task, skills_analysis_task],
        callback=callback_function,
    )

    return {
        "job_search": job_search_task,
        "skills_analysis": skills_analysis_task,
        "interview_prep": interview_prep_task,
        "career_strategy": career_strategy_task,
    }
