import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

# ✅ Broad search (ALL Ralph Lauren items)
URL = "https://www.vinted.co.uk/catalog?search_text=ralph+lauren&order=newest_first"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Accept-Language": "en-GB,en;q=0.9"
}


def send_to_discord(title, price, link):
    try:
        data = {
            "content": f"👕 **Ralph Lauren Item**\n\n{title}\n💷 {price}\n🔗 {link}"
        }
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print("Discord error:", e)


def main():
    print("Starting bot...")

    response = requests.get(URL, headers=HEADERS)
    print("Website status:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.feed-grid__item")

    print(f"Items detected: {len(items)}")

    sent = 0

    for item in items:
        try:
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue

            link = "https://www.vinted.co.uk" + link_tag["href"]

            title_tag = item.find("p")
            title = title_tag.text.strip() if title_tag else "No title"

            price_tag = item.find("span")
            price = price_tag.text.strip() if price_tag else "?"

            title_lower = title.lower()

            # ✅ ONLY check it's Ralph Lauren related
            if not any(word in title_lower for word in ["ralph", "polo", "rl"]):
                continue

            send_to_discord(title, price, link)
            sent += 1

        except Exception as e:
            print("Error:", e)

    print(f"✅ Sent items: {sent}")


if __name__ == "__main__":
    main()
