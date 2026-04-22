from crewai import Agent, Task, Crew

analysis_agent = Agent(
    role="Test Analyst",
    goal="Find flaky tests",
    backstory="Expert in testing",
    llm="llama-3.1-8b-instant",
    verbose=True
)

fix_agent = Agent(
    role="Fix Expert",
    goal="Suggest fixes",
    backstory="Debugging expert",
    llm="llama-3.1-8b-instant",
    verbose=True
)

# Tasks
analysis_task = Task(
    description="Analyze flaky test data and identify issues",
    expected_output="List of flaky tests with reasons",
    agent=analysis_agent
)

fix_task = Task(
    description="Suggest solutions to improve test reliability",
    expected_output="Actionable fixes and recommendations",
    agent=fix_agent
)

# Crew
crew = Crew(
    agents=[analysis_agent, fix_agent],
    tasks=[analysis_task, fix_task],
    verbose=True
)

def run_crew():
    return crew.kickoff()

# Run
if __name__ == "__main__":
    result = run_crew()
    print("\nFINAL RESULT:\n")
    print(result)