from vector_db import initialize_vector_db
from playwright.sync_api import sync_playwright
import json
import time
from enum import Enum
from typing import Dict, List

# Initialize vector DB at startup
VECTOR_DB = initialize_vector_db()

class Action(Enum):
    GOTO = "goto"
    CLICK = "click"
    TYPE = "type"
    PRESS_ENTER = "press_enter"
    HOVER = "hover"

def get_llm_plan(user_goal: str) -> Dict:
    """Get action plan from vector database examples"""
    similar_examples = VECTOR_DB.get_similar_examples(user_goal)
    return similar_examples[0]["plan"] if similar_examples else {"steps": []}

def wait_for_angular(page, timeout: int = 30000):
    """Wait for Angular to be stable"""
    try:
        page.wait_for_function("""() => {
            return window.getAllAngularTestabilities?.().findIndex(x=>!x.isStable()) === -1 || 
                   angular?.element(document).injector().get('$http').pendingRequests.length === 0;
        }""", timeout=timeout)
    except:
        page.wait_for_load_state("networkidle")

def find_angular_element(page, description: str):
    """Find elements in Angular apps with multiple strategies"""
    selectors = [
        f"[ng-click*='{description.lower()}']",
        f"[data-ng-click*='{description.lower()}']",
        f"[analytics-id*='{description.lower()}']",
        f"[bb-click*='{description.lower()}']",
        f"text=/^{description}$/i",
        f"text={description}",
        f"[aria-label*='{description}']",
        f"[title*='{description}']",
    ]
    for selector in selectors:
        try:
            return page.wait_for_selector(selector, timeout=2000)
        except:
            continue
    return None

def get_csrf_token(page):
    """Extract CSRF token from Angular app meta tags"""
    return page.evaluate('''() => {
        return document.querySelector('meta[name="csrf-token"]')?.content || 
               document.querySelector('meta[name="_csrf"]')?.content;
    }''')

def perform_click(page, element_description: str) -> bool:
    """Click an element with enhanced error handling"""
    element = find_angular_element(page, element_description)
    if not element:
        print(f"Element not found: {element_description}")
        return False

    try:
        # Update CSRF token before each action
        csrf_token = get_csrf_token(page)
        if csrf_token:
            page.set_extra_http_headers({"X-CSRF-Token": csrf_token})

        element.scroll_into_view_if_needed()
        current_url = page.url

        # Prevent new tabs/windows
        page.evaluate("""() => {
            window.open = function(url) { window.location.href = url; return null; };
            document.querySelectorAll('a').forEach(a => a.target = '_self');
        }""")

        try:
            with page.expect_navigation(timeout=10000, wait_until="networkidle"):
                element.click()
        except:
            element.click(force=True)

        if page.url != current_url:
            wait_for_angular(page)

        return True
    except Exception as e:
        print(f"Click failed: {str(e)}")
        return False

def interactive_angular_navigator():
    with sync_playwright() as p:
        # Launch with realistic browser context
        browser = p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ])
        context = browser.new_context()

        # Add authentication cookies if needed
        context.add_cookies([{
            "name": "SESSION_ID",
            "value": "your_session_token",
            "domain": "yourdomain.com",
            "path": "/"
        }])

        page = context.new_page()
        page.set_default_timeout(15000)

        # Enable network debugging
        def log_request(request):
            print(f"> {request.method} {request.url}")
        def log_response(response):
            if response.status >= 400:
                print(f"< {response.status} {response.url}")
                try:
                    print(f"   Response: {response.text()[:200]}...")
                except:
                    pass
        page.on("request", log_request)
        page.on("response", log_response)

        # Tab management
        def handle_new_tab(new_tab):
            nonlocal page
            if new_tab != page:
                print("⚠️ Tab switch detected")
                if not page.is_closed():
                    page.close()
                page = new_tab
                page.set_default_timeout(15000)
        context.on("page", handle_new_tab)

        print("Connected. Type your goal or 'quit'.")
        while True:
            try:
                user_prompt = input("\nEnter command: ").strip()
                if user_prompt.lower() == "quit":
                    break

                plan = get_llm_plan(user_prompt)
                print(f"\nPlan: {json.dumps(plan, indent=2)}")

                for step in plan.get("steps", []):
                    action = step.get("action")
                    if action == "goto":
                        url = step.get("url")
                        if url and url != page.url:
                            try:
                                response = page.goto(url, wait_until="networkidle")
                                if response.status == 403:
                                    print(f"Access denied to {url}")
                                    break
                                wait_for_angular(page)
                            except Exception as e:
                                print(f"Navigation failed: {str(e)}")
                                break
                    elif action == "click":
                        if not perform_click(page, step["element_description"]):
                            break
                    elif action == "type":
                        element = find_angular_element(page, step["element_description"])
                        if element:
                            element.fill(step.get("text", ""))
                        else:
                            print(f"Element not found for typing: {step['element_description']}")
                            break
                    elif action == "press_enter":
                        page.keyboard.press("Enter")
                        wait_for_angular(page)
            except Exception as e:
                print(f"Error: {str(e)}")
            finally:
                while len(context.pages) > 1:
                    context.pages[-1].close()

if __name__ == "__main__":
    interactive_angular_navigator()