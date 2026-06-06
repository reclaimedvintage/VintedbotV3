import requests
from bs4 import BeautifulSoup
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

BASE_URL = "https://www.vinted.co.uk/catalog"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Accept-Language": "en-GB,en;q=0.9"
}


def send_to_discord(title, price, link, image, priority=False):
    tag = "🚨 **HIGH PRIORITY DEAL** 🚨\n" if priority else ""

    data = {
        "embeds": [
            {
                "title": f"{tag}{title}",
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
        print("Blocked page:", page)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("div.feed-grid__item")


def is_valid_item(title):
    title = title.lower()

    # ✅ MUST contain strong RL indicator
    valid_brand = ["ralph", "polo ralph", "polo by ralph"]
    if not any(v in title for v in valid_brand):
        return False

    # ✅ GOOD resale categories
    good_keywords = [
        "jumper", "sweater", "knit", "cable",
        "hoodie", "zip", "quarter", "shirt",
        "jacket", "coat", "fleece"
    ]

    if not any(k in title for k in good_keywords):
        return False

    # ❌ REMOVE JUNK TERMS
    bad_keywords = [
        "kids", "baby", "fake", "inspired",
        "bundle", "job lot", "damaged",
        "worn out", "xs women", "primark"
    ]

    if any(b in title for b in bad_keywords):
        return False

    return True


def main():
    print("Starting PROFIT SNIPER...")

    total_sent = 0

    for page in range(1, 5):  # ✅ fewer pages = faster detection
        print(f"Checking page {page}...")

        items = scrape_page(page)

        for item in items:
            try:
                a_tag = item.find("a", href=True)
                if not a_tag:
                    continue

                link = "https://www.vinted.co.uk" + a_tag["href"]

                title = a_tag.get("title") or a_tag.get_text(strip=True)
                if not title:
                    continue

                price_tag = item.select_one("span")
                price_text = price_tag.get_text(strip=True) if price_tag else "?"

                # ✅ CLEAN PRICE
                try:
                    price_value = float(price_text.replace("£", "").strip())
                except:
                    continue

                # ✅ HARD PRICE FILTER
                if price_value > 20:
                    continue

                if not is_valid_item(title):
                    continue

                # ✅ IMAGE
                img_tag = item.find("img")
                image = img_tag["src"] if img_tag and "src" in img_tag.attrs else None

                # ✅ PRIORITY ALERT
                priority = price_value <= 12

                send_to_discord(title, price_text, link, image, priority)

                total_sent += 1

            except Exception as e:
                print("Error:", e)

        time.sleep(1)  # ✅ faster but still safe

    print(f"✅ Sent {total_sent} items")


if __name__ == "__main__":
    main()
