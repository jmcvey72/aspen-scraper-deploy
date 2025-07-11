import pandas as pd
from playwright.sync_api import sync_playwright
import subprocess
import json

# Ensure Chromium is installed
subprocess.run(["playwright", "install", "chromium"], check=True)

def scrape_aspen_dealers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        dealer_data = []

        def handle_response(response):
            if "dealers" in response.url and response.status == 200 and response.request.resource_type == "xhr":
                try:
                    json_data = response.json()
                    if isinstance(json_data, dict) and "locations" in json_data:
                        dealer_data.extend(json_data["locations"])
                except Exception as e:
                    print(f"Failed to parse dealer JSON: {e}")

        page.on("response", handle_response)

        print("➡️ Visiting Aspen dealer locator page...")
        page.goto("https://www.aspenfuels.us/outlets/find-dealer/", timeout=60000)
        page.wait_for_timeout(10000)  # wait for data to load

        browser.close()
        return dealer_data

# Run and save results
data = scrape_aspen_dealers()
df = pd.DataFrame(data)

if not df.empty:
    df = df.rename(columns={
        'store': 'name',
        'zip': 'zip'
    })[["name", "address", "city", "state", "zip", "phone", "lat", "lng", "url"]]

df.to_csv("aspen_us_dealers.csv", index=False)
print(f"✅ Scraped {len(df)} dealers and saved to aspen_us_dealers.csv")
