# Génère une vraie page HTML par article (Option B) + page hub + sitemap
import json, os, html

ADSENSE = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2554513695879251" crossorigin="anonymous"></script>'
BASE = "https://flashjob.ma"
FAV = ('<link rel="icon" href="/favicon.ico" sizes="any">'
       '<link rel="icon" type="image/png" href="/favicon.png">'
       '<link rel="apple-touch-icon" href="/apple-touch-icon.png">')

CSS = """
:root{--bg:#0b0b0d;--accent:#c8f53d;--ink:#16181d;--soft:#5b6170;--line:#e7e7e2;--paper:#fbfbf9}
*{box-sizing:border-box}
body{margin:0;font-family:'Hanken Grotesk',system-ui,Arial,sans-serif;color:var(--ink);background:var(--paper);line-height:1.7}
a{color:inherit}
.top{background:var(--bg);color:#fff;padding:14px 20px}
.top .in{max-width:820px;margin:0 auto;display:flex;align-items:center;gap:10px}
.logo{display:flex;align-items:center;gap:10px;font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:800;font-size:20px;color:#fff;text-decoration:none}
.logo .b{background:var(--accent);color:#0b0b0d;width:32px;height:32px;border-radius:8px;display:grid;place-items:center;font-size:18px}
.logo em{color:var(--accent);font-style:normal}
.wrap{max-width:820px;margin:0 auto;padding:30px 20px 60px}
.crumb{font-size:13px;color:var(--soft);margin-bottom:14px}
.crumb a{text-decoration:none;color:var(--soft)}
.cat{display:inline-block;background:#eef4d9;color:#41560f;font-size:12px;font-weight:700;padding:5px 11px;border-radius:100px;letter-spacing:.03em}
h1{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:33px;line-height:1.15;margin:14px 0 8px}
.meta{color:var(--soft);font-size:14px;margin-bottom:26px}
article p{margin:0 0 18px;font-size:17px}
article b{color:#0b0b0d}
.adslot{margin:30px auto;min-height:90px;background:repeating-linear-gradient(45deg,#fafafa,#fafafa 10px,#f3f3f0 10px,#f3f3f0 20px);border:1px dashed var(--line);border-radius:12px;display:grid;place-items:center;color:#aaa;font-size:12px;letter-spacing:.05em}
.cta{display:block;background:var(--bg);color:#fff;text-decoration:none;border-radius:16px;padding:22px;margin:34px 0;text-align:center}
.cta b{color:var(--accent)}
.more{margin-top:40px;border-top:1px solid var(--line);padding-top:26px}
.more h3{font-family:'Bricolage Grotesque',system-ui,sans-serif}
.more a{display:block;text-decoration:none;padding:13px 0;border-bottom:1px solid var(--line);color:#0b0b0d}
.more a span{color:var(--soft);font-size:13px;display:block}
.foot{background:var(--bg);color:#9a9aa2;text-align:center;padding:26px 20px;font-size:14px}
.foot a{color:var(--accent);text-decoration:none;margin:0 8px}
[dir=rtl]{text-align:right}
@media(max-width:600px){h1{font-size:26px}}
"""

def page_head(title, desc, canonical, rtl=False):
    return f"""<!DOCTYPE html>
<html lang="{'ar' if rtl else 'fr'}"{' dir="rtl"' if rtl else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{ADSENSE}
<title>{html.escape(title)} | FlashJob</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
{FAV}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@700;800&family=Hanken+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="in"><a class="logo" href="/"><span class="b">⚡</span>Flash<em>Job</em></a></div></header>
"""

FOOT = """<footer class="foot"><div>FlashJob.ma — Votre portail emploi au Maroc<br>
<a href="/">Accueil</a> · <a href="/articles.html">Conseils</a> · <a href="/#/outils">Outils</a> · <a href="/#/mentions">Mentions légales</a></div></footer>
</body></html>"""

