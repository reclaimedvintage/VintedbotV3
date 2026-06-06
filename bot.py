import requests
from bs4 import BeautifulSoup

# ✅ YOUR DISCORD WEBHOOK
WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

# ✅ VINTED SEARCH PAGE (REAL WEBSITE)
URL = "https://www.vinted.co.uk/catalog?search_text=ralph+lauren&order=newest_first"

# ✅ HEADERS (VERY IMPORTANT - makes it look like a real phone user)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Accept-Language": "en-GB,en;q=0.9"
}


def send_to_discord(title, price, link):
    message = {
        "content": f"🔥 **New Find!**\n\n👕 {title}\n💷 {price}\n🔗 {link}"
    }

    response = requests.post(WEBHOOK_URL, json=message)

    print(f"Sent to Discord: {response.status_code}")


def main():
    print("Starting bot...")

    # ✅ Request the real Vinted page
    response = requests.get(URL, headers=HEADERS)

    print("Website status:", response.status_code)

    # ✅ Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ Find listings (this is the correct container)
    items = soup.select("div.feed-grid__item")

    print(f"Items detected on page: {len(items)}")

    sent_count = 0

    for item in items:
        try:
            # ✅ Extract link
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue

            link = "https://www.vinted.co.uk" + link_tag["href"]

            # ✅ Extract title
            title_tag = item.find("p")
            title = title_tag.text.strip() if title_tag else "No title"

            # ✅ Extract price
            price_tag = item.find("span")
            price = price_tag.text.strip() if price_tag else "?"

            # ✅ FILTERING
            title_lower = title.lower()

            if "ralph" not in title_lower:
                continue

