# Robot Offres Maroc (Jooble) — VERSION DIAGNOSTIC
import json, os, hashlib, datetime, urllib.request, urllib.error

KEY = os.environ.get("JOOBLE_KEY", "").strip().strip('"').strip("'")
print("Longueur de la cle lue :", len(KEY), "caracteres")
if not KEY:
    print("Cle Jooble absente (secret JOOBLE_KEY).")
    raise SystemExit(0)

def ref(s):
    return "ma-" + hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]

live = json.load(open("offres.json", encoding="utf-8")) if os.path.exists("offres.json") else []
seen = {o.get("ref_unique") or o.get("id") for o in live}

REQUETES = [
    {"keywords": "emploi", "location": "Maroc"},
    {"keywords": "comptable", "location": "Casablanca"},
    {"keywords": "commercial", "location": "Rabat"},
    {"keywords": "informatique", "location": "Maroc"},
]

def chercher(body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "https://jooble.org/api/" + KEY, data=data,
        headers={"Content-Type": "application/json",
                 "User-Agent": "FlashJob/1.0 (+https://flashjob.ma)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.getcode(), json.load(r)

today = datetime.date.today().isoformat()
added = []
for body in REQUETES:
    label = "[%s | %s]" % (body["keywords"], body["location"])
    try:
        code, res = chercher(body)
        jobs = res.get("jobs") or []
        total = res.get("totalCount")
        print("%s HTTP %s, totalCount=%s, jobs recus=%d" % (label, code, total, len(jobs)))
    except urllib.error.HTTPError as e:
        body_txt = ""
        try: body_txt = e.read().decode("utf-8")[:200]
        except Exception: pass
        print("%s ERREUR HTTP %s : %s" % (label, e.code, body_txt))
        continue
    except Exception as e:
        print("%s ERREUR : %s" % (label, e))
        continue
    for j in jobs[:12]:
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
        resume = ("%s chez %s, a %s." % (titre, comp, ville)) if comp else ("%s a %s." % (titre, ville))
        added.append({
            "id": r, "titre": titre, "entreprise": ent,
            "ville": ville, "pays": "Maroc", "type_contrat": type_c,
            "secteur": "Divers", "remote": False,
            "competences": ["Voir le detail sur la source"],
            "resume_neutre": resume + " Details et candidature sur le site source.",
            "url_source": lien, "source_nom": "Jooble",
            "date_pub": today, "ref_unique": r,
        })
        seen.add(r)

if added:
    live = added + live
    live = live[:300]
    json.dump(live, open("offres.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
print("Offres Maroc ajoutees :", len(added))
