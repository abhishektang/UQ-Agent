from playwright.sync_api import sync_playwright
import re
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import time
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


from vector_db import initialize_vector_db

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
class Action(Enum):
    CLICK = "click"
    HOVER = "hover"
    FILL = "fill"
    TYPE = "type"
    GOTO = "goto"
    PRESS_ENTER = "press_enter"
    SELECT = "select"
    WAIT = "wait"


ELEMENT_CACHE = {}
CURRENT_PAGE = None
LAST_ACTION_TIME = 0
DEBUG = True

VECTOR_DB = initialize_vector_db()


def debug_print(message: str):
    if DEBUG:
        print(f"[DEBUG] {message}")


def get_navigation_plan(user_prompt: str) -> Dict:
    """
    Get navigation plan for a user's prompt by querying similar examples from vector database.
    """
    try:
        similar_examples = VECTOR_DB.get_similar_examples(user_prompt)
        if similar_examples:
            debug_print(f"Found matching plan: {similar_examples[0]['plan']}")
            return similar_examples[0]["plan"]
    except Exception as e:
        debug_print(f"Error getting navigation plan: {e}")

    return {"steps": []}


def execute_plan(current_page, plan: Dict) -> bool:
    """
    Execute a navigation plan step by step with balanced waiting between actions.
    """
    if not plan or not plan.get("steps"):
        print("No valid plan found")
        return False

    for step in plan["steps"]:
        action = step.get("action")
        if not action:
            continue

        try:
            # Wait for DOM stability before each action
            wait_for_dom_stability(current_page)

            if action == Action.GOTO.value:
                url = step.get("url")
                if url and url != current_page.url:
                    print(f"Navigating to: {url}")
                    current_page.goto(url, wait_until="networkidle", timeout=30000)
                    wait_for_angular(current_page)
                    time.sleep(1)  # Conservative wait after navigation

            elif action == Action.CLICK.value:
                element_desc = step.get("element_description")
                print(f"Clicking: {element_desc}")
                if not perform_action_on_element(current_page, Action.CLICK, element_desc):
                    print(f"Failed to click: {element_desc}")
                    return False
                # Wait for potential page changes after click
                wait_for_dom_stability(current_page, extra_wait=1)

            elif action == Action.TYPE.value:
                element_desc = step.get("element_description")
                text = step.get("text", "")
                print(f"Typing in {element_desc}: {text}")
                if not perform_action_on_element(current_page, Action.TYPE, element_desc, text):
                    print(f"Failed to type in: {element_desc}")
                    return False
                time.sleep(0.5)  # Wait after typing

            elif action == Action.FILL.value:
                element_desc = step.get("element_description")
                text = step.get("text", "")
                print(f"Filling {element_desc}: {text}")
                if not perform_action_on_element(current_page, Action.FILL, element_desc, text):
                    print(f"Failed to fill: {element_desc}")
                    return False
                time.sleep(0.5)  # Wait after filling

            elif action == Action.PRESS_ENTER.value:
                print("Pressing Enter")
                current_page.keyboard.press("Enter")
                # Wait for navigation after Enter
                wait_for_dom_stability(current_page, extra_wait=1.5)

            elif action == Action.HOVER.value:
                element_desc = step.get("element_description")
                print(f"Hovering over: {element_desc}")
                if not perform_action_on_element(current_page, Action.HOVER, element_desc):
                    print(f"Failed to hover: {element_desc}")
                    return False
                time.sleep(0.5)  # Wait for hover effects

            elif action == Action.SELECT.value:
                element_desc = step.get("element_description")
                option = step.get("option", "")
                print(f"Selecting {option} in {element_desc}")
                if not perform_action_on_element(current_page, Action.SELECT, element_desc, option):
                    print(f"Failed to select: {element_desc}")
                    return False
                wait_for_dom_stability(current_page)

            elif action == Action.WAIT.value:
                wait_time = step.get("time", 1)
                print(f"Waiting for {wait_time} seconds")
                time.sleep(wait_time)

        except Exception as e:
            print(f"Error executing step {step}: {str(e)}")
            return False

    return True


def is_angular_page(page) -> bool:
    """Check if the current page is an Angular application"""
    try:
        return page.evaluate("""() => {
            return !!window.angular || !!document.querySelector('[ng-app], [data-ng-app]');
        }""")
    except:
        return False


