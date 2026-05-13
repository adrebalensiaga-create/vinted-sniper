[13-05-2026 21:49] Ростик: import requests
import time
import os
import re
import random
import json

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ---------------- SETTINGS ----------------

filters = {
    "stone island": "🟢",
    "gucci": "🔴",
    "balenciaga": "⚫",
    "nike": "👟"
}

SEEN_FILE = "seen.json"

# проверка каждые 3-5 минут
MIN_DELAY = 180
MAX_DELAY = 300

# отдых после нескольких циклов
BREAK_AFTER_MIN = 8
BREAK_AFTER_MAX = 12

# отдых 30-45 минут
BREAK_MIN = 1800
BREAK_MAX = 2700

# ---------------- SESSION ----------------

session = requests.Session()

session.headers.update({
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
    ])
})

# ---------------- SEEN SYSTEM ----------------

if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r") as f:
            seen = set(json.load(f))
    except:
        seen = set()
else:
    seen = set()


def save_seen():
    try:
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen), f)
    except Exception as e:
        print("SAVE ERROR:", e)

# ---------------- TELEGRAM ----------------

def send_photo(photo, caption):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "photo": photo,
                "caption": caption
            },
            timeout=20
        )
    except Exception as e:
        print("PHOTO SEND ERROR:", e)


def send_text(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=15
        )
    except Exception as e:
        print("TEXT SEND ERROR:", e)

# ---------------- FETCH ITEMS ----------------

def fetch_items(brand):
    try:

        search = brand.replace(" ", "+")

        url = (
            f"https://www.vinted.ee/catalog"
            f"?search_text={search}"
            f"&order=newest_first"
        )

        r = session.get(url, timeout=20)

        if r.status_code != 200:
            print("STATUS ERROR:", r.status_code)
            return []

        html = r.text

        ids = list(dict.fromkeys(
            re.findall(r'/items/(\d+)', html)
        ))

        items = []

        for item_id in ids[:40]:

            item_url = f"https://www.vinted.ee/items/{item_id}"

            items.append({
                "id": item_id,
                "url": item_url
            })

        return items

    except Exception as e:
        print("FETCH ERROR:", e)
        return []

# ---------------- ITEM INFO ----------------

def get_item_info(item_url):

    try:
        r = session.get(item_url, timeout=20)

        html = r.text

        img_match = re.search(
            r'"url":"(https:[^"]+)"',
            html
        )

        image = None

        if img_match:
            image = img_match.group(1)
            image = image.replace("\\", "")

        price_match = re.search(
            r'"price":"([^"]+)"',
            html
        )

        price = "?"
        if price_match:
            price = price_match.group(1)

        return {
            "image": image,
            "price": price
        }

    except Exception as e:
        print("ITEM INFO ERROR:", e)

        return {
            "image": None,
            "price": "?"
        }

# ---------------- MAIN ----------------

print("🚀 SNIPER STARTED")
send_text("🚀 VINTED SNIPER LIVE")

cycle_count = 0
break_after = random.randint(BREAK_AFTER_MIN, BREAK_AFTER_MAX)

while True:

    try:

        brands = list(filters.items())

        random.shuffle(brands)

        for brand, emoji in brands:

            print("📡 checking:", brand)

            items = fetch_items(brand)

            for item in items:

                item_id = item["id"]
[13-05-2026 21:49] Ростик: if item_id in seen:
                    continue

                seen.add(item_id)
                save_seen()

                info = get_item_info(item["url"])

                caption = f"""{emoji} NEW ITEM

🏷 {brand}
💰 {info['price']}

🔗 {item['url']}"""

                if info["image"]:
                    send_photo(info["image"], caption)
                else:
                    send_text(caption)

                print("📩 SENT:", item["url"])

                time.sleep(random.randint(7, 15))

            time.sleep(random.randint(8, 18))

        cycle_count += 1

        if cycle_count >= break_after:

            sleep_time = random.randint(BREAK_MIN, BREAK_MAX)

            print(f"😴 LONG BREAK: {sleep_time}s")

            send_text("😴 sniper resting...")

            time.sleep(sleep_time)

            cycle_count = 0
            break_after = random.randint(
                BREAK_AFTER_MIN,
                BREAK_AFTER_MAX
            )

        sleep_time = random.randint(MIN_DELAY, MAX_DELAY)

        print(f"⏳ sleep: {sleep_time}s")

        time.sleep(sleep_time)

    except Exception as e:

        print("MAIN ERROR:", e)

        time.sleep(60)
