# Robot Offres Maroc (gratuit) : utilise l'API autorisee de Jooble.
# Jooble autorise la reprise de ses resultats sur un site tiers, avec lien retour.
# On garde les faits + le lien vers l'offre (on n'heberge pas le texte source).
# Regle en douceur : 1 execution/jour x 4 recherches = 4 requetes/jour (limite 500).
import json, os, hashlib, datetime, urllib.request

KEY = os.environ.get("JOOBLE_KEY", "").strip()
if not KEY:
    print("Cle Jooble absente (secret JOOBLE_KEY) : rien a faire pour l'instant.")
    raise SystemExit(0)

def ref(s):
    return "ma-" + hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]

live = json.load(open("offres.json", encoding="utf-8")) if os.path.exists("offres.json") else []
seen = {o.get("ref_unique") or o.get("id") for o in live}

# 4 recherches pour couvrir large au Maroc sans epuiser la limite
REQUETES = [
    {"keywords": "", "location": "Maroc"},
    {"keywords": "comptable", "location": "Maroc"},
    {"keywords": "commercial", "location": "Maroc"},
    {"keywords": "stage", "location": "Maroc"},
]

def chercher(body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "https://jooble.org/api/" + KEY, data=data,
        headers={"Content-Type": "application/json",
                 "User-Agent": "FlashJob/1.0 (+https://flashjob.ma)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

today = datetime.date.today().isoformat()
added = []
for body in REQUETES:
    try:
        res = chercher(body)
    except Exception as e:
        print("Requete echouee", body, ":", e)
        continue
    for j in (res.get("jobs") or [])[:12]:
        titre = (j.get("title") or "").strip()
        lien = (j.get("link") or "").strip()
        if not titre or not lien:
            continue
        r = ref(titre + lien)
        if r in seen:
            continue
        ville = (j.get("location") or "Maroc").strip() or "Maroc"
        comp = (j.get("company") or "").strip()
        type_c = (j.get("type") or "").strip() or "Non precise"
        ent = comp if comp else "Voir l'offre sur la source"
        if comp:
            resume = "%s chez %s, a %s." % (titre, comp, ville)
        else:
            resume = "%s a %s." % (titre, ville)
        offre = {
            "id": r, "titre": titre, "entreprise": ent,
            "ville": ville, "pays": "Maroc",
            "type_contrat": type_c, "secteur": "Divers",
            "remote": False,
            "competences": ["Voir le detail sur la source"],
            "resume_neutre": resume + " Details et candidature sur le site source.",
            "url_source": lien, "source_nom": "Jooble",
            "date_pub": today, "ref_unique": r,
        }
        added.append(offre)
        seen.add(r)

if added:
    live = added + live
    live = live[:300]
    json.dump(live, open("offres.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
print("Offres Maroc ajoutees :", len(added))
