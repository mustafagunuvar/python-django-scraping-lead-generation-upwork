import requests
import re
import json
import os
from bs4 import BeautifulSoup

INPUT_FILE = "output/clutch_leads_stealth.json"
OUTPUT_FILE = "output/enriched_with_email.json"

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def extract_emails_from_website(url):
    try:
        if not url:
            return None
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        matches = re.findall(EMAIL_REGEX, text)
        unique_emails = list(set(matches))

        # Return only first email found for now
        return unique_emails[0] if unique_emails else None

    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def enrich_data_with_emails(data):
    for company in data:
        website = company.get("website")
        print(f"🔍 Looking for email in: {website}")
        email = extract_emails_from_website(website)
        company["email"] = email
    return data

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        companies = json.load(f)

    enriched_data = enrich_data_with_emails(companies)

    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Email enrichment complete. Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
