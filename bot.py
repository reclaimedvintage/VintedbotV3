import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

API_URL = "https://www.vinted.co.uk/api/v2/catalog/items"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.vinted.co.uk/",
}


# ✅ Brands to track
BRANDS = [
    "ralph", "polo",
    "nike",
    "carhartt",
    "patagonia",
    "north face", "tnf"
]

# ✅ Sizes to allow
VALID_SIZES = ["S", "M", "L"]


def send_to_discord(item, priority=False):
    tag = "🚨 HIGH PRIORITY DEAL 🚨\n" if priority else ""

    image_url = None
    if item.get("photo"):
        image_url = item["photo"]["url"]

    data = {
        "embeds": [
            {
                "title": f"{tag}{item['title']}",
                "url": item["url"],
                "description": f"💷 £{item['price']}\n📏 Size: {item.get('size_title', 'N/A')}",
                "image": {"url": image_url} if image_url else {},
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


def is_valid_item(item):
    title = item["title"].lower()
    size = item.get("size_title", "").upper()

    # ✅ Brand check
    if not any(brand in title for brand in BRANDS):
        return False

    # ✅ Size filter
    if size not in VALID_SIZES:
        return False

    # ✅ Remove junk
    bad_keywords = [
        "kids", "baby", "fake", "replica",
        "bundle", "job lot", "damaged",
        "primark", "shein"
    ]

    if any(b in title for b in bad_keywords):
        return False

    return True


def main():
    print("Starting MULTI-BRAND SNIPER...")

    params = {
        "search_text": "",   # ✅ VERY IMPORTANT: no restriction
        "order": "newest_first",
        "per_page": 100
    }

    response = requests.get(API_URL, headers=HEADERS, params=params)

    print("Status:", response.status_code)

    if response.status_code != 200:
        print("API blocked or failed")
        return

    data = response.json()
    items = data.get("items", [])

    print(f"Items found: {len(items)}")

    sent = 0

    for item in items:
        try:
            price = float(item["price"])

            # ✅ Price filter
            if price > 20:
                continue

            # ✅ Validate brand + size + junk
            if not is_valid_item(item):
                continue

            # ✅ Priority flag
            priority = price <= 12

            send_to_discord(item, priority)
            sent += 1

        except Exception as e:
            print("Error:", e)

    print(f"✅ Sent {sent} items")


if __name__ == "__main__":
    main()