def wait_for_dom_stability(page, timeout: int = 5000, extra_wait: float = 0):
    """
    Wait for DOM to stabilize with appropriate waits for different page types.
    """
    try:
        if page.is_closed():
            return False

        # Basic load state check
        page.wait_for_load_state("domcontentloaded", timeout=2000)

        # Get initial DOM metrics
        initial_metrics = page.evaluate("""() => {
            return {
                childElementCount: document.body.childElementCount,
                scrollHeight: document.body.scrollHeight,
                domLength: document.documentElement.outerHTML.length
            };
        }""")

        # Wait until DOM metrics stabilize
        def check_dom_stable():
            current_metrics = page.evaluate("""() => {
                return {
                    childElementCount: document.body.childElementCount,
                    scrollHeight: document.body.scrollHeight,
                    domLength: document.documentElement.outerHTML.length
                };
            }""")
            return (current_metrics['childElementCount'] == initial_metrics['childElementCount'] and
                    abs(current_metrics['scrollHeight'] - initial_metrics['scrollHeight']) < 5 and
                    abs(current_metrics['domLength'] - initial_metrics['domLength']) < 100)

        # Wait for DOM to stabilize or timeout
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            if check_dom_stable():
                break
            time.sleep(0.2)

        # Additional wait if requested
        if extra_wait > 0:
            time.sleep(extra_wait)

        # Check for Angular if detected
        if is_angular_page(page):
            wait_for_angular(page, timeout=3000)

    except Exception as e:
        debug_print(f"DOM stability check warning: {e}")
        time.sleep(1)  # Fallback wait


def wait_for_angular(page, timeout: int = 3000):
    """Optimized Angular waiting that checks first if Angular is present"""
    if not is_angular_page(page):
        return

    try:
        # First wait for network idle
        page.wait_for_load_state("networkidle", timeout=timeout / 2)

        # Then wait for Angular stability with timeout
        page.wait_for_function("""() => {
            try {
                if (window.getAllAngularTestabilities) {
                    return window.getAllAngularTestabilities().findIndex(x=>!x.isStable()) === -1;
                }
                if (window.angular) {
                    return angular.element(document).injector().get('$http').pendingRequests.length === 0;
                }
                return true;
            } catch(e) {
                return true;
            }
        }""", timeout=timeout / 2)
    except Exception as e:
        debug_print(f"Angular wait warning: {e}")
        try:
            page.wait_for_load_state("domcontentloaded", timeout=2000)
        except:
            pass


def find_text_area_element(page, description: str) -> Optional[Any]:
    """Improved text area finder with better element selection"""
    common_editors = [
        'div[role="textbox"]',
        'div[contenteditable="true"]',
        '.ql-editor',
        '.tox-edit-area',
        '.cke_contents',
        '.ProseMirror',
        '.public-DraftEditor-content',
        '.w-md-editor-content',
        'textarea.large-textarea',
        'textarea[aria-label="Post content"]'
    ]

    for selector in common_editors:
        try:
            elements = page.query_selector_all(selector)
            for element in elements:
                try:
                    box = element.bounding_box()
                    if box and box['width'] > 100 and box['height'] > 50:  # Reduced minimum size
                        # Check if element is actually visible
                        if element.is_visible():
                            return element
                except:
                    continue
        except:
            continue

    try:
        elements = page.query_selector_all('textarea, div[contenteditable="true"]')
        largest_area = None
        max_size = 0

        for element in elements:
            try:
                if not element.is_visible():
                    continue

                box = element.bounding_box()
                if box:
                    size = box['width'] * box['height']
                    if size > max_size:
                        max_size = size
                        largest_area = element
            except:
                continue

        return largest_area
    except:
        return None


def perform_action_on_element(page, action: Action, element_description: str, value: str = None) -> bool:
    global LAST_ACTION_TIME

    try:
        current_url = page.url
    except:
        print("Page is no longer available")
        return False

    # Wait for DOM to be ready before proceeding
    try:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_load_state("networkidle", timeout=15000)
    except:
        print("Warning: Page took too long to load, proceeding anyway")

    # Rest of the function remains the same...
    cached_selector, _ = get_cached_element(current_url, element_description)
    if cached_selector:
        try:
            element = page.query_selector(cached_selector)
            if element:
                return _execute_action(page, action, element, element_description, value)
        except Exception as e:
            print(f"Cache action failed: {e}")

    # Special handling for text areas
    if action in (Action.FILL, Action.TYPE) and any(word in element_description.lower()
                                                    for word in
                                                    ['post', 'content', 'reply', 'comment', 'text', 'message']):
        element = find_text_area_element(page, element_description)
        if element:
            try:
                return _execute_action(page, action, element, element_description, value)
            except Exception as e:
                debug_print(f"Action failed on text area: {e}")

    # Try fuzzy matching
    element = find_element_by_text(page, element_description)
    if element:
        try:
            return _execute_action(page, action, element, element_description, value)
        except Exception as e:
            debug_print(f"Action failed on found element: {e}")

    print(f"Could not find element matching: {element_description}")
    return False


