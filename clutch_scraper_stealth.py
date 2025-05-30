import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
import time
import json
import csv
import os
import random

BASE_URL = "https://clutch.co/developers/python-django"
TOTAL_PAGES = 10  # You can increase this value as needed


# ✅ Initialize stealth Chrome driver with realistic options
def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    # ✅ Fake user-agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    # ✅ Optional: Proxy support (replace with a working proxy if needed)
    # options.add_argument('--proxy-server=http://123.123.123.123:8080')

    driver = uc.Chrome(options=options)
    return driver


# ✅ Scroll the page and simulate realistic user behavior
def scroll_and_behave(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2, 4))
    body = driver.find_element(By.TAG_NAME, "body")
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(body, 100, 100).perform()
    time.sleep(random.uniform(1, 2))


# ✅ Load and parse a page of company cards
def get_company_cards(driver, page_number=0):
    url = f"{BASE_URL}?page={page_number}"
    driver.get(url)
    scroll_and_behave(driver)

    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.provider.provider-row"))
        )
        print(f"🔍 Page {page_number + 1} loaded.")
    except:
        print(f"❌ Timeout on page {page_number + 1}")
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup.select("div.provider.provider-row")


# ✅ Extract information from a single company card
def parse_company_card(card):
    def get_attr(tag, attr):
        return tag[attr] if tag and attr in tag.attrs else None

    name_tag = card.find("h3", class_="provider__title")
    name = name_tag.get_text(strip=True) if name_tag else None
    profile_link_tag = name_tag.find("a") if name_tag else None
    profile_url = get_attr(profile_link_tag, "href")
    if profile_url and not profile_url.startswith("http"):
        profile_url = "https://clutch.co" + profile_url

    website_tag = card.find("a", class_="website-link__item")
    website_raw = get_attr(website_tag, "href")
    website = unquote(parse_qs(urlparse(website_raw).query).get("u", [None])[0]) if website_raw else None

    def find_field(cls):
        block = card.find("div", attrs={"class": lambda x: x and cls in x})
        return block.get_text(strip=True) if block else None

    location = find_field("location")
    hourly_rate = find_field("hourly-rate")
    employee_range = find_field("employees-count")
    min_project_size = find_field("min-project-size")

    review_block = card.find("div", class_="provider__rating")
    review_count = get_attr(review_block.find("meta", itemprop="reviewCount"), "content") if review_block else None
    rating = get_attr(review_block.find("meta", itemprop="ratingValue"), "content") if review_block else None

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


# ✅ Save the results to JSON
def save_to_json(data, filename):
    os.makedirs("output", exist_ok=True)
    with open(f"output/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ✅ Save the results to CSV
def save_to_csv(data, filename):
    os.makedirs("output", exist_ok=True)
    keys = data[0].keys()
    with open(f"output/{filename}", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


# ✅ Main workflow
def main():
    print("🚀 Starting stealth browser...")
    driver = init_driver()
    all_results = []

    for page_number in range(TOTAL_PAGES):
        print(f"⏳ Scraping page {page_number + 1}/{TOTAL_PAGES}...")
        cards = get_company_cards(driver, page_number)
        results = [parse_company_card(card) for card in cards]
        all_results.extend(results)
        time.sleep(random.uniform(2, 4))  # polite wait

    driver.quit()

    print(f"✅ Scraped {len(all_results)} companies.")
    save_to_json(all_results, "clutch_leads_stealth.json")
    save_to_csv(all_results, "clutch_leads_stealth.csv")
    print("📁 Data saved to output folder.")


if __name__ == "__main__":
    main()

