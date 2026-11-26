import urllib.request
from html.parser import HTMLParser

KANALLAR = ["soliqnews", "Nurullo_Bobomuradov", "Afzalraximov"]


class Postlar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.postlar = []      # [havola, matn]
        self.havola = ""
        self.chuqurlik = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("data-post"):
            self.havola = "https://t.me/" + a["data-post"]
        if self.chuqurlik:
            if tag == "div":
                self.chuqurlik += 1
            elif tag == "br":
                self.postlar[-1][1] += "\n"
        elif tag == "div" and "js-message_text" in (a.get("class") or "").split():
            self.chuqurlik = 1
            self.postlar.append([self.havola, ""])

    def handle_endtag(self, tag):
        if tag == "div" and self.chuqurlik:
            self.chuqurlik -= 1

    def handle_data(self, data):
        if self.chuqurlik:
            self.postlar[-1][1] += data


def main():
    for kanal in KANALLAR:
        print("=====", kanal, "=====")
        try:
            sorov = urllib.request.Request(
                "https://t.me/s/" + kanal, headers={"User-Agent": "Mozilla/5.0"})
            html = urllib.request.urlopen(sorov, timeout=30).read().decode("utf-8")
        except Exception as xato:
            print("Xato:", xato)
            continue
        p = Postlar()
        p.feed(html)
        print("Topilgan postlar:", len(p.postlar))
        for havola, matn in p.postlar[-3:]:
            print(havola)
            print(matn[:200])
            print("---")


if __name__ == "__main__":
    main()
