from playwright.sync_api import sync_playwright
from rapidfuzz import fuzz, process

user_input = "Assignment 0 - Task Description"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]

    # Get all visible elements
    all_elements = page.query_selector_all("*")
    visible_texts = []
    element_map = {}
    visible_elements = page.locator("*:visible")
    count = visible_elements.count()
    for i in range(count):
        el = visible_elements.nth(i)
        text = el.inner_text().strip()
        if text:
            visible_texts.append(text)
            element_map[text] = el

    # Find best match using fuzzy matching
    best_match = process.extractOne(user_input, visible_texts, scorer=fuzz.ratio)
    if best_match:
        matched_text = best_match[0]
        print(f"Clicking on: {matched_text}")
        element_map[matched_text].click()
    else:
        print("No matching element found")

    browser.close()
