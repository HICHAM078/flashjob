# Robot News (gratuit) : publie un article du stock vers news.json
import json, os, time, datetime

def load(p, default):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default

live = load("news.json", [])
stock = load("news-stock.json", [])
titres = {(a.get("titre") or "").strip().lower() for a in live}
mois = ["janvier","février","mars","avril","mai","juin","juillet",
        "août","septembre","octobre","novembre","décembre"]

published = False
for art in stock:
    if (art.get("titre") or "").strip().lower() in titres:
        continue
    d = datetime.date.today()
    art = dict(art)
    art["id"] = "news-" + str(int(time.time()))
    art["date"] = "%d %s %d" % (d.day, mois[d.month - 1], d.year)
    live = [art] + live
    live = live[:100]
    json.dump(live, open("news.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("Publié :", art["titre"])
    published = True
    break

if not published:
    print("Stock épuisé — rien à publier.")
