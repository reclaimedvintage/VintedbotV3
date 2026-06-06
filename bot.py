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
    data = {
        "content": f"👕 **Ralph Lauren**\n\n**{title}**\n💷 {price}\n🔗 {link}"
    }
    requests.post(WEBHOOK_URL, json=data)


def scrape_page(page):
    url = f"{BASE_URL}?search_text=ralph+lauren&order=newest_first&page={page}"

    print(f"Scraping page {page}...")

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("Failed page:", page)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ THIS SELECTOR TARGETS ACTUAL PRODUCT CARDS
    items = soup.select("div.feed-grid__item")

    return items


def main():
    print("Starting bot...")

    total_sent = 0

    for page in range(1, 6):  # first 5 pages
        items = scrape_page(page)
        print(f"Items found on page {page}: {len(items)}")

        for item in items:
            try:
                # ✅ LINK (correct)
                a_tag = item.find("a", href=True)
                if not a_tag:
                    continue

                href = a_tag["href"]

                # Ensure correct link formatting
                if href.startswith("/"):
                    link = "https://www.vinted.co.uk" + href
                else:
                    link = href

                # ✅ TITLE (more reliable extraction)
                title = a_tag.get("title")
                if not title:
                    title = a_tag.get_text(strip=True)

                if not title:
                    continue

                # ✅ PRICE (better extraction)
                price_tag = item.select_one("span[data-testid*='price']")
                if price_tag:
                    price = price_tag.get_text(strip=True)
                else:
                    # fallback
                    price_span = item.find("span")
                    price = price_span.get_text(strip=True) if price_span else "?"

                title_lower = title.lower()

                # ✅ FILTER: Ralph Lauren only
                if not any(x in title_lower for x in ["ralph", "polo", "rl"]):
                    continue

                send_to_discord(title, price, link)
                total_sent += 1

            except Exception as e:
                print("Item error:", e)

        time.sleep(2)

    print(f"✅ Total sent: {total_sent}")


if __name__ == "__main__":
    main()
