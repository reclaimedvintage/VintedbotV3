import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

API_URL = "https://www.vinted.co.uk/api/v2/catalog/items"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
}

BRANDS = [
    "ralph", "polo",
    "nike",
    "carhartt",
    "patagonia",
    "north face", "tnf"
]

VALID_SIZES = ["S", "M", "L"]


def send_to_discord(item, priority=False):
    tag = "🚨 HIGH PRIORITY DEAL 🚨\n" if priority else ""

    image = item["photo"]["url"] if item.get("photo") else None

    data = {
        "embeds": [
            {
                "title": f"{tag}{item['title']}",
                "url": item["url"],
                "description": f"💷 £{item['price']}\n📏 Size: {item.get('size_title','N/A')}",
                "image": {"url": image} if image else {}
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)


def is_valid(item):
    title = item["title"].lower()
    size = item.get("size_title", "").upper()

    # ✅ Brand check
    if not any(b in title for b in BRANDS):
        return False

    # ✅ Size
    if size not in VALID_SIZES:
        return False

    # ✅ Remove junk
    bad = ["kids", "baby", "fake", "replica", "bundle", "damaged"]
    if any(x in title for x in bad):
        return False

    return True


def main():
    print("Starting MULTI-BRAND SNIPER...")

    params = {
        "search_text": "nike",   # ✅ KEY FIX (see below)
        "order": "newest_first",
        "per_page": 100,
    }

    response = requests.get(API_URL, headers=HEADERS, params=params)

    print("Status:", response.status_code)

    if response.status_code != 200:
        print("API blocked — switching strategy")
        return

    items = response.json().get("items", [])
    print(f"Items found: {len(items)}")

    sent = 0

    for item in items:
        try:
            price = float(item["price"])

            if price > 20:
                continue

            if not is_valid(item):
                continue

            priority = price <= 12

            send_to_discord(item, priority)
            sent += 1

        except Exception as e:
            print("Error:", e)

    print(f"✅ Sent {sent} items")


if __name__ == "__main__":
    main()
