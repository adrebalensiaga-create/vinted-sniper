import requests
import time
import os
import re

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

seen = set()

filters = {
    "stone island": "🟢",
    "gucci": "🔴",
    "balenciaga": "⚫️"
}

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

def send(text):

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

def fetch(brand):

    url = f"https://www.vinted.ee/catalog?search_text={brand.replace(' ', '%20')}"

    r = session.get(url, timeout=15)

    if r.status_code != 200:
        print("PAGE ERROR:", r.status_code)
        return []

    html = r.text

    ids = list(set(re.findall(r'/items/(\\d+)', html)))

    items = []

    for item_id in ids[:20]:

        items.append({
            "id": item_id,
            "url": f"https://www.vinted.ee/items/{item_id}"
        })

    return items

print("SNIPER STARTED")

send("🚀 CLOUD SNIPER STARTED")

while True:

    try:

        print("🔄 checking vinted...")

        for brand, emoji in filters.items():

            print("📡", brand)

            items = fetch(brand)

            for item in items:

                item_id = item["id"]

                if item_id in seen:
                    continue

                seen.add(item_id)

                msg = f"""{emoji} NEW ITEM

🏷 {brand}

🔗 {item['url']}"""

                print("📩 sent:", item["url"])

                send(msg)

        time.sleep(15)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(30)
