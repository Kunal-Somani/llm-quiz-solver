# llm_agent.py
import os
import json
import requests
import subprocess
import sys
from openai import OpenAI
from utils import AIPROXY_TOKEN, OPENAI_API_BASE

client = OpenAI(
    api_key=AIPROXY_TOKEN,
    base_url=OPENAI_API_BASE
)

def execute_python_code(code_str):
    try:
        local_scope = {}
        exec(code_str, globals(), local_scope)
        return local_scope.get('result', "No result variable found")
    except Exception as e:
        return f"Execution Error: {str(e)}"

def solve_quiz_task(task_text, current_url):
    """
    Now accepts 'current_url' to help resolve relative links.
    """
    
    # Improved System Prompt with URL handling instructions
    system_prompt = f"""
    You are an intelligent agent. You have been given a raw text dump of a webpage.
    The page contains:
    1. A data analysis question.
    2. A JSON structure for submission.
    
    The CURRENT PAGE URL is: {current_url}
    
    Your goal:
    Extract the submission URL and write Python code to solve the question.
    
    Output strictly valid JSON format:
    {{
        "submission_url": "extracted_url",
        "python_code": "code_to_solve_problem",
        "explanation": "brief explanation"
    }}
    
    CRITICAL RULES:
    1. **Relative URLs**: If the submission URL or a data file URL starts with '/', you MUST prepend the base domain from the CURRENT PAGE URL provided above.
       - Example: if current_url is "https://site.com/page" and found url is "/submit", make it "https://site.com/submit".
    2. **Python Code**: 
       - Must use 'requests', 'pandas', etc.
       - Store the final answer in a variable named 'result'.
       - When reading CSVs, use 'pd.read_csv(file, on_bad_lines="skip")' to avoid tokenizing errors.
       - Handle errors gracefully.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the webpage text:\n{task_text}"}
        ],
        response_format={"type": "json_object"}
    )
    
    llm_output = json.loads(response.choices[0].message.content)
    
    code = llm_output['python_code']
    submit_url = llm_output['submission_url']
    
    # DOUBLE SAFETY: If the LLM still returns a relative URL for submission, fix it here manually
    if submit_url.startswith("/"):
        from urllib.parse import urljoin
        submit_url = urljoin(current_url, submit_url)
    
    print(f"Executing code for: {llm_output['explanation']}")
    
    answer = execute_python_code(code)
    
    return submit_url, answer