# Robot Offres (gratuit) : agrège un flux autorisé (RemoteOK) avec lien retour.
# On n'héberge PAS le texte des annonces : on garde les faits + le lien source.
import json, os, hashlib, datetime, urllib.request

def ref(s):
    return "jf-" + hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]

live = json.load(open("offres.json", encoding="utf-8")) if os.path.exists("offres.json") else []
seen = {o.get("ref_unique") or o.get("id") for o in live}

data = []
try:
    req = urllib.request.Request(
        "https://remoteok.com/api",
        headers={"User-Agent": "FlashJob/1.0 (+https://flashjob.ma)"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
except Exception as e:
    print("Flux indisponible :", e)

today = datetime.date.today().isoformat()
jobs = [j for j in data if isinstance(j, dict) and j.get("position")]
added = []
for j in jobs[:20]:
    titre = (j.get("position") or "").strip()
    comp = (j.get("company") or "").strip()
    if not titre or not comp:
        continue
    r = ref(titre + comp)
    if r in seen:
        continue
    tags = [t for t in (j.get("tags") or []) if t][:5]
    offre = {
        "id": r, "titre": titre, "entreprise": comp,
        "ville": "Télétravail", "pays": "International",
        "type_contrat": "Freelance",
        "secteur": (tags[0].title() if tags else "Tech"),
        "remote": True,
        "competences": tags or ["Voir l'offre sur la source"],
        "resume_neutre": "%s chez %s, poste en télétravail. Détails et candidature sur le site source." % (titre, comp),
        "url_source": j.get("url") or j.get("apply_url") or "https://remoteok.com",
        "source_nom": "RemoteOK", "date_pub": today, "ref_unique": r,
    }
    added.append(offre)
    seen.add(r)

if added:
    live = added + live
    live = live[:300]
    json.dump(live, open("offres.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
print("Offres ajoutées :", len(added))
