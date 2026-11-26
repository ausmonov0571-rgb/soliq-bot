import os
import urllib.parse
import urllib.request

from test_kanal import KANALLAR, Postlar

TOKEN = os.environ["TELEGRAM_TOKEN"].strip()
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"].strip()


def yubor(matn):
    manzil = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": matn}).encode()
    urllib.request.urlopen(manzil, data=data, timeout=30)


def oxirgi_post(kanal):
    sorov = urllib.request.Request(
        "https://t.me/s/" + kanal, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(sorov, timeout=30).read().decode("utf-8")
    p = Postlar()
    p.feed(html)
    return p.postlar[-1]


for kanal in KANALLAR:
    havola, matn = oxirgi_post(kanal)
    yubor(kanal + "\n\n" + matn[:3000] + "\n\nManba: " + havola)
    print("Yuborildi:", kanal)