def find_course_element_by_description(page, description: str) -> Optional[Any]:
    """Find course element based on description text"""
    # Extract potential course code from description
    course_code_match = re.search(r'(\[?[A-Za-z]{2,}\s?\d{3,}[A-Za-z]?\]?)', description.upper())
    if not course_code_match:
        return None

    course_code = course_code_match.group(1).replace('[', '').replace(']', '').replace(' ', '')
    return find_course_element(page, course_code)


def get_cached_element(url: str, element_description: str) -> Optional[Tuple[str, Dict]]:
    cache_key = get_cache_key(url, element_description)
    cached = ELEMENT_CACHE.get(cache_key)
    if cached and time.time() - cached['timestamp'] < 3600:  # Cache valid for 1 hour
        return cached['selector'], cached['element_info']
    return None, None


def _execute_action(page, action: Action, element, element_description: str, value: str = None) -> bool:
    global CURRENT_PAGE, LAST_ACTION_TIME

    try:
        current_url = page.url
    except:
        print("Page is no longer available")
        return False

    try:
        # Additional wait before performing the action
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        element.wait_for_element_state("stable", timeout=10000)

        tag = element.evaluate("el => el.tagName.toLowerCase()")
        text = element.inner_text().strip()
        if not text and tag in ('input', 'textarea', 'div'):
            text = element.get_attribute('placeholder') or ""
            label = element.evaluate('''el => {
                const id = el.id;
                if (id) {
                    const label = document.querySelector(`label[for="${id}"]`);
                    return label ? label.textContent.trim() : '';
                }
                return '';
            }''')
            if label:
                text = f"{text} {label}".strip()
        selector = f"{tag}:has-text('{text}')" if text else f"{tag}"

        ensure_element_visible(page, element)

        if action == Action.CLICK:
            try:
                element.click(timeout=10000)
            except:
                # Try multiple click strategies
                try:
                    element.dispatch_event('click')
                except:
                    page.evaluate('(element) => element.click()', element)

            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "text_match", "text": text, "tag": tag}
            )
            LAST_ACTION_TIME = time.time()
            return True

        elif action == Action.HOVER:
            element.hover(timeout=10000)
            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "text_match", "text": text, "tag": tag}
            )
            LAST_ACTION_TIME = time.time()
            return True

        elif action == Action.FILL and value:
            element.fill(value)
            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "input_field", "text": text, "tag": tag}
            )
            LAST_ACTION_TIME = time.time()
            return True

        elif action == Action.TYPE and value:
            element.click()
            page.keyboard.type(value, delay=100)  # Slower typing for reliability
            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "text_area", "text": text, "tag": tag}
            )
            LAST_ACTION_TIME = time.time()
            return True

        elif action == Action.SELECT and value:
            element.select_option(value)
            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "select", "text": text, "tag": tag}
            )
            LAST_ACTION_TIME = time.time()
            return True

    except Exception as e:
        print(f"Error executing action {action} on element: {e}")
        return False

    return False


def cache_element_selector(url: str, element_description: str, selector: str, element_info: Dict):
    cache_key = get_cache_key(url, element_description)
    ELEMENT_CACHE[cache_key] = {
        'selector': selector,
        'element_info': element_info,
        'timestamp': time.time()
    }


def get_cache_key(url: str, element_description: str) -> str:
    return f"{url}|||{element_description.lower().strip()}"


def ensure_element_visible(page, element):
    """More robust element visibility ensuring"""
    try:
        # First try standard scroll
        element.scroll_into_view_if_needed()

        # Then wait for visibility
        element.wait_for_element_state("visible", timeout=10000)

        # Additional checks for Angular apps
        page.wait_for_function('''(element) => {
            const style = window.getComputedStyle(element);
            return style.visibility !== 'hidden' && 
                   style.display !== 'none' &&
                   element.offsetWidth > 0 && 
                   element.offsetHeight > 0;
        }''', arg=element, timeout=5000)

        # Small delay for stability
        page.wait_for_timeout(300)
    except Exception as e:
        debug_print(f"Warning: Could not ensure element visibility - {e}")


