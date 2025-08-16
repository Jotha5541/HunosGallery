import time
from playwright.sync_api import sync_playwright

def scrape(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        for _ in range(5):
            page.keyboard.press("End")
            time.sleep(2)  # Wait for the page to load completely
        content = page.content()
        browser.close()
        return content
    
if __name__ == "__main__":
    url = "https://www.pinterest.com/search/pins/?q=John%20Harris&rs=typed"
    artworks = scrape(url)
    
    for art in artworks:
        print(art)