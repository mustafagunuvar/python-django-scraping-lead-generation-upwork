import asyncio
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs, unquote
import json
import csv
import os
import time

BASE_URL = "https://clutch.co/developers/python-django"
TOTAL_PAGES = 5


def extract_company_info(card):
    try:
        name = card.query_selector("h3.provider__title").inner_text().strip()
        profile_url = card.query_selector("h3.provider__title a").get_attribute("href")
        if profile_url and not profile_url.startswith("http"):
            profile_url = "https://clutch.co" + profile_url
    except:
        name = profile_url = None

    try:
        raw_website = card.query_selector("a.website-link__item").get_attribute("href")
        parsed = parse_qs(urlparse(raw_website).query)
        website = unquote(parsed.get("u", [None])[0])
    except:
        website = None

    def get_text_by_class(keyword):
        block = card.query_selector(f"div[class*='{keyword}']")
        return block.inner_text().strip() if block else None

    location = get_text_by_class("location")
    hourly_rate = get_text_by_class("hourly-rate")
    employee_range = get_text_by_class("employees-count")
    min_project_size = get_text_by_class("min-project-size")

    try:
        review_count = card.query_selector("meta[itemprop='reviewCount']").get_attribute("content")
        rating = card.query_selector("meta[itemprop='ratingValue']").get_attribute("content")
    except:
        review_count = rating = None

    try:
        description = card.query_selector("p.provider__description-text-more").inner_text().strip()
    except:
        description = None

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


def main():
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        for page_number in range(TOTAL_PAGES):
            print(f"⏳ Scraping page {page_number + 1}/{TOTAL_PAGES}...")
            url = f"{BASE_URL}?page={page_number}"
            page.goto(url, timeout=60000)

            detect_and_wait_for_captcha(page)  # CAPTCHA varsa kullanıcıya göster

            page.wait_for_selector("div.provider.provider-row", timeout=40000)

            cards = page.query_selector_all("div.provider.provider-row")
            for card in cards:
                info = extract_company_info(card)
                all_results.append(info)

            time.sleep(2)


        browser.close()

        save_to_json(all_results, "clutch_leads_playwright.json")
        save_to_csv(all_results, "clutch_leads_playwright.csv")
        print(f"✅ Total {len(all_results)} companies scraped.")
        print("📁 Data saved to output folder.")

def detect_and_wait_for_captcha(page):
    print("🧪 Checking for CAPTCHA...")
    try:
        captcha_found = page.query_selector("iframe[src*='turnstile']")  # turnstile (Cloudflare) kontrolü
        if captcha_found:
            print("🚧 CAPTCHA detected! Please solve it manually in the opened browser.")
            input("✅ Press ENTER after solving CAPTCHA to continue...")
    except:
        pass


if __name__ == "__main__":
    main()
