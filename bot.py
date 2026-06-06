import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = "https://discord.com/api/webhooks/1512845629938860242/cI1uxNg-J9TFNZJThRcJVg0AX6Y-I5SP4_V44OyzvPL0V6Rg_6MuasGmzQ_NFRWL5Ng3"

URL = "https://www.vinted.co.uk/vetements?search_text=ralph+lauren"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
    "Accept-Language": "en-GB,en;q=0.9"
}


def send_to_discord(title, price, link):
    data = {
        "content": f"🔥 **New Find!**\n\n👕 {title}\n💷 {price}\n🔗 {link}"
    }
    requests.post(WEBHOOK_URL, json=data)


def main():
    response = requests.get(URL, headers=HEADERS)

    print("Status:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.find_all("a", href=True)

    results = []

    for item in items:
        link = item.get("href")

        if "/items/" not in link:
            continue

        title = item.get_text(strip=True)

        if not title:
            continue

        full_link = "https://www.vinted.co.uk" + link

        results.append((title, full_link))

    print(f"Found {len(results)} items")

    sent = 0

    for title, link in results:
        title_lower = title.lower()

        if "ralph" not in title_lower:
            continue

        keywords = ["jumper", "sweater", "knit", "cable", "hoodie"]

        if not any(k in title_lower for k in keywords):
            continue

        # crude price check (visible in title sometimes)
        if "£" in title:
            try:
                price = title.split("£")[-1].split()[0]
                if float(price) > 30:
                    continue
            except:
                price = "?"

        else:
            price = "?"

        send_to_discord(title, price, link)
        sent += 1

    print(f"Sent {sent} items")


if __name__ == "__main__":
    main()
