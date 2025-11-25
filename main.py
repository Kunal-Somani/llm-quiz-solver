# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from browser_task import get_task_from_url
from llm_agent import solve_quiz_task
from utils import MY_EMAIL, MY_SECRET
import requests

app = FastAPI()

class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str

async def process_quiz_flow(start_url: str):
    """
    Recursive function to handle the quiz loop.
    """
    current_url = start_url
    
    # Loop to handle multi-step quizzes
    # We limit to 5 iterations to prevent infinite loops
    for _ in range(5):
        print(f"Processing: {current_url}")
        
        # 1. Get Page Content (Headless)
        task_text = await get_task_from_url(current_url)
        
        # 2. Solve Task (LLM + Code Exec)
        submit_url, answer = solve_quiz_task(task_text)
        
        # 3. Construct Payload
        payload = {
            "email": MY_EMAIL,
            "secret": MY_SECRET,
            "url": current_url,
            "answer": answer
        }
        
        # 4. Submit Answer
        print(f"Submitting to {submit_url} with answer: {answer}")
        try:
            response = requests.post(submit_url, json=payload, timeout=10)
            res_json = response.json()
            print(f"Result: {res_json}")
            
            if res_json.get("correct", False):
                # If correct, check if there is a NEXT url
                next_url = res_json.get("url")
                if next_url:
                    current_url = next_url # Continue loop
                else:
                    print("Quiz Completed!")
                    break
            else:
                print("Wrong answer. Stopping or Retrying logic needed.")
                break
                
        except Exception as e:
            print(f"Submission failed: {e}")
            break

@app.post("/run")
async def run_quiz(request: QuizRequest, background_tasks: BackgroundTasks):
    # 1. Validate Secret
    if request.secret != MY_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Secret")
    
    # 2. Start the worker in the background (to return 200 OK immediately)
    background_tasks.add_task(process_quiz_flow, request.url)
    
    return {"message": "Quiz processing started", "status": "success"}

@app.get("/")
def home():
    return {"status": "Online", "details": "LLM Quiz Solver"}