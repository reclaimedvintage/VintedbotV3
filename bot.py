import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

WEBHOOK_URL = "PUT YOUR WEBHOOK HERE"

BASE_URL = "https://www.vinted.co.uk/catalog"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-GB,en;q=0.9"
}

SEEN_FILE = "seen_items.json"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def extract_id(url):
    match = re.search(r"/items/(\d+)", url)
    return match.group(1) if match else url


def send_to_discord(title, price, link, image):
    data = {
        "embeds": [
            {
                "title": title,
                "url": link,
                "description": f"💷 {price}",
                "image": {"url": image} if image else {}
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


def scrape_page(page):
    url = f"{BASE_URL}?search_text=ralph+lauren&order=newest_first&page={page}"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("Failed page:", page)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("div.feed-grid__item")


def is_valid(title, price, size):
    title = title.lower()

    # ✅ Must be Ralph Lauren
    if not ("ralph" in title or "polo" in title):
        return False

    # ✅ Size filter
    if size not in ["S", "M", "L"]:
        return False

    # ✅ Price filter
    try:
        if float(price.replace("£", "").strip()) > 20:
            return False
    except:
        return False

    # ❌ Remove junk
    bad = ["kids", "baby", "fake", "bundle", "job lot", "damaged"]
    if any(b in title for b in bad):
        return False

    return True


def main():
    print("Starting RL sniper...")

    seen = load_seen()
    new_seen = set()
    sent = 0

    for page in range(1, 6):  # ✅ multiple pages

        print(f"Page {page}")

        items = scrape_page(page)

        for item in items:
            try:
                a = item.find("a", href=True)
                if not a:
                    continue

                link = "https://www.vinted.co.uk" + a["href"]

                item_id = extract_id(link)

                # ✅ skip duplicates (across runs)
                if item_id in seen:
                    continue

                title = a.get("title") or a.get_text(strip=True)
                if not title:
                    continue

                price_tag = item.find("span")
                price = price_tag.get_text(strip=True) if price_tag else "?"

                size = item.get_text().upper()

                if not is_valid(title, price, size):
                    continue

                img = item.find("img")
                image = img["src"] if img and "src" in img.attrs else None

                send_to_discord(title, price, link, image)

                new_seen.add(item_id)
                sent += 1

            except Exception as e:
                print("Item error:", e)

        time.sleep(1)

    seen.update(new_seen)
    save_seen(seen)

    print(f"✅ Sent {sent} new items")


if __name__ == "__main__":
    main()
