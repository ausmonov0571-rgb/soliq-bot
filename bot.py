import html
import json
import os
import time
import urllib.parse
import urllib.request

from test_kanal import KANALLAR, Postlar

TOKEN = os.environ["TELEGRAM_TOKEN"].strip()
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"].strip()
HOLAT = "holat.json"   # qaysi postgacha yuborilgani
GEMINI_KEY = os.environ["GEMINI_API_KEY"].strip()
MODEL = "gemini-3.5-flash-lite"

TOPSHIRIQ = """Sen O'zbekistondagi yordamchi buxgalter uchun yangiliklarni saralaysan.
Quyidagi Telegram posti soliq, buxgalteriya, hisobot muddati yoki biznesga oid
qonunchilik bo'yicha foydali ma'lumot bermasa (reklama, kurs, tabrik, foto,
shaxsiy fikr, layfhak), faqat SKIP deb yoz.
Foydali bo'lsa, o'zbek tilida (lotin) sodda qilib yoz:
📌 Mavzu: ...
📝 Qisqacha: 2-3 ta sodda gap
👤 Kimga tegishli: ...
📅 Muddat: ... (postda bo'lmasa, bu qatorni yozma)
Postda yo'q raqam yoki sanani qo'shma. "Deyarli", "ayrim", "mumkin" kabi
so'zlarni tushirib qoldirma. Bu loyiha yoki taklif bo'lsa, Mavzu oldiga
(LOYIHA) deb yoz va Muddat qatorida "tasdiqlansa" so'zini ishlat.
Markdown belgilarini ishlatma.

POST:
"""

NOMLAR = {
    "soliqnews": "Soliq xizmati (rasmiy)",
    "Nurullo_Bobomuradov": "Nurullo Bobomuradov",
    "Afzalraximov": "Afzal Raximov",
}


def qisqartir(matn):
    manzil = ("https://generativelanguage.googleapis.com/v1beta/models/"
              + MODEL + ":generateContent")
    tana = {"contents": [{"parts": [{"text": TOPSHIRIQ + matn}]}]}
    sorov = urllib.request.Request(
        manzil, data=json.dumps(tana).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY})
    javob = json.load(urllib.request.urlopen(sorov, timeout=60))
    qismlar = javob["candidates"][0]["content"]["parts"]
    time.sleep(5)   # bepul tarif limitiga tushmaslik uchun
    return "".join(q.get("text", "") for q in qismlar if not q.get("thought")).strip()


def bezat(xulosa, kanal):
    qatorlar = []
    for q in html.escape(xulosa[:3000], quote=False).split("\n"):
        if q.startswith(("📌", "📝", "👤", "📅")) and ":" in q:
            sarlavha, qolgani = q.split(":", 1)
            q = "<b>" + sarlavha + ":</b>" + qolgani
        qatorlar.append(q)
    return ("🏛 <b>" + NOMLAR.get(kanal, kanal) + "</b>\n"
            + "━━━━━━━━━━━━\n"
            + "\n".join(qatorlar)
            + "\n\n<i>ℹ️ Sun'iy intellekt qisqartirdi. "
            + "Qo'llashdan oldin manbani tekshiring.</i>")


def yubor(matn, havola):
    manzil = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    tugma = {"inline_keyboard": [
        [{"text": "📖 Asl postni o'qish", "url": havola}],
        [{"text": "⚖️ Lex.uz", "url": "https://lex.uz"},
         {"text": "🧾 Soliq.uz", "url": "https://soliq.uz"}]]}
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID, "text": matn, "parse_mode": "HTML",
        "reply_markup": json.dumps(tugma)}).encode()
    urllib.request.urlopen(manzil, data=data, timeout=30)
    time.sleep(3)


def postlarni_ol(kanal):
    sorov = urllib.request.Request(
        "https://t.me/s/" + kanal, headers={"User-Agent": "Mozilla/5.0"})
    sahifa = urllib.request.urlopen(sorov, timeout=30).read().decode("utf-8")
    p = Postlar()
    p.feed(sahifa)
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
        yangi = postlar[-3:]   # birinchi marta oxirgi 3 tasi
    soni = 0
    for havola, matn in yangi:
        xulosa = qisqartir(matn)
        if xulosa and not xulosa.upper().startswith("SKIP"):
            yubor(bezat(xulosa, kanal), havola)
            soni += 1
        holat[kanal] = raqam(havola)
        with open(HOLAT, "w") as f:
            json.dump(holat, f)
    print(kanal, "- yangi:", len(yangi), "yuborildi:", soni)
