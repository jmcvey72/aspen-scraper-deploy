import pandas as pd
from playwright.sync_api import sync_playwright
import subprocess

# Ensure Playwright is installed
subprocess.run(["playwright", "install", "chromium"], check=True)

def scrape_aspen_dealers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        dealer_data = []

        def handle_response(response):
            try:
                if "locations" in response.url and response.status == 200:
                    json_data = response.json()
                    if "locations" in json_data:
                        dealer_data.extend(json_data["locations"])
                        print(f"✅ Captured {len(json_data['locations'])} dealers from JSON.")
            except Exception as e:
                print(f"⚠️ Error parsing response from {response.url}: {e}")

        page.on("response", handle_response)

        print("➡️ Loading Aspen dealer page...")
        page.goto("https://www.aspenfuels.us/outlets/find-dealer/", timeout=60000)

        # Force the JavaScript to simulate a ZIP code search
        page.wait_for_selector("input[placeholder='Enter your location']", timeout=10000)
        page.fill("input[placeholder='Enter your location']", "90210")
        page.keyboard.press("Enter")

        # Wait for the network to fetch results
        page.wait_for_timeout(8000)

        browser.close()
        return dealer_data

data = scrape_aspen_dealers()

if not data:
    print("⚠️ No dealer data captured. Possible cause: network route not triggered or search returned nothing.")

df = pd.DataFrame(data)

if not df.empty:
    df = df.rename(columns={
        'store': 'name',
        'zip': 'zip'
    })[["name", "address", "city", "state", "zip", "phone", "lat", "lng", "url"]]

df.to_csv("aspen_us_dealers.csv", index=False)
print(f"✅ Done. Scraped {len(df)} dealers and saved to aspen_us_dealers.csv")

