import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

URL = "https://www.vinted.co.uk/catalog?search_text=ralph+lauren&order=newest_first"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Accept-Language": "en-GB,en;q=0.9"
}


def send_to_discord(title, price, link):
    try:
        message = {
            "content": f"🔥 **New Find!**\n\n👕 {title}\n💷 {price}\n🔗 {link}"
        }

        response = requests.post(WEBHOOK_URL, json=message)
        print("Discord status:", response.status_code)

    except Exception as e:
        print("Discord error:", e)


def main():
    print("Starting bot...")

    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        print("Website status:", response.status_code)

    except Exception as e:
        print("Request failed:", e)
        return

    if response.status_code != 200:
        print("Blocked or failed request")
        send_to_discord("⚠️ Vinted blocked the request", "N/A", URL)
        return

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.feed-grid__item")

    print("Items detected:", len(items))

    if len(items) == 0:
        send_to_discord("⚠️ No items found (likely blocked)", "N/A", URL)
        return

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

            if "ralph" not in title_lower:
                continue

            keywords = ["jumper", "sweater", "knit", "cable", "hoodie"]

            if not any(k in title_lower for k in keywords):
                continue

            try:
                clean_price = float(price.replace("£", "").strip())
                if clean_price > 30:
                    continue
            except:
                pass

            send_to_discord(title, price, link)
            sent += 1

        except Exception as e:
            print("Item error:", e)

    print("Sent items:", sent)


if __name__ == "__main__":
    main()
