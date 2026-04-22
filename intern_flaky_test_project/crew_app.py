import os
from langchain_groq import ChatGroq
from crewai import Agent, Task, Crew

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant"
)

analysis_agent = Agent(
    role="Test Analyst",
    goal="Find flaky tests",
    backstory="Expert in testing",
    llm=llm,
    verbose=True
)

fix_agent = Agent(
    role="Fix Expert",
    goal="Suggest fixes",
    backstory="Debugging expert",
    llm=llm,
    verbose=True
)

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

crew = Crew(
    agents=[analysis_agent, fix_agent],
    tasks=[analysis_task, fix_task],
    verbose=True
)

def run_crew():
    return crew.kickoff()

if __name__ == "__main__":
    result = run_crew()
    print("\nFINAL RESULT:\n")
    print(result)