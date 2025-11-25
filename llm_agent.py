# llm_agent.py
import os
import json
import requests
import subprocess
import sys
from openai import OpenAI
from utils import AIPROXY_TOKEN, OPENAI_API_BASE

# Initialize Client
client = OpenAI(
    api_key=AIPROXY_TOKEN,
    base_url=OPENAI_API_BASE
)

def execute_python_code(code_str):
    """
    Executes the generated Python code and returns the output (stdout).
    """
    try:
        # We wrap the code to capture the result
        # This is a simplified execution environment
        local_scope = {}
        exec(code_str, globals(), local_scope)
        return local_scope.get('result', "No result variable found")
    except Exception as e:
        return f"Execution Error: {str(e)}"

def solve_quiz_task(task_text):
    """
    1. Asks LLM to parse the task.
    2. Asks LLM to write code to solve the data problem.
    3. Executes code.
    4. Returns the JSON answer.
    """
    
    # Step 1: Parse the intent and get the submission URL and Logic
    system_prompt = """
    You are an intelligent agent. You have been given a raw text dump of a webpage.
    The page contains:
    1. A data analysis question (e.g., "Download X, sum column Y").
    2. A JSON structure for submission (including a submission URL).
    
    Your goal:
    Extract the submission URL and write Python code to solve the question.
    
    Output strictly valid JSON format:
    {
        "submission_url": "url_found_in_text",
        "python_code": "code_to_solve_problem",
        "explanation": "brief explanation"
    }
    
    For the "python_code":
    - It must use 'requests', 'pandas', 'BeautifulSoup' etc.
    - It must PRINT or store the final answer in a variable named 'result'.
    - If a file needs downloading, download it using python requests.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Use a cost-effective but smart model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the webpage text:\n{task_text}"}
        ],
        response_format={"type": "json_object"}
    )
    
    llm_output = json.loads(response.choices[0].message.content)
    
    code = llm_output['python_code']
    submit_url = llm_output['submission_url']
    
    print(f"Executing code for: {llm_output['explanation']}")
    
    # Execute the code to get the answer
    answer = execute_python_code(code)
    
    return submit_url, answer