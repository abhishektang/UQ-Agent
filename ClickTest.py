from playwright.sync_api import sync_playwright
import re
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from vector_db import initialize_vector_db


class Action(Enum):
    CLICK = "click"
    HOVER = "hover"
    FILL = "fill"
    TYPE = "type"


ELEMENT_CACHE = {}
CURRENT_PAGE = None
LAST_ACTION_TIME = 0

VECTOR_DB = initialize_vector_db()


def get_navigation_plan(user_prompt: str) -> Dict:
    """
    Get navigation plan for a user's prompt by querying similar examples from vector database.

    Args:
        user_prompt (str): The user's goal or command to generate a plan for

    Returns:
        Dict: A dictionary containing the action plan with steps
    """
    # Get similar examples from vector database
    similar_examples = VECTOR_DB.get_similar_examples(user_prompt)
    # Return the first matching plan if found, otherwise return empty plan
    return similar_examples[0]["plan"] if similar_examples else {"steps": []}

def get_cache_key(url: str, element_description: str) -> str:
    return f"{url}|||{element_description.lower().strip()}"


def cache_element_selector(url: str, element_description: str, selector: str, element_info: Dict):
    cache_key = get_cache_key(url, element_description)
    ELEMENT_CACHE[cache_key] = {
        'selector': selector,
        'element_info': element_info,
        'timestamp': time.time()
    }


def get_cached_element(url: str, element_description: str) -> Optional[Tuple[str, Dict]]:
    cache_key = get_cache_key(url, element_description)
    cached = ELEMENT_CACHE.get(cache_key)
    if cached:
        return cached['selector'], cached['element_info']
    return None, None


def find_text_area_element(page, description: str) -> Optional[Any]:
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
                    if box and box['width'] > 300 and box['height'] > 100:
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


def find_course_element(page, course_code: str) -> Optional[Any]:
    """Specialized function to find course elements in UQ systems"""
    # Clean the course code (remove brackets and spaces)
    clean_code = course_code.replace('[', '').replace(']', '').replace(' ', '').upper()

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
            if element:
                return element
        except:
            continue

    # Fallback: Find by text in course cards
    try:
        course_cards = page.query_selector_all('.course-card, [class*="course-node"]')
        for card in course_cards:
            text = card.inner_text().upper().replace(' ', '')
            if clean_code in text:
                return card
    except:
        pass

    return None

def find_element_by_text(page, text: str, threshold: int = 5) -> Optional[Any]:
    # First try to find course elements if text contains a course code
    course_code_match = re.search(r'(\[?[A-Za-z]{2,}\s?\d{3,}\]?)', text.upper())
    if course_code_match:
        course_code = course_code_match.group(1)
        course_element = find_course_element(page, course_code)
        if course_element:
            return course_element

    # Original fuzzy matching logic for other elements
    try:
        elements = page.query_selector_all(
            'button, a, [role=button], [role=link], [ng-click], [click], input, textarea, [role="textbox"], div[contenteditable="true"]')
    except:
        return None

    best_match = None
    highest_score = 0

    for element in elements:
        try:
            element_text = element.inner_text().strip()
            if not element_text:
                if element.evaluate('el => el.tagName.toLowerCase()') in ('input', 'textarea'):
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

            score = fuzz.token_sort_ratio(element_text.lower(), text.lower())
            if score > highest_score and score >= threshold:
                highest_score = score
                best_match = element
        except:
            continue

    return best_match if highest_score >= threshold else None


def ensure_element_visible(page, element):
    try:
        element.evaluate('element => element.scrollIntoView({block: "center"})')
        element.wait_for_element_state("visible", timeout=5000)
        element.wait_for_element_state("stable", timeout=5000)
        page.wait_for_timeout(500)  # Increased delay for stability
    except Exception as e:
        print(f"Warning: Could not ensure element visibility - {e}")


def perform_action_on_element(page, action: Action, element_description: str, value: str = None) -> bool:
    global LAST_ACTION_TIME

    try:
        current_url = page.url
    except:
        print("Page is no longer available")
        return False

    # Extract potential course code from description
    course_code_match = re.search(r'(\[?[A-Za-z]{2,}\s?\d{3,}\]?)', element_description.upper())
    if course_code_match:
        course_code = course_code_match.group(1).replace('[', '').replace(']', '').replace(' ', '')

        # First try to find exact course code element
        course_elements = page.query_selector_all('[class*="course"], [id*="course"], [data-course-code]')
        for element in course_elements:
            try:
                element_text = element.inner_text().strip()
                if f"[{course_code}]" in element_text or course_code in element_text.replace(' ', ''):
                    return _execute_action(page, action, element, element_description, value)
            except:
                continue

    # Rest of the original function remains the same...
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except:
        print("Warning: Page took too long to load, proceeding anyway")

    cached_selector, _ = get_cached_element(current_url, element_description)
    if cached_selector:
        try:
            element = page.query_selector(cached_selector)
            if element:
                return _execute_action(page, action, element, element_description, value)
        except Exception as e:
            print(f"Cache action failed: {e}")

    if action in (Action.FILL, Action.TYPE) and any(word in element_description.lower()
                                                    for word in
                                                    ['post', 'content', 'reply', 'comment', 'text', 'message']):
        element = find_text_area_element(page, element_description)
        if element:
            try:
                return _execute_action(page, action, element, element_description, value)
            except Exception as e:
                print(f"Action failed on text area: {e}")

    element = find_element_by_text(page, element_description)
    if element:
        try:
            return _execute_action(page, action, element, element_description, value)
        except Exception as e:
            print(f"Action failed on found element: {e}")

    print(f"Could not find element matching: {element_description}")
    return False


def _execute_action(page, action: Action, element, element_description: str, value: str = None) -> bool:
    global CURRENT_PAGE, LAST_ACTION_TIME

    try:
        current_url = page.url
    except:
        print("Page is no longer available")
        return False

    try:
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
            # Try multiple click strategies
            try:
                element.click(timeout=10000)
            except:
                # Fallback to JavaScript click
                page.evaluate('(element) => element.click()', element)

            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "text_match", "text": text}
            )
            LAST_ACTION_TIME = time.time()
            return True
        elif action == Action.HOVER:
            element.hover(timeout=10000)
            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "text_match", "text": text}
            )
            LAST_ACTION_TIME = time.time()
            return True
        elif action == Action.FILL and value:
            element.fill(value)
            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "input_field", "text": text}
            )
            LAST_ACTION_TIME = time.time()
            return True
        elif action == Action.TYPE and value:
            element.click()
            page.keyboard.type(value)
            cache_element_selector(
                current_url,
                element_description,
                selector,
                {"type": "text_area", "text": text}
            )
            LAST_ACTION_TIME = time.time()
            return True
    except Exception as e:
        print(f"Error executing action: {e}")
        return False

    return False


def parse_user_command(user_prompt: str) -> Tuple[Action, str, Optional[str]]:
    user_prompt = user_prompt.lower().strip()

    type_match = re.match(r'^(type|write|enter)\s+(?:in|into)\s+(.+?)\s+(.+)$', user_prompt)
    if type_match:
        return Action.TYPE, type_match.group(2).strip(), type_match.group(3).strip()

    fill_match = re.match(r'^(fill|enter|input)\s+(.+?)\s+(?:with|as)\s+(.+)$', user_prompt)
    if fill_match:
        return Action.FILL, fill_match.group(2).strip(), fill_match.group(3).strip()

    if user_prompt.startswith(('click', 'select', 'choose', 'press', 'open')):
        element_desc = re.sub(r'^(click|select|choose|press|open)\s*', '', user_prompt).strip()
        return Action.CLICK, element_desc, None
    if user_prompt.startswith(('hover', 'mouse over')):
        element_desc = re.sub(r'^(hover|mouse over)\s*', '', user_prompt).strip()
        return Action.HOVER, element_desc, None

    return Action.CLICK, user_prompt, None


def get_active_page(context):
    """Get the most recently active page, waiting briefly for new pages if needed"""
    global CURRENT_PAGE, LAST_ACTION_TIME

    # If we recently performed an action that might open a new tab, wait a bit
    if time.time() - LAST_ACTION_TIME < 3:
        for _ in range(5):
            if len(context.pages) > 1:
                # Find the newest page that's not the current one
                new_pages = [p for p in context.pages if p != CURRENT_PAGE]
                if new_pages:
                    return new_pages[-1]
            time.sleep(0.5)

    # Return current page if it's still valid, otherwise the last page in context
    if CURRENT_PAGE and not CURRENT_PAGE.is_closed():
        return CURRENT_PAGE
    return context.pages[-1] if context.pages else None


def interactive_angular_navigator():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        global CURRENT_PAGE, LAST_ACTION_TIME
        CURRENT_PAGE = context.pages[0] if context.pages else None
        LAST_ACTION_TIME = time.time()

        def handle_new_page(new_page):
            global CURRENT_PAGE, LAST_ACTION_TIME
            print(f"\nNew tab opened: {new_page.url}")
            CURRENT_PAGE = new_page
            LAST_ACTION_TIME = time.time()
            print(f"Now controlling tab: {CURRENT_PAGE.url}")

            # Wait for the new page to be ready
            try:
                CURRENT_PAGE.wait_for_load_state("networkidle", timeout=20000)
            except Exception as e:
                print(f"Warning: New tab took too long to load - {e}")

        context.on("page", handle_new_page)

        print("Connected to browser. New tabs will immediately switch control.")
        print("Examples:")
        print("- 'Click COMP3702 course card'")
        print("- 'Mark as complete'")
        print("- 'Hover over user profile'")
        print("- 'Fill username with myuser123'")
        print("- 'Type in post content Hello world'")

        while True:
            try:
                user_prompt = input("\nWhat would you like to do? (or 'quit' to exit): ").strip()
                if user_prompt.lower() == 'quit':
                    break
                if not user_prompt:
                    continue

                # Get the most appropriate page to work with
                current_page = get_active_page(context)
                if not current_page or current_page.is_closed():
                    if context.pages:
                        CURRENT_PAGE = context.pages[-1]
                        current_page = CURRENT_PAGE
                        print(f"Recovered control of tab: {current_page.url}")
                    else:
                        print("No pages available, exiting...")
                        break

                action, element_desc, value = parse_user_command(user_prompt)
                success = perform_action_on_element(current_page, action, element_desc, value)

                if not success:
                    print(f"Failed to perform action: {user_prompt}")
            except Exception as e:
                print(f"Error processing command: {e}")
                # Try to recover by getting the active page
                if context.pages:
                    CURRENT_PAGE = context.pages[-1]
                    print(f"Recovered control of tab: {CURRENT_PAGE.url}")
                else:
                    print("No pages available, exiting...")
                    break


if __name__ == "__main__":
    interactive_angular_navigator()