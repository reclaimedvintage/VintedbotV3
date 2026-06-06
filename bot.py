import requests
from bs4 import BeautifulSoup
import time
import json
import os
import re

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

BASE_URL = "https://www.vinted.co.uk/catalog"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Accept-Language": "en-GB,en;q=0.9"
}

SEEN_FILE = "seen_items.json"


# ✅ Load seen items
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


# ✅ Save seen items
def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def extract_item_id(url):
    match = re.search(r"/items/(\d+)", url)
    return match.group(1) if match else url


def send_to_discord(title, price, link, image):
    data = {
        "embeds": [
            {
                "title": title,
                "url": link,
                "description": f"💷 {price}",
                "image": {"url": image} if image else {},
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=data)


def scrape_page(page):
    url = f"{BASE_URL}?search_text=ralph+lauren&order=newest_first&page={page}"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("Blocked on page", page)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("div.feed-grid__item")


def main():
    print("Starting PRO bot...")

    seen = load_seen()
    new_seen = set()

    total_sent = 0

    for page in range(1, 6):
        print(f"Checking page {page}...")

        items = scrape_page(page)

        for item in items:
            try:
                a_tag = item.find("a", href=True)
                if not a_tag:
                    continue

                href = a_tag["href"]
                link = "https://www.vinted.co.uk" + href if href.startswith("/") else href

                item_id = extract_item_id(link)

                # ✅ Skip duplicates
                if item_id in seen:
                    continue

                # ✅ Title
                title = a_tag.get("title") or a_tag.get_text(strip=True)
                if not title:
                    continue

                # ✅ Price
                price_tag = item.select_one("span")
                price = price_tag.get_text(strip=True) if price_tag else "?"

                # ✅ Image
                img_tag = item.find("img")
                image = img_tag["src"] if img_tag and "src" in img_tag.attrs else None

                title_lower = title.lower()

                # ✅ Ralph Lauren filter
                if not any(x in title_lower for x in ["ralph", "polo", "rl"]):
                    continue

                # ✅ Optional SNIPER MODE (uncomment to activate)
                """
                try:
                    price_value = float(price.replace("£", "").strip())
                    if price_value > 20:
                        continue
                except:
                    pass
                """

                send_to_discord(title, price, link, image)

                new_seen.add(item_id)
                total_sent += 1

            except Exception as e:
                print("Error:", e)

        time.sleep(2)

    # ✅ Save updated seen list
    seen.update(new_seen)
    save_seen(seen)

    print(f"✅ Sent {total_sent} NEW items")


if __name__ == "__main__":
    main()
