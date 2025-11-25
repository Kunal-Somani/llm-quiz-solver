# 1. Use the official Playwright image (contains Python + Browsers)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the dependency file first (for caching)
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# 6. Expose the port (Render uses standard port 10000 usually, or 8000)
EXPOSE 8000

# 7. Command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]