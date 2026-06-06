import requests
import time
import random

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

SEARCH_URL = "https://www.vinted.co.uk/api/v2/catalog/items"

PARAMS = {
    "search_text": "ralph lauren",
    "price_to": 20,
    "currency": "GBP",
    "order": "newest_first",
    "per_page": 20
}

seen_ids = set()


def send_to_discord(item):
    message = {
        "content": f"🔥 **New Find!**\n\n👕 {item['title']}\n💷 £{item['price']}\n🔗 {item['url']}"
    }

    requests.post(WEBHOOK_URL, json=message)


def get_items():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(SEARCH_URL, params=PARAMS, headers=headers)
    return response.json()["items"]


def is_good_item(item):
    keywords = ["jumper", "sweater", "knit", "cable", "vintage"]

    title = item["title"].lower()

    if float(item["price"]) > 20:
        return False

    return any(word in title for word in keywords)


def main():
    while True:
        try:
            items = get_items()

            for item in items:
                if item["id"] in seen_ids:
                    continue

                if not is_good_item(item):
                    continue

                seen_ids.add(item["id"])

                send_to_discord({
                    "title": item["title"],
                    "price": item["price"],
                    "url": item["url"]
                })

            time.sleep(random.randint(90, 180))

        except Exception as e:
            print("Error:", e)
            time.sleep(60)


if __name__ == "__main__":
    main()
