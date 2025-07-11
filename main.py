import pandas as pd
from playwright.sync_api import sync_playwright
import subprocess

# Ensure browsers are installed
subprocess.run(["playwright", "install", "chromium"], check=True)

def scrape_aspen_dealers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Intercept the network request that contains dealer data
        dealers_json = {}

        def handle_response(response):
            if "wp-json/wp/v2/dealers" in response.url and response.status == 200:
                try:
                    json_data = response.json()
                    dealers_json.update(json_data)
                except:
                    pass

        page.on("response", handle_response)
        page.goto("https://www.aspenfuels.us/outlets/find-dealer/", timeout=60000)
        page.wait_for_timeout(8000)

        browser.close()
        return dealers_json.get('locations', [])

# Run and save
data = scrape_aspen_dealers()
df = pd.DataFrame(data)

if not df.empty:
    df = df.rename(columns={
        'store': 'name',
        'zip': 'zip',
    })[["name", "address", "city", "state", "zip", "phone", "lat", "lng", "url"]]

df.to_csv("aspen_us_dealers.csv", index=False)
print(f"✅ Scraped {len(df)} dealers and saved to aspen_us_dealers.csv")
