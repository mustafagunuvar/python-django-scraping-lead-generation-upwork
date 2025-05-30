from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
import csv
import json
import os
import time
import random

# User-Agent list for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

BASE_URL = "https://clutch.co/developers/python-django"

# Setup Selenium Chrome driver with enhanced stealth
def init_driver():
    options = Options()
    
    # Random user agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'user-agent={user_agent}')
    
    # Additional stealth settings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Headless mode can trigger Cloudflare more easily
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    
    # Disable images to speed up loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Execute stealth.js to hide automation
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        window.navigator.chrome = {
            runtime: {},
        };
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        """
    })
    
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    
    return driver

# Enhanced page loading with retry mechanism
def get_company_cards(driver, page_number=0, retries=3):
    url = f"{BASE_URL}?page={page_number}"
    
    for attempt in range(retries):
        try:
            driver.get(url)
            
            # Random delay to mimic human behavior
            time.sleep(random.uniform(2, 5))
            
            # Check for Cloudflare challenge
            if "Checking if the site connection is secure" in driver.page_source:
                print("⚠️ Cloudflare challenge detected. Waiting...")
                time.sleep(random.uniform(10, 20))  # Increased wait time
                continue
            
            # Wait for company cards
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.provider.provider-row"))
            )
            
            # Human-like scrolling
            for _ in range(random.randint(1, 3)):
                scroll_px = random.randint(500, 1000)
                driver.execute_script(f"window.scrollBy(0, {scroll_px});")
                time.sleep(random.uniform(0.5, 2))
            
            print(f"🔍 Page {page_number} loaded successfully.")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            return soup.select("div.provider.provider-row")
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                # Change user agent and proxy between retries
                user_agent = random.choice(USER_AGENTS)
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
                time.sleep(random.uniform(5, 10))
            else:
                print(f"❌ Failed to load page {page_number} after {retries} attempts.")
                return []

# ... (rest of the code remains the same until main function)

def main():
    print("🚀 Starting browser with enhanced stealth settings...")
    driver = init_driver()
    all_results = []
    
    total_pages = 3
    
    try:
        for page_number in range(total_pages):
            print(f"⏳ Scraping page {page_number + 1} of {total_pages}...")
            
            # Random delay between pages
            time.sleep(random.uniform(3, 8))
            
            cards = get_company_cards(driver, page_number=page_number)
            if not cards:
                print(f"⚠️ No cards found on page {page_number}. Skipping...")
                continue
                
            page_results = [parse_company_card(card) for card in cards]
            all_results.extend(page_results)
            
            # Random action to mimic human behavior
            if random.random() > 0.7:  # 30% chance to perform random action
                if random.random() > 0.5:
                    driver.back()
                    time.sleep(random.uniform(2, 5))
                    driver.forward()
                else:
                    driver.refresh()
                    time.sleep(random.uniform(3, 6))
    
    except Exception as e:
        print(f"❌ Critical error occurred: {str(e)}")
    finally:
        debug_save_html(driver)
        driver.quit()
    
    if all_results:
        print(f"✅ Total {len(all_results)} companies scraped.")
        save_to_json(all_results, "clutch_leads.json")
        print("📁 Saved to 'output/clutch_leads.json'")
        save_to_csv(all_results, "clutch_leads.csv")
        print("📁 Saved to 'output/clutch_leads.csv'")
    else:
        print("❌ No data was scraped. Check for blocking issues.")