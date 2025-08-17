from dataclasses import dataclass
from typing import List, Dict, Optional
import re
import json
import requests
from playwright.sync_api import sync_playwright
import time

# ======== AGENT SYSTEM ========
@dataclass
class Action:
    type: str  # "goto", "click", "scroll", "expand_dropdown", etc.
    target: str  # URL, element description, or scroll direction
    value: str = ""  # For text input or scroll amount


class NavigatorAgent:
    def __init__(self):
        self.memory = {}  # Simple memory for course codes, etc.
        self.llm_url = "http://localhost:11434/api/generate"
        self.model = "llama3"  # Lighter model

    def plan_actions(self, goal: str) -> List[Action]:
        """Improved planning with course code recognition"""
        # Check memory for known course codes
        course_code = self._detect_course_code(goal)
        if course_code:
            return [
                Action("goto", "https://learn.uq.edu.au/ultra/course"),
                Action("click", course_code),
                Action("scroll", "down", "500"),
                Action("expand_dropdown", "Assessment"),
                Action("click", "assessment 0 - 2025"),
                Action("expand_dropdown", "assignment 0 - Task Description"),  # For dropdowns
                Action("click", "assignment 0 - Task Description")
            ]

        # Fallback to LLM for complex goals
        return self._llm_plan(goal)

    def _detect_course_code(self, text: str) -> Optional[str]:
        """Extract course codes like COMP3710"""
        matches = re.findall(r"\b([A-Z]{4}\d{4})\b", text.upper())
        return matches[0] if matches else None

    def _llm_plan(self, goal: str) -> List[Action]:
        """Lightweight LLM planning with expanded action types"""
        prompt = f"""Convert this UQ navigation goal to JSON actions:
Goal: {goal}

Available action types:
- "goto": navigate to URL
- "click": click on element with matching text
- "scroll": scroll page ("up"/"down") by pixels
- "expand_dropdown": expand a dropdown menu before clicking

Output format (ONLY respond with this exact format):
{{
  "actions": [
    {{"type": "goto", "target": "<url>"}},
    {{"type": "click", "target": "<element>"}},
    {{"type": "scroll", "target": "<direction>", "value": "<pixels>"}},
    {{"type": "expand_dropdown", "target": "<element>"}}
  ]
}}"""

        try:
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=10
            )
            data = json.loads(response.json().get("response", "{}"))
            return [Action(**a) for a in data.get("actions", [])]
        except:
            return []


# ======== INTEGRATED AUTOMATION ========
def run_agent_automation():
    agent = NavigatorAgent()

    with sync_playwright() as p:
        # Connect to existing Chrome instead of launching new browser
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0] if browser.contexts else browser.new_page()

        print(f"Connected to: {page.url}")

        while True:
            goal = input("\nUQ Navigation Goal (or 'quit'): ").strip()
            if goal.lower() == "quit":
                break

            actions = agent.plan_actions(goal)
            print(f"\nPlan: {actions}")

            for action in actions:
                try:
                    if action.type == "goto":
                        page.goto(action.target)
                        page.wait_for_load_state("networkidle")
                    elif action.type == "click":
                        page.click(f"text={action.target}")
                    elif action.type == "scroll":
                        if action.target.lower() == "down":
                            page.mouse.wheel(0, int(action.value or "300"))
                        else:  # default to up
                            page.mouse.wheel(0, -int(action.value or "300"))
                    elif action.type == "expand_dropdown":
                        # Hover to expand dropdown (if needed)
                        page.click(f"text={action.target}")
                        # Alternative: click the dropdown arrow if it exists
                        try:
                            page.click(f"text={action.target} >> xpath=./following-sibling::button")
                        except:
                            pass
                        time.sleep(1)  # Wait for dropdown to expand
                    time.sleep(1)
                except Exception as e:
                    print(f"Error executing {action.type}: {e}")
                    break


if __name__ == "__main__":
    run_agent_automation()