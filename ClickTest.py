from playwright.sync_api import sync_playwright
import requests
import json
import re
from typing import List, Dict, Optional

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "uqagent"  # Replace with your preferred model


def query_ollama(prompt: str, context: str = "") -> Optional[str]:
    """Query the Ollama API with a prompt and optional context"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{context}\n\n{prompt}",
        "stream": False,
        "options": {"temperature": 0.3}  # More deterministic responses
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        return json.loads(response.text)["response"]
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None


def get_angular_element_descriptions(page) -> List[Dict]:
    """Get enhanced descriptions of interactive elements with AngularJS attributes"""
    # Query all interactive elements including Angular-specific ones
    elements = page.query_selector_all(
        'button, input, a, [ng-click], [ng-model], [role=button], [role=link], '
        '[bb-click-to-invoke-child], [analytics-id], article.element-card, '
        '[data-analytics-id], .click-to-invoke-container, .ax-focusable-title'
    )

    descriptions = []
    for element in elements:
        try:
            # Get standard attributes
            tag = element.evaluate("el => el.tagName.toLowerCase()")
            text = element.inner_text().strip() or ""
            placeholder = element.get_attribute("placeholder") or ""
            aria_label = element.get_attribute("aria-label") or ""
            name = element.get_attribute("name") or ""
            id = element.get_attribute("id") or ""
            title = element.get_attribute("title") or ""
            class_list = element.get_attribute("class") or ""

            # Get Angular-specific attributes
            ng_click = element.get_attribute("ng-click") or ""
            ng_model = element.get_attribute("ng-model") or ""
            analytics_id = element.get_attribute("analytics-id") or ""
            bb_click = element.get_attribute("bb-click-to-invoke-child") or ""
            data_analytics_id = element.get_attribute("data-analytics-id") or ""

            # Special handling for course cards
            if tag == "article" and "element-card" in class_list:
                course_name = element.query_selector(".js-course-title-element")
                if course_name:
                    text = course_name.inner_text().strip()
                    id = element.get_attribute("id") or ""
                    descriptions.append({
                        "tag": tag,
                        "text": text,
                        "id": id,
                        "type": "course_card",
                        "selector": f"article#{id}" if id else f"article:has-text('{text}')"
                    })
                continue

            # Special handling for click-to-invoke containers
            if "click-to-invoke-container" in class_list:
                title_element = element.query_selector('.ax-focusable-title')
                if title_element:
                    text = title_element.inner_text().strip()
                    descriptions.append({
                        "tag": tag,
                        "text": text,
                        "type": "click_to_invoke",
                        "selector": f".click-to-invoke-container:has-text('{text}')"
                    })
                continue

            # Build description
            if any([text, placeholder, aria_label, name, id, ng_click, ng_model, analytics_id, bb_click,
                    data_analytics_id, title]):
                desc = {
                    "tag": tag,
                    "text": text,
                    "placeholder": placeholder,
                    "aria_label": aria_label,
                    "name": name,
                    "id": id,
                    "title": title,
                    "ng_click": ng_click,
                    "ng_model": ng_model,
                    "analytics_id": analytics_id,
                    "bb_click": bb_click,
                    "data_analytics_id": data_analytics_id,
                    "selector": ""
                }

                # Create a good selector for this element
                if id:
                    desc["selector"] = f"#{id}"
                elif data_analytics_id:
                    desc["selector"] = f"[data-analytics-id='{data_analytics_id}']"
                elif text:
                    desc["selector"] = f"{tag}:has-text('{text}')"
                elif aria_label:
                    desc["selector"] = f"{tag}[aria-label='{aria_label}']"
                elif name:
                    desc["selector"] = f"{tag}[name='{name}']"
                elif analytics_id:
                    desc["selector"] = f"{tag}[analytics-id='{analytics_id}']"
                elif title:
                    desc["selector"] = f"{tag}[title='{title}']"

                descriptions.append(desc)
        except Exception as e:
            continue

    return descriptions


def find_best_matching_element(page, element_description: str) -> Optional[Dict]:
    """Find the best matching element based on the description, strongly preferring title matches."""
    elements = get_angular_element_descriptions(page)
    desc_lower = element_description.lower()

    # Step 1: Try to find direct title matches first
    title_matches = []
    for el in elements:
        title_text = str(el.get("title") or "").lower()
        heading_text = str(el.get("text") or "").lower()
        aria_label = str(el.get("aria_label") or "").lower()

        # A title match is considered exact or contains the search phrase
        if desc_lower in title_text or desc_lower in heading_text:
            score = 100  # Very high base score for title matches
            if el.get("tag") == "button":
                score += 10  # Button bonus
            title_matches.append((score, el))

    if title_matches:
        return max(title_matches, key=lambda x: x[0])[1]

    # Step 2: If no title matches, fall back to general scoring
    scored_elements = []
    for el in elements:
        score = 0

        if "text" in el and desc_lower in str(el["text"]).lower():
            score += 3
        if "aria_label" in el and desc_lower in str(el["aria_label"]).lower():
            score += 3
        if "placeholder" in el and desc_lower in str(el["placeholder"]).lower():
            score += 2
        if "name" in el and desc_lower in str(el["name"]).lower():
            score += 2
        if "id" in el and desc_lower in str(el["id"]).lower():
            score += 1

        # Button preference
        if el.get("tag") == "button":
            score += 2

        if score > 0:
            scored_elements.append((score, el))

    return max(scored_elements, key=lambda x: x[0])[1] if scored_elements else None


def perform_action_on_element(page, action: str, element_description: str) -> bool:
    """Perform the specified action on the matching element"""
    element_info = find_best_matching_element(page, element_description)

    if not element_info:
        print(f"Could not find element matching: {element_description}")
        return False

    try:
        selector = element_info.get("selector")
        if not selector:
            print(f"No valid selector for element: {element_info}")
            return False

        element = page.query_selector(selector)
        if not element:
            print(f"Element not found with selector: {selector}")
            return False

        if action == "click":
            element.click()
            return True
        elif action.startswith("type:"):
            text_to_type = action.split("type:")[1].strip()
            element.fill(text_to_type)
            return True
        elif action == "press_enter":
            element.press("Enter")
            return True
        elif action == "hover":
            element.hover()
            return True
    except Exception as e:
        print(f"Error performing action: {e}")
        return False


def generate_ai_prompt(user_prompt: str, page_context: Dict) -> str:
    """Generate a detailed prompt for the AI"""
    return f"""
    The user wants to interact with an AngularJS webpage. Based on the page context below, determine:
    1. What action they want to perform (click, type text, press enter, hover)
    2. Which element they want to interact with (prioritize visible text, aria-labels, titles, course names)

    User command: "{user_prompt}"

    Current page title: {page_context.get('title', '')}
    Current URL: {page_context.get('url', '')}

    Respond in JSON format with these keys:
    - "action": one of ["click", "type:<text>", "press_enter", "hover"]
    - "element_description": a string identifying the element based on its most distinctive attribute

    Example responses:
    - For "click the COMP3702 course card":
    {{
        "action": "click",
        "element_description": "COMP3702"
    }}

    - For "click the Course Profile link":
    {{
        "action": "click",
        "element_description": "Course Profile"
    }}

    - For "mark as complete":
    {{
        "action": "click",
        "element_description": "Mark as complete"
    }}

    - For "search for artificial intelligence":
    {{
        "action": "type:artificial intelligence",
        "element_description": "search"
    }}

    - For "type myemail@example.com in the email field":
    {{
        "action": "type:myemail@example.com",
        "element_description": "email"
    }}
    """


def interactive_angular_navigator():
    """Interactive navigator specialized for AngularJS applications"""
    with sync_playwright() as p:
        # Connect to existing browser
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]

        # Cache page context
        page_context = {
            "title": page.title(),
            "url": page.url,
        }

        print("Connected to browser. You can now give commands to interact with the AngularJS page.")
        print("Examples: 'Click COMP3702 course card', 'Click Course Profile', 'Mark as complete'")
        warmup = query_ollama("This is just to warm you up. Just reply with '.'")
        while True:
            user_prompt = input("\nWhat would you like to do? (or 'quit' to exit): ").strip()

            if user_prompt.lower() == 'quit':
                break
            if not user_prompt:
                continue

            # Generate AI prompt
            ai_prompt = generate_ai_prompt(user_prompt, page_context)
            response = query_ollama(ai_prompt)

            if not response:
                print("Failed to get response from Ollama.")
                continue

            try:
                # Extract JSON from the response
                json_str = re.search(r'\{.*\}', response, re.DOTALL).group()
                command = json.loads(json_str)

                # Perform the action
                success = perform_action_on_element(page, command["action"], command["element_description"])

                if not success:
                    print(f"Failed to perform action. Original AI response: {response}")

                # Update cached context after action
                page_context = {
                    "title": page.title(),
                    "url": page.url,
                }
            except Exception as e:
                print(f"Error interpreting command: {e}")
                print(f"Original AI response: {response}")


if __name__ == "__main__":
    interactive_angular_navigator()