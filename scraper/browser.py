from playwright.sync_api import sync_playwright

def fetch_dynamic_html(url: str, timeout_ms: int = 15000) -> str:
    """
    Launches a headless browser instance using Playwright to execute JavaScript
    and return the fully rendered DOM content of the target URL.
    """
    with sync_playwright() as p:
        # Launch browser in headless mode for server-side execution
        browser = p.chromium.launch(headless=True)
        
        # Configure a secure, clean browser context
        context = browser.new_context(
            user_agent="SecureScraper/1.0 (Dynamic Browser Portfolio Engine)"
        )
        
        page = context.new_page()
        
        try:
            # Navigate to the target page and wait until background network traffic settles
            page.goto(url, timeout=timeout_ms, wait_until="networkidle")
            html_content = page.content()
            return html_content
        except Exception as e:
            print(f"[!] Playwright browser execution failed for {url}: {str(e)}")
            return ""
        finally:
            # Ensure resources are closed cleanly to avoid memory leaks
            context.close()
            browser.close()