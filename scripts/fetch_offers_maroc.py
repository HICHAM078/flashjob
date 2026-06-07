# Robot Offres Maroc (Jooble) — essaie plusieurs serveurs Jooble + diagnostic
import json, os, hashlib, datetime, urllib.request, urllib.error

KEY = os.environ.get("JOOBLE_KEY", "").strip().strip('"').strip("'")
print("Longueur de la cle lue :", len(KEY), "caracteres")
if not KEY:
    print("Cle Jooble absente (secret JOOBLE_KEY).")
    raise SystemExit(0)

HOSTS = ["https://ma.jooble.org/api/", "https://fr.jooble.org/api/", "https://jooble.org/api/"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def call(host, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(host + KEY, data=data,
        headers={"Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.getcode(), json.load(r)

def ref(s):
    return "ma-" + hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]

# 1) Trouver le serveur Jooble qui accepte la cle
probe = {"keywords": "emploi", "location": "Maroc"}
WORK = None
for h in HOSTS:
    try:
        code, res = call(h, probe)
        print("Serveur %s -> HTTP %s, totalCount=%s" % (h, code, res.get("totalCount")))
        WORK = h
        break
    except urllib.error.HTTPError as e:
        print("Serveur %s -> ERREUR HTTP %s" % (h, e.code))
    except Exception as e:
        print("Serveur %s -> ERREUR %s" % (h, e))
if not WORK:
    print("Aucun serveur Jooble n'accepte la cle. Verifie la cle / le pays d'inscription.")
    raise SystemExit(0)
print("==> Serveur retenu :", WORK)

# 2) Recuperer les offres sur le bon serveur
live = json.load(open("offres.json", encoding="utf-8")) if os.path.exists("offres.json") else []
seen = {o.get("ref_unique") or o.get("id") for o in live}
REQUETES = [
    {"keywords": "emploi", "location": "Maroc"},
    {"keywords": "comptable", "location": "Casablanca"},
    {"keywords": "commercial", "location": "Rabat"},
    {"keywords": "informatique", "location": "Maroc"},
]
today = datetime.date.today().isoformat()
added = []
for body in REQUETES:
    try:
        code, res = call(WORK, body)
        jobs = res.get("jobs") or []
        print("[%s | %s] totalCount=%s, jobs=%d" % (body["keywords"], body["location"], res.get("totalCount"), len(jobs)))
    except Exception as e:
        print("[%s] ERREUR : %s" % (body["keywords"], e)); continue
    for j in jobs[:12]:
        titre = (j.get("title") or "").strip()
        lien = (j.get("link") or "").strip()
        if not titre or not lien: continue
        r = ref(titre + lien)
        if r in seen: continue
        ville = (j.get("location") or "Maroc").strip() or "Maroc"
        comp = (j.get("company") or "").strip()
        ent = comp if comp else "Voir l'offre sur la source"
        resume = ("%s chez %s, a %s." % (titre, comp, ville)) if comp else ("%s a %s." % (titre, ville))
        added.append({
            "id": r, "titre": titre, "entreprise": ent, "ville": ville, "pays": "Maroc",
            "type_contrat": (j.get("type") or "").strip() or "Non precise", "secteur": "Divers",
            "remote": False, "competences": ["Voir le detail sur la source"],
            "resume_neutre": resume + " Details et candidature sur le site source.",
            "url_source": lien, "source_nom": "Jooble", "date_pub": today, "ref_unique": r,
        })
        seen.add(r)

if added:
    live = (added + live)[:300]
    json.dump(live, open("offres.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("Offres Maroc ajoutees :", len(added))
