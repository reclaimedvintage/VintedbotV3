import requests
from bs4 import BeautifulSoup
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

BASE_URL = "https://www.vinted.co.uk/catalog"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Accept-Language": "en-GB,en;q=0.9"
}


def send_to_discord(title, price, link):
    try:
        data = {
            "content": f"👕 **Ralph Lauren Item**\n\n{title}\n💷 {price}\n🔗 {link}"
        }
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print("Discord error:", e)


def scrape_page(page):
    url = f"{BASE_URL}?search_text=ralph+lauren&order=newest_first&page={page}"

    print(f"Scraping page {page}...")

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("Blocked or failed on page", page)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.feed-grid__item")

    return items


def main():
    print("Starting multi-page bot...")

    total_sent = 0

    # ✅ Scrape first 5 pages (adjust if needed)
    for page in range(1, 6):

        items = scrape_page(page)
        print(f"Items on page {page}: {len(items)}")

        for item in items:
            try:
                link_tag = item.find("a", href=True)
                if not link_tag:
                    continue

                link = "https://www.vinted.co.uk" + link_tag["href"]

                title_tag = item.find("p")
                title = title_tag.text.strip() if title_tag else "No title"

                price_tag = item.find("span")
                price = price_tag.text.strip() if price_tag else "?"

                title_lower = title.lower()

                # ✅ Only Ralph Lauren related
                if not any(word in title_lower for word in ["ralph", "polo", "rl"]):
                    continue

                send_to_discord(title, price, link)
                total_sent += 1

            except Exception as e:
                print("Error:", e)

        # ✅ Small delay between pages (avoid blocking)
        time.sleep(2)

    print(f"✅ Total items sent: {total_sent}")


if __name__ == "__main__":
    main()
