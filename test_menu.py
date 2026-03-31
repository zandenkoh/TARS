from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:18780")

        # take a screenshot and then check if the form is there
        time.sleep(2)
        page.screenshot(path="screenshot_check.png")

        try:
            page.wait_for_selector("#setup-username", timeout=3000)
            page.fill("#setup-username", "test")
            page.fill("#setup-age", "20")
            page.click("text=Complete Setup")
            time.sleep(2)
        except Exception:
            pass # Maybe not present

        page.screenshot(path="screenshot_after_setup.png")

        # click to open profile menu
        page.click("div[onclick='toggleProfileMenu()']")
        time.sleep(1)
        page.screenshot(path="screenshot_menu.png")

        # click Settings button within the menu
        page.click("text=Settings")
        time.sleep(2)
        page.screenshot(path="screenshot_settings.png")
        browser.close()

if __name__ == "__main__":
    run()