data = json.load(open('news.json', encoding='utf-8'))

def slug(a): return a['id']

# Pages articles
for i, a in enumerate(data):
    rtl = (a.get('lang') == 'ar')
    canonical = f"{BASE}/articles/{slug(a)}.html"
    body = a.get('body') or []
    paras = ""
    for j, par in enumerate(body):
        paras += f"<p>{par}</p>\n"
        if j == 1:
            paras += '<div class="adslot">EMPLACEMENT PUBLICITAIRE — AdSense</div>\n'
    # liens internes : 5 autres articles (même langue de préférence)
    others = [x for x in data if x['id'] != a['id'] and (x.get('lang') or 'fr') == (a.get('lang') or 'fr')]
    others = (others + [x for x in data if x['id'] != a['id']])[:5]
    seen=set(); uniq=[]
    for x in others:
        if x['id'] not in seen: seen.add(x['id']); uniq.append(x)
    more = "".join(f'<a href="/articles/{slug(x)}.html">{html.escape(x["titre"])}<span>{html.escape(x.get("cat",""))}</span></a>' for x in uniq[:5])
    cta_txt = "Découvrez les offres d'emploi" if not rtl else "اكتشف عروض الشغل"
    html_out = page_head(a['titre'], a.get('excerpt',''), canonical, rtl)
    html_out += f"""<main class="wrap">
<div class="crumb"><a href="/">Accueil</a> › <a href="/articles.html">Conseils</a> › {html.escape(a.get('cat',''))}</div>
<span class="cat">{html.escape(a.get('cat',''))}</span>
<h1>{html.escape(a['titre'])}</h1>
<div class="meta">{html.escape(a.get('date',''))} · FlashJob</div>
<article>
{paras}
</article>
<a class="cta" href="/"><b>{cta_txt}</b> — flashjob.ma</a>
<div class="more"><h3>À lire aussi</h3>{more}</div>
</main>
{FOOT}"""
    open(f"articles/{slug(a)}.html", "w", encoding="utf-8").write(html_out)

print("Pages articles générées :", len(data))

# Page hub /articles.html
cards = ""
for a in data:
    rtl = (a.get('lang')=='ar')
    cards += f'<a class="card" href="/articles/{slug(a)}.html"{" dir=rtl" if rtl else ""}><span class="cat">{html.escape(a.get("cat",""))}</span><h2>{html.escape(a["titre"])}</h2><p>{html.escape(a.get("excerpt",""))}</p></a>\n'
hub = page_head("Conseils emploi & carrière", "Tous nos guides et conseils pour réussir votre recherche d'emploi au Maroc : CV, entretien, télétravail, salaire, carrière.", f"{BASE}/articles.html")
hub += f"""<main class="wrap">
<div class="crumb"><a href="/">Accueil</a> › Conseils</div>
<h1>Conseils emploi & carrière</h1>
<div class="meta">{len(data)} articles pour réussir votre recherche d'emploi au Maroc</div>
<div class="adslot">EMPLACEMENT PUBLICITAIRE — AdSense</div>
<style>.card{{display:block;background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px;margin-bottom:14px;text-decoration:none}}.card h2{{font-family:'Bricolage Grotesque',sans-serif;font-size:20px;margin:8px 0 6px}}.card p{{color:var(--soft);font-size:15px;margin:0}}</style>
{cards}
</main>
{FOOT}"""
open("articles.html","w",encoding="utf-8").write(hub)
print("Page hub /articles.html générée")

# Sitemap : uniquement de VRAIES URLs (pas de #/)
urls = [f"{BASE}/", f"{BASE}/articles.html"] + [f"{BASE}/articles/{slug(a)}.html" for a in data]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    sm += f"  <url><loc>{u}</loc></url>\n"
sm += "</urlset>\n"
open("sitemap.xml","w",encoding="utf-8").write(sm)
print("sitemap.xml régénéré avec", len(urls), "URLs réelles")
