# browser_task.py
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def get_task_from_url(url: str):
    """
    Visits the URL, renders JS, and extracts the Question and Submission URL.
    """
    async with async_playwright() as p:
        # Launch the browser in headless mode (no visible UI)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Visit the page with a 60-second timeout
            await page.goto(url, timeout=60000)
            
            # Wait for the page to settle (networkidle ensures most JS has finished)
            await page.wait_for_load_state('networkidle')
            
            # Get the full HTML content after JS execution
            content = await page.content()
            
            # Use BeautifulSoup to strip HTML tags and get clean text
            soup = BeautifulSoup(content, 'html.parser')
            page_text = soup.get_text(separator="\n", strip=True)
            
            await browser.close()
            return page_text
            
        except Exception as e:
            await browser.close()
            # Return the error as text so the LLM knows something went wrong
            return f"Error fetching page: {str(e)}"