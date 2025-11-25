import requests

# 1. Your RENDER URL (The one you just gave me)
API_URL = "https://llm-solver-app.onrender.com/run"

# 2. The payload (Must match your utils.py details)
payload = {
    "email": "23f2001869@ds.study.iitm.ac.in",
    "secret": "Kunal_Somani_1905",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
}

print(f"Sending request to {API_URL}...")

try:
    # 3. Send the POST request
    response = requests.post(API_URL, json=payload, timeout=10)
    
    # 4. Print the result
    print(f"Status Code: {response.status_code}")
    print("Response Body:", response.json())
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Your API accepted the task.")
        print("Now check your Render Logs to see if it solves the quiz.")
    else:
        print("\n❌ FAILED. Check credentials or server logs.")

except Exception as e:
    print(f"Error: {e}")