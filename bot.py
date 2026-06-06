import requests
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

API_URL = "https://www.vinted.co.uk/api/v2/catalog/items"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
}

SEARCHES = [
    "ralph lauren",
    "nike",
    "carhartt",
    "patagonia",
    "north face"
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
                "description": f"💷 £{item['price']}\n📏 Size: {item.get('size_title', 'N/A')}",
                "image": {"url": image} if image else {}
            }
        ]
    }

    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print("Discord error:", e)


def is_valid(item):
    title = item["title"].lower()
    size = item.get("size_title", "").upper()

    # ✅ Size filter
    if size not in VALID_SIZES:
        return False

    # ❌ Remove junk
    bad_keywords = [
        "kids", "baby", "fake", "replica",
        "bundle", "job lot", "damaged",
        "primark", "shein"
    ]

    if any(b in title for b in bad_keywords):
        return False

    return True


def fetch_items(search_term):
    params = {
        "search_text": search_term,
        "order": "newest_first",
        "per_page": 100
    }

    try:
        response = requests.get(API_URL, headers=HEADERS, params=params)
        print(f"{search_term} → Status: {response.status_code}")

        if response.status_code != 200:
            return []

        return response.json().get("items", [])

    except Exception as e:
        print("API error:", e)
        return []


def main():
    print("Starting MULTI-BRAND SNIPER...")

    seen_ids = set()
    total_sent = 0

    for search in SEARCHES:
        print(f"\nChecking: {search}")

        items = fetch_items(search)
        print(f"Found {len(items)} items")

