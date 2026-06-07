# Lit la fiche d'offre (issue GitHub), genere la description et l'ajoute a offres.json
import json, os, hashlib, datetime, re

body = os.environ.get("ISSUE_BODY", "") or ""

# Parser les sections "### Label" -> valeur
sections, current, buf = {}, None, []
for line in body.splitlines():
    m = re.match(r'^###\s+(.*)', line.strip())
    if m:
        if current is not None:
            sections[current] = "\n".join(buf).strip()
        current, buf = m.group(1).strip(), []
    else:
        buf.append(line)
if current is not None:
    sections[current] = "\n".join(buf).strip()

def get(label):
    v = (sections.get(label, "") or "").strip()
    return "" if v in ("", "_No response_", "_Aucune réponse_", "None") else v

P = get("Intitulé du poste")
O = get("Organisme / Entreprise")
V = get("Ville")
C = get("Type de contrat")
if C == "Non précisé":
    C = ""
S = get("Secteur") or "Divers"
N = get("Nombre de postes (optionnel)")
D = get("Date limite (optionnel)")
U = get("Lien officiel pour postuler")
lang = "ar" if "عرب" in get("Langue de l'annonce") else "fr"

if not P or not V or not U:
    print("Champs obligatoires manquants (titre/ville/lien). Abandon.")
    raise SystemExit(0)

if lang == "ar":
    resume = ((O + " يعلن عن توظيف") if O else "توظيف") + " في منصب " + P + " بمدينة " + V \
        + (("، " + C) if C else "") + "." \
        + ((" عدد المناصب: " + N + ".") if N else "") \
        + ((" آخر أجل للترشيح: " + D + ".") if D else "") \
        + " التفاصيل والترشيح عبر الموقع الرسمي."
else:
    resume = ((O + " recrute") if O else "Recrutement") + " pour un poste de " + P + " à " + V \
        + ((", en " + C) if C else "") + "." \
        + ((" " + N + " poste(s) à pourvoir.") if N else "") \
        + ((" Date limite de candidature : " + D + ".") if D else "") \
        + " Les détails et la candidature se font sur le site officiel."

ref = "man-" + hashlib.sha1((P + U).encode("utf-8")).hexdigest()[:10]
today = datetime.date.today().isoformat()
offre = {
    "id": ref, "titre": P, "entreprise": (O or "Voir l'offre sur la source"),
    "ville": V, "pays": "Maroc", "type_contrat": (C or "Non précisé"),
    "secteur": S, "remote": False, "lang": lang,
    "competences": ["Voir le détail sur la source"],
    "resume_neutre": resume, "url_source": U, "source_nom": "Site officiel",
    "date_pub": today, "ref_unique": ref,
}

live = json.load(open("offres.json", encoding="utf-8")) if os.path.exists("offres.json") else []
seen = {o.get("ref_unique") or o.get("id") for o in live}
if ref in seen:
    print("Offre déjà présente, rien à faire.")
    raise SystemExit(0)
live = ([offre] + live)[:300]
json.dump(live, open("offres.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("Offre ajoutée :", P)
