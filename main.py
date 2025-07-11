import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_aspen_dealers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.aspenfuels.us/outlets/find-dealer/", timeout=60000)
        page.wait_for_timeout(8000)

        # Extract raw dealer data from map markers
        dealer_data = page.evaluate("""
            () => {
                const markers = window.storeLocator?.locations || [];
                return markers.map(m => ({
                    name: m.store,
                    address: m.address,
                    city: m.city,
                    state: m.state,
                    zip: m.zip,
                    phone: m.phone,
                    lat: m.lat,
                    lng: m.lng,
                    url: m.url
                }));
            }
        """)

        browser.close()
        return dealer_data

data = scrape_aspen_dealers()
df = pd.DataFrame(data)
df.to_csv("aspen_us_dealers.csv", index=False)
print(f"✅ Scraped {len(df)} dealers and saved to aspen_us_dealers.csv")
