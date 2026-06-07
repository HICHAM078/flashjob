# Robot News (gratuit) : publie un article de chaque stock (FR + AR) vers news.json
import json, os, time, datetime

def load(p, default):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default

mois = ["janvier","février","mars","avril","mai","juin","juillet",
        "août","septembre","octobre","novembre","décembre"]

def date_fr():
    d = datetime.date.today()
    return "%d %s %d" % (d.day, mois[d.month - 1], d.year)

live = load("news.json", [])
titres = {(a.get("titre") or "").strip().lower() for a in live}

def publier_un(stock_path, lang_defaut):
    global live
    stock = load(stock_path, [])
    for art in stock:
        t = (art.get("titre") or "").strip().lower()
        if not t or t in titres:
            continue
        art = dict(art)
        if "lang" not in art:
            art["lang"] = lang_defaut
        art["id"] = "news-%d-%s" % (int(time.time()), art["lang"])
        art["date"] = date_fr()
        live = [art] + live
        titres.add(t)
        print("Publié [%s] : %s" % (art["lang"], art["titre"]))
        return True
    return False

a = publier_un("news-stock.json", "fr")
b = publier_un("news-stock-ar.json", "ar")

if a or b:
    live = live[:100]
    json.dump(live, open("news.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
else:
    print("Stock épuisé — rien à publier.")
