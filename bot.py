import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

SEARCH_URL = "https://www.vinted.co.uk/api/v2/catalog/items"

PARAMS = {
    "search_text": "ralph lauren",
    "currency": "GBP",
    "order": "newest_first",
    "per_page": 50  # more items = higher chance of results
}


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
    title = item["title"].lower()

    keywords = [
        "jumper", "sweater", "knit", "cable",
        "wool", "cotton", "hoodie", "zip", "quarter zip"
    ]

    # Must include Ralph Lauren
    if "ralph" not in title:
        return False

    # Price filter
    try:
        if float(item["price"]) > 25:   # slightly relaxed from £20
            return False
    except:
        return False

    # Broader keyword matching
    return any(word in title for word in keywords)


def main():
    items = get_items()

    found = 0

    for item in items:
        if not is_good_item(item):
            continue

        send_to_discord({
            "title": item["title"],
            "price": item["price"],
            "url": item["url"]
        })

        found += 1

    print(f"Sent {found} items")


if __name__ == "__main__":
    main()