def find_course_element(page, course_code: str) -> Optional[Any]:
    """Improved course element finder with multiple strategies"""
    if not course_code:
        return None

    # Clean the course code (remove brackets and spaces)
    clean_code = course_code.replace('[', '').replace(']', '').replace(' ', '').upper()
    if len(clean_code) < 5:  # Minimum reasonable course code length
        return None

    # Try different strategies to find the course element
    selectors = [
        f'[title*="{clean_code}"]',  # Match title attribute
        f'[aria-label*="{clean_code}"]',  # Match aria-label
        f'[data-course-id*="{clean_code}"]',  # Match data attributes
        f'[id*="{clean_code.lower()}"]',  # Match ID
        f'[class*="course-{clean_code.lower()}"]',  # Match class
        f'[href*="{clean_code.lower()}"]',  # Match href
        f'text=/.*{clean_code}.*/i',  # Text contains course code
        f'text=/.*{clean_code[:4]}.*{clean_code[4:]}.*/i'  # Text with possible space
    ]

    for selector in selectors:
        try:
            element = page.query_selector(selector)
            if element and element.is_visible():
                return element
        except:
            continue

    # Fallback: Find by text in course cards or lists
    try:
        course_containers = page.query_selector_all(
            '.course-card, [class*="course-node"], .course-item, .course-list-item')
        for container in course_containers:
            if not container.is_visible():
                continue

            text = container.inner_text().upper().replace(' ', '')
            if clean_code in text:
                return container

            # Check child elements
            children = container.query_selector_all('*')
            for child in children:
                try:
                    child_text = child.inner_text().upper().replace(' ', '')
                    if clean_code in child_text:
                        return child
                except:
                    continue
    except:
        pass

    return None


def find_element_by_text(page, text: str, threshold: int = 70) -> Optional[Any]:
    """Improved fuzzy text matching with better element selection"""
    # First try exact matches
    try:
        exact_elements = page.query_selector_all(f'text=/{re.escape(text)}/i')
        for element in exact_elements:
            if element.is_visible():
                return element
    except:
        pass

    # Then try partial matches
    try:
        partial_elements = page.query_selector_all(
            'a, button, [role=button], [role=link], input, textarea, [role=textbox], [contenteditable=true]'
        )
    except:
        return None

    best_match = None
    highest_score = 0

    for element in partial_elements:
        try:
            if not element.is_visible():
                continue

            element_text = element.inner_text().strip()
            if not element_text:
                # Handle input elements with labels
                if element.evaluate('el => el.tagName.toLowerCase()') in ('input', 'textarea', 'select'):
                    label_text = element.evaluate('''el => {
                        const id = el.id;
                        if (id) {
                            const label = document.querySelector(`label[for="${id}"]`);
                            return label ? label.textContent.trim() : '';
                        }
                        return '';
                    }''')
                    placeholder = element.get_attribute('placeholder') or ""
                    nearby_text = element.evaluate('''el => {
                        const container = el.closest('div, li, section, article');
                        return container ? container.textContent.trim() : '';
                    }''')
                    combined_text = f"{label_text} {placeholder} {nearby_text}".strip()
                    if combined_text:
                        element_text = combined_text

            if not element_text:
                continue

            # Calculate multiple similarity scores
            ratio_score = fuzz.ratio(element_text.lower(), text.lower())
            partial_score = fuzz.partial_ratio(element_text.lower(), text.lower())
            token_score = fuzz.token_sort_ratio(element_text.lower(), text.lower())

            # Use the highest score
            current_score = max(ratio_score, partial_score, token_score)

            if current_score > highest_score and current_score >= threshold:
                highest_score = current_score
                best_match = element
        except:
            continue

    return best_match if highest_score >= threshold else None


