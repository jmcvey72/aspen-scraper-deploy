import pandas as pd
from playwright.sync_api import sync_playwright
import subprocess

# Install browsers at runtime
subprocess.run(["playwright", "install", "chromium"], check=True)

def scrape_aspen_dealers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        dealer_data = []

        def handle_response(response):
            if "locations" in response.url and response.status == 200:
                try:
                    json_data = response.json()
                    if "locations" in json_data:
                        dealer_data.extend(json_data["locations"])
                        print(f"✅ Found {len(json_data['locations'])} dealers.")
                except Exception as e:
                    print(f"⚠️ Failed to parse response: {e}")

        page.on("response", handle_response)

        print("➡️ Visiting Aspen dealer locator...")
        page.goto("https://www.aspenfuels.us/outlets/find-dealer/", timeout=60000)

        # Wait for network request to complete
        page.wait_for_timeout(8000)

        browser.close()
        return dealer_data

# Run the scraper
data = scrape_aspen_dealers()
df = pd.DataFrame(data)

# Optional: clean & rename columns
if not df.empty:
    df = df.rename(columns={
        'store': 'name',
        'zip': 'zip'
    })[["name", "address", "city", "state", "zip", "phone", "lat", "lng", "url"]]

df.to_csv("aspen_us_dealers.csv", index=False)
print(f"✅ Scraped {len(df)} dealers and saved to aspen_us_dealers.csv")
