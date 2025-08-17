from playwright.sync_api import sync_playwright
import requests
import json
import base64
import time

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"  # Using Qwen3:8b model


class TextClickAutomation:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
        self.page = self.browser.contexts[0].pages[0]

    def capture_screenshot(self) -> str:
        """Capture screenshot of the current page and return as base64"""
        screenshot_bytes = self.page.screenshot(full_page=True)
        return base64.b64encode(screenshot_bytes).decode('utf-8')

    def query_ollama(self, prompt: str, image_data= None):
        """Send prompt to Ollama with optional image data"""
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1}
        }

        if image_data:
            payload["images"] = [image_data]

        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying Ollama: {e}")
            return {"error": str(e)}

    def find_text_to_click(self, user_command: str) -> str:
        """Ask the model to identify the exact text to click"""
        screenshot = self.capture_screenshot()

        prompt = f"""
        The user wants to: "{user_command}".

        Look at the screenshot and identify the exact visible text of the clickable element 
        that best matches this request. Respond ONLY with the exact text to click, nothing else.

        Example requests and responses:
        User: "click the login button"
        Response: "Login"

        User: "click the assessment tab"
        Response: "Assessments"

        User: "open the settings menu"
        Response: "Settings"
        """

        response = self.query_ollama(prompt, screenshot)
        if "error" in response:
            raise Exception(f"Model error: {response['error']}")

        # Extract just the text (models sometimes add extra commentary)
        text = response["response"].strip().strip('"').strip("'").split("\n")[0]
        return text

    def click_text(self, text: str):
        """Attempt to click on text element"""
        try:
            self.page.get_by_text(text, exact=True).click()
            return {"status": "success", "action": "click", "text": text}
        except Exception as e:
            return {"status": "error", "message": str(e), "text": text}

    def execute_command(self, user_command: str):
        """Full pipeline: find text and click it"""
        try:
            text_to_click = self.find_text_to_click(user_command)
            return self.click_text(text_to_click)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def close(self):
        """Clean up resources"""
        self.browser.close()
        self.playwright.stop()


# Example usage
if __name__ == "__main__":
    agent = TextClickAutomation()

    try:
        # Example commands to try:
        commands = [
            "click the artificial intelligence",
        ]

        for cmd in commands:
            print(f"\nExecuting command: '{cmd}'")
            result = agent.execute_command(cmd)
            print("Result:", json.dumps(result, indent=2))
            time.sleep(2)  # Pause between commands

    finally:
        agent.close()