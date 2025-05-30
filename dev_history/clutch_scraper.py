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

BASE_URL = "https://clutch.co/developers/python-django"

# Setup Selenium Chrome driver
def init_driver():
    options = Options()
    # options.add_argument("--headless")  # Run browser in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
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

# Load page and parse company cards
def get_company_cards(driver, page_number=0):
    url = f"{BASE_URL}?page={page_number}"
    driver.get(url)
    
    try:
        # Wait up to 20 seconds until the company cards are visible
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.provider.provider-row"))
        )
        # Try to scroll the page to trigger lazy-load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Give time for lazy-loaded content
        print(f"🔍 Page {page_number} loaded and scrolled.")
    except:
        print("❌ Timeout: Company cards not found.")
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup.select("div.provider.provider-row")

# Parse individual company card
def parse_company_card(card):
    # Extract company name
    name_tag = card.find("h3", class_="provider__title")
    name = name_tag.get_text(strip=True) if name_tag else None

    # Extract Clutch profile URL
    profile_link_tag = name_tag.find("a") if name_tag else None
    profile_url = profile_link_tag["href"] if profile_link_tag else None
    if profile_url and not profile_url.startswith("http"):
        profile_url = "https://clutch.co" + profile_url

    # Extract external website (from redirect URL)
    website_tag = card.find("a", class_="website-link__item")
    if website_tag and "href" in website_tag.attrs:
        raw_url = website_tag["href"]
        parsed = parse_qs(urlparse(raw_url).query)
        website = unquote(parsed.get("u", [None])[0])
    else:
        website = None

    # Extract location (via flexible class match)
    location_block = card.find("div", attrs={"class": lambda x: x and "location" in x})
    location = location_block.get_text(strip=True) if location_block else None

    # Extract hourly rate
    rate_block = card.find("div", attrs={"class": lambda x: x and "hourly-rate" in x})
    hourly_rate = rate_block.get_text(strip=True) if rate_block else None

    # Extract employee range
    employee_block = card.find("div", attrs={"class": lambda x: x and "employees-count" in x})
    employee_range = employee_block.get_text(strip=True) if employee_block else None

    # Extract minimum project size
    min_project_block = card.find("div", attrs={"class": lambda x: x and "min-project-size" in x})
    min_project_size = min_project_block.get_text(strip=True) if min_project_block else None

    # Extract review count and rating
    review_block = card.find("div", class_="provider__rating")
    review_count_tag = review_block.find("meta", itemprop="reviewCount") if review_block else None
    review_count = review_count_tag["content"] if review_count_tag else None

    rating_tag = review_block.find("meta", itemprop="ratingValue") if review_block else None
    rating = rating_tag["content"] if rating_tag else None

    # Extract description
    description_tag = card.find("p", class_="provider__description-text-more")
    description = description_tag.get_text(strip=True) if description_tag else None

    return {
        "name": name,
        "profile_url": profile_url,
        "website": website,
        "location": location,
        "hourly_rate": hourly_rate,
        "employee_range": employee_range,
        "min_project_size": min_project_size,
        "review_count": review_count,
        "rating": rating,
        "description": description
    }

# Save results to JSON file
def save_to_json(data, filename):
    os.makedirs("output", exist_ok=True)
    with open(f"output/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_to_csv(data, filename):
    os.makedirs("output", exist_ok=True)
    keys = data[0].keys()
    with open(f"output/{filename}", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# Save page HTML content for debugging
def debug_save_html(driver, filename="debug_output.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

# Main script
def main():
    print("🚀 Starting browser...")
    driver = init_driver()
    all_results = []

    total_pages = 3  # You can increase this later if needed

    for page_number in range(total_pages):
        print(f"⏳ Scraping page {page_number + 1} of {total_pages}...")
        cards = get_company_cards(driver, page_number=page_number)
        page_results = [parse_company_card(card) for card in cards]
        all_results.extend(page_results)
        time.sleep(2)  # polite delay to avoid rate limiting

    debug_save_html(driver)
    driver.quit()

    print(f"✅ Total {len(all_results)} companies scraped.")
    save_to_json(all_results, "clutch_leads.json")
    print("📁 Saved to 'output/clutch_leads.json'")
    save_to_csv(all_results, "clutch_leads.csv")
    print("📁 Saved to 'output/clutch_leads.csv'")

if __name__ == "__main__":
    main()

