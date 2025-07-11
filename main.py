import pandas as pd
from playwright.sync_api import sync_playwright
import subprocess
import time

# Install browsers
subprocess.run(["playwright", "install", "chromium"], check=True)

def scrape_aspen_dealers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("➡️ Visiting Aspen dealer locator...")
        page.goto("https://www.aspenfuels.us/outlets/find-dealer/", timeout=60000)

        # Retry until window.storeLocator.locations is available
        max_attempts = 10
        attempt = 0
        store_data = None

        while attempt < max_attempts:
            try:
                store_data = page.evaluate("""
                    () => {
                        if (window.storeLocator?.locations?.length > 0) {
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
                        return null;
                    }
                """)
                if store_data:
                    break
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1}: JS variable not ready, retrying...")
            time.sleep(2)
            attempt += 1

        browser.close()

        if not store_data:
            raise RuntimeError("❌ Failed to load dealer data after multiple attempts.")

        return store_data

if __name__ == "__main__":
    data = scrape_aspen_dealers()
    df = pd.DataFrame(data)
    df.to_csv("aspen_us_dealers.csv", index=False)
    print(f"✅ Scraped {len(df)} dealers and saved to aspen_us_dealers.csv")
