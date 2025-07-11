import pandas as pd
from playwright.sync_api import sync_playwright
import subprocess

# Install browsers (Render needs this on each deploy)
subprocess.run(["playwright", "install", "chromium"], check=True)

def scrape_aspen_dealers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("➡️ Visiting Aspen dealer locator...")
        page.goto("https://www.aspenfuels.us/outlets/find-dealer/", timeout=60000)

        # Wait for JS variable to load (instead of a DOM element)
        page.wait_for_function(
            "window.storeLocator && window.storeLocator.locations && window.storeLocator.locations.length > 0",
            timeout=15000
        )

        # Pull data directly from JS variable
        dealer_data = page.evaluate("""
            () => {
                return window.storeLocator.locations.map(loc => ({
                    name: loc.store,
                    address: loc.address,
                    city: loc.city,
                    state: loc.state,
                    zip: loc.zip,
                    phone: loc.phone,
                    lat: loc.lat,
                    lng: loc.lng,
                    url: loc.url
                }));
            }
        """)

        browser.close()
        return dealer_data

if __name__ == "__main__":
    data = scrape_aspen_dealers()
    df = pd.DataFrame(data)
    df.to_csv("aspen_us_dealers.csv", index=False)
    print(f"✅ Scraped {len(df)} dealers and saved to aspen_us_dealers.csv")

