# 🕸️ Python & Django Lead Generation Scraper (Clutch.co)

> 🚀 A complete Lead Generation pipeline that scrapes top Python & Django development companies from Clutch.co — **with advanced CAPTCHA/Cloudflare bypass**, email enrichment, and insightful analytics.

---

## ✨ Project Summary

This project is designed to **extract, enrich, and analyze** B2B company data from Clutch.co’s Python & Django developer directory. It goes beyond basic scraping by handling real-world obstacles such as **Cloudflare protections and CAPTCHA challenges**, making it robust, production-ready, and **Upwork portfolio-worthy**.

---

## 🎯 Objectives

- Scrape **10+ pages** of company listings from Clutch.co
- Extract structured data (company name, location, hourly rate, employee size, website, etc.)
- Automatically **bypass CAPTCHA & Cloudflare protection**
- Visit each company website and **extract business emails**
- Perform **data cleaning, enrichment, and analysis**
- Save outputs in `.json` and `.csv`
- Visualize insights in a Jupyter notebook

---

## 🔐 Bypassing CAPTCHA & Cloudflare (Key Challenge Solved ✅)

Clutch.co uses **Cloudflare’s anti-bot protection** and sometimes **CAPTCHA validation** to block automation tools.

We solved this using:

- ✅ `undetected_chromedriver` for stealthy Selenium sessions
- ✅ Custom browser headers & realistic user-agent
- ✅ Human-like mouse movements and scroll simulation
- ✅ Manual fallback if CAPTCHA appears (browser opens visually)

> 🔥 Unlike most scrapers that fail silently after the first page, **our script successfully scraped 830 companies across 10 pages** — even under strict bot protection.

---

## 🧩 Tech Stack

- `Python 3.10+`
- `Selenium` with `undetected-chromedriver`
- `BeautifulSoup` for HTML parsing
- `pandas` for data wrangling
- `matplotlib / seaborn` for visualizations
- `re`, `urllib`, and `json` for processing & formatting

---

## 📦 Folder Structure

```bash
├── clutch_scraper_stealth.py       # Main scraping script (Cloudflare-safe)
├── email_enricher.py               # Extracts emails from websites
├── output/
│   ├── clutch_leads_stealth.json
│   ├── clutch_leads_stealth.csv
│   ├── enriched_with_email.json
├── analysis/
│   └── insights.ipynb              # Data cleaning + visualization
├── dev_history                     # Notes and logs from earlier development phases
├── requirements.txt                # Python dependencies
├── README.md                       # This file