def get_active_page(context):
    """Improved active page detection that ensures we're working with the correct tab"""
    global CURRENT_PAGE, LAST_ACTION_TIME

    # If we recently performed an action, check for new tabs first
    if time.time() - LAST_ACTION_TIME < 3:
        for page in reversed(context.pages):
            if not page.is_closed() and page != CURRENT_PAGE:
                try:
                    # Verify the page is actually different
                    if page.url != (CURRENT_PAGE.url if CURRENT_PAGE else None):
                        CURRENT_PAGE = page
                        print(f"Switched to new tab: {CURRENT_PAGE.url}")
                        # Wait briefly for the new page to settle
                        wait_for_dom_stability(CURRENT_PAGE)
                        return CURRENT_PAGE
                except:
                    continue

    # Return current page if it's still valid
    if CURRENT_PAGE and not CURRENT_PAGE.is_closed():
        return CURRENT_PAGE

    # Otherwise return the last non-closed page
    for page in reversed(context.pages):
        if not page.is_closed():
            CURRENT_PAGE = page
            # Wait briefly for the page to settle
            wait_for_dom_stability(CURRENT_PAGE)
            return CURRENT_PAGE

    return None


def interactive_angular_navigator(prompt):
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            global CURRENT_PAGE, LAST_ACTION_TIME

            # Initialize with first page or new page
            CURRENT_PAGE = context.pages[0] if context.pages else context.new_page()
            LAST_ACTION_TIME = time.time()

            def handle_new_page(new_page):
                global CURRENT_PAGE, LAST_ACTION_TIME
                print(f"\nNew tab opened: {new_page.url}")
                CURRENT_PAGE = new_page
                LAST_ACTION_TIME = time.time()
                print(f"Now controlling tab: {CURRENT_PAGE.url}")

                # Wait for the new page to be ready
                try:
                    wait_for_dom_stability(new_page)
                except Exception as e:
                    debug_print(f"New tab load warning: {e}")

            context.on("page", handle_new_page)

            print("Connected to browser. New tabs will immediately switch control.")
            print("Enter your goal and the system will find and execute a matching plan.")

            while True:
                try:
                    user_prompt = prompt.strip()
                    if user_prompt.lower() in ('quit', 'exit'):
                        break
                    if not user_prompt:
                        continue

                    # Get the current active page (ensures we're working with the right tab)
                    current_page = get_active_page(context)
                    if not current_page or current_page.is_closed():
                        if context.pages:
                            CURRENT_PAGE = context.pages[-1]
                            current_page = CURRENT_PAGE
                            print(f"Recovered control of tab: {current_page.url}")
                            wait_for_dom_stability(current_page)
                        else:
                            print("No pages available, exiting...")
                            break

                    print(f"\nCurrent active tab: {current_page.url}")

                    # Get the plan from vector DB
                    plan = get_navigation_plan(user_prompt)
                    print(f"\nExecuting plan:\n{json.dumps(plan, indent=2)}")

                    # Execute the plan
                    success = execute_plan(current_page, plan)

                    if success:
                        print("Plan executed successfully!")
                    else:
                        print("Plan execution failed.")

                except Exception as e:
                    print(f"Error processing command: {e}")
                    if context.pages:
                        CURRENT_PAGE = context.pages[-1]
                        print(f"Recovered control of tab: {CURRENT_PAGE.url}")
                        wait_for_dom_stability(CURRENT_PAGE)
                    else:
                        print("No pages available, exiting...")
                        break

        finally:
            try:
                browser.close()
            except:
                pass
            

PORT = 3001  # Different from your Vite port

class RequestHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Process your prompt
            result = self.process_prompt(data.get('prompt', ''))
            
            # Always return valid JSON
            response = {
                'status': 'success',
                'message': result.get('message', ''),
                'details': result.get('details', {})
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            # Error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': str(e)
            }).encode('utf-8'))
    
    def process_prompt(self, prompt):
        
        try:

                # Generic processing for other prompts
            plan = {
                "steps": [
                    {
                        "action": "evaluate",
                        "description": f"Analyzing: {prompt}",
                        "result": f"I'll help you with: {prompt}"
                    }
                ]
            }
            interactive_angular_navigator(prompt)
            success = execute_plan(CURRENT_PAGE, get_navigation_plan(prompt))
            
            return {
                "status": "success" if success else "error",
                "message": self.generate_response(prompt, plan, success),
                "details": plan
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing your request: {str(e)}"
            }

    def generate_response(self, prompt, plan, success):
        """Generate natural language response based on the plan"""
        if not success:
            return "I couldn't complete that action. Please try again."
        
        # Default response
        actions = [step['description'] for step in plan.get('steps', [])]
        return f"I've completed these actions for you:\n- " + "\n- ".join(actions)

def run_server():
    server_address = ('', 3001)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Starting server on port 3001")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()