import json
import os
import time
import urllib.parse
import urllib.request

from test_kanal import KANALLAR, Postlar

TOKEN = os.environ["TELEGRAM_TOKEN"].strip()
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"].strip()
HOLAT = "holat.json"   # qaysi postgacha yuborilgani


def yubor(matn):
    manzil = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": matn}).encode()
    urllib.request.urlopen(manzil, data=data, timeout=30)
    time.sleep(1)


def postlarni_ol(kanal):
    sorov = urllib.request.Request(
        "https://t.me/s/" + kanal, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(sorov, timeout=30).read().decode("utf-8")
    p = Postlar()
    p.feed(html)
    return p.postlar


def raqam(havola):
    return int(havola.rsplit("/", 1)[1])


holat = {}
if os.path.exists(HOLAT):
    with open(HOLAT) as f:
        holat = json.load(f)

for kanal in KANALLAR:
    postlar = postlarni_ol(kanal)
    if kanal in holat:
        yangi = [p for p in postlar if raqam(p[0]) > holat[kanal]][:10]
    else:
        yangi = postlar[-1:]   # birinchi marta faqat oxirgisi
    for havola, matn in yangi:
        yubor(kanal + "\n\n" + matn[:3000] + "\n\nManba: " + havola)
        holat[kanal] = raqam(havola)
        with open(HOLAT, "w") as f:
            json.dump(holat, f)
    print(kanal, "- yuborildi:", len(yangi))
