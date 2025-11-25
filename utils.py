# utils.py
import os
from dotenv import load_dotenv

load_dotenv() # Loads the .env file

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN") # Securely loads key
OPENAI_API_BASE = "https://aipipe.org/openrouter/v1"

MY_EMAIL = "23f2001869@ds.study.iitm.ac.in"
MY_SECRET = "Kunal_Somani_1905"