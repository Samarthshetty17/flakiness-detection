from groq import Groq
import os
import pandas as pd

df = pd.read_csv("testneo_test_executions.csv")
data_sample = df.head(20).to_string()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
prompt = f"""
Analyze the test execution data and:
1. Detect flaky tests
2. Rank them by severity
3. Identify patterns across environments and browsers
4. Suggest fixes and best practices
5. Highlight critical issues
Data:
{"Highlight top 3 flaky tests and risky environments"}
"""
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": prompt}
    ]
)
print(response.choices[0].message.content)