import os

from playwright.sync_api import sync_playwright


def run_cuj(page):
    page.goto("http://localhost:18780")

    # Handle onboarding if it appears
    try:
        page.wait_for_selector("#setup-username", timeout=2000)
        page.fill("#setup-username", "TestUser")
        page.fill("#setup-age", "30")
        page.get_by_role("button", name="Complete Setup").click()
        page.wait_for_timeout(2000)
    except Exception:
        pass

    page.wait_for_timeout(1000)

    # Click the "Search chats" button in the sidebar
    search_button = page.get_by_text("Search chats").first
    search_button.click()
    page.wait_for_timeout(1000)

    # Type "Hello" in the search input
    page.fill("#search-modal-input", "Hello")
    page.wait_for_timeout(1000)

    # Click the search button instead of Enter
    search_icon_button = page.get_by_role("button", name="Search", exact=True)
    search_icon_button.click()
    page.wait_for_timeout(2000)

    # Take screenshot at the key moment showing search modal
    page.screenshot(path="tests/e2e/screenshots/search_modal_with_button.png")
    page.wait_for_timeout(1000)

    # Close it and try Projects
    close_button = page.get_by_label("Close Search")
    close_button.click()
    page.wait_for_timeout(1000)

    # Open Projects
    projects_button = page.get_by_text("Projects").first
    projects_button.click()
    page.wait_for_timeout(2000)
    page.screenshot(path="tests/e2e/screenshots/projects_modal.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    os.makedirs("tests/e2e/screenshots", exist_ok=True)
    os.makedirs("tests/e2e/videos", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="tests/e2e/videos",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
