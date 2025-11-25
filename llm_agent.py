# llm_agent.py
import os
import json
import requests
import subprocess
import sys
import pandas as pd  # <--- ADDED THIS
import numpy as np   # <--- ADDED THIS
from openai import OpenAI
from utils import AIPROXY_TOKEN, OPENAI_API_BASE

client = OpenAI(
    api_key=AIPROXY_TOKEN,
    base_url=OPENAI_API_BASE
)

def execute_python_code(code_str):
    try:
        # We define a specific dictionary of tools available to the code
        # This ensures 'pd' and 'np' are always recognized
        execution_scope = {
            "pd": pd,
            "np": np,
            "requests": requests,
            "json": json,
            "result": None # Initialize result variable
        }
        
        # Execute the code using this scope
        exec(code_str, execution_scope)
        
        return execution_scope.get('result', "No result variable found")
    except Exception as e:
        return f"Execution Error: {str(e)}"

def solve_quiz_task(task_text, current_url):
    
    # Updated prompt to be even more explicit about imports
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
    1. **Relative URLs**: If the submission URL starts with '/', PREPEND the base domain from the CURRENT PAGE URL ({current_url}).
    2. **Imports**: ALWAYS include 'import pandas as pd' and 'import numpy as np' in your python_code, just to be safe.
    3. **CSV Parsing**: Use 'pd.read_csv(..., on_bad_lines="skip")' to avoid tokenizing errors.
    4. **Result**: Store the final answer in a variable named 'result'.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the webpage text:\n{task_text}"}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        llm_output = json.loads(response.choices[0].message.content)
        code = llm_output.get('python_code', '')
        submit_url = llm_output.get('submission_url', '')
        explanation = llm_output.get('explanation', 'No explanation')
        
        # Safety fix for relative URLs
        if submit_url.startswith("/"):
            from urllib.parse import urljoin
            submit_url = urljoin(current_url, submit_url)
        
        print(f"Executing code for: {explanation}")
        answer = execute_python_code(code)
        
        return submit_url, answer
        
    except Exception as e:
        print(f"LLM Parsing Error: {e}")
        return current_url, None