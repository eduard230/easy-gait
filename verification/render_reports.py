# -*- coding: utf-8 -*-
"""
Transforma rezultatul workflow-ului de verificare in rapoarte .md lizibile.
Genereaza:
  - reports/00_SUMAR_EXECUTIV.md         (privire de ansamblu + scoruri + top probleme)
  - reports/01_DOSAR_PROIECT.md          (ground-truth extras din cod/rezultate)
  - reports/CAPITOL_III.md / IV.md / V.md (sinteza + detalii per afirmatie + lacune + corecturi)
"""
import json
import os
import re

OUTPUT = r"C:/Users/Eduard/AppData/Local/Temp/claude/D--OneDrive---Realworld-Holding-b-v-Documents-67/dd53a181-5b96-43b8-8d22-597f9af57634/tasks/wto453rkk.output"
REPORTS = r"D:/OneDrive - Realworld Holding b.v/Documents/67/verification/reports"
os.makedirs(REPORTS, exist_ok=True)

data = json.loads(open(OUTPUT, encoding="utf-8").read())["result"]
dosare = data["dosare"]
reports = data["workunit_reports"]
syntheses = data["syntheses"]
stats = data["stats"]

VERDICT_ICON = {
    "CONFIRMAT": "✅", "PARTIAL": "🟡", "CONTRAZIS": "❌", "NEVERIFICABIL": "⚪",
}
SEV_ICON = {"critic": "🔴", "mediu": "🟠", "minor": "🟢", "n/a": ""}


def chapter_of(wu_id):
    m = re.match(r"WU-([A-Z]+)", wu_id or "")
    return m.group(1) if m else "misc"


def norm_cap(c):
    c = (c or "").upper()
    for k in ["III", "IV", "V"]:
        if re.search(rf"\b{k}\b", c) or c == k:
            return k
    return c


# index sinteze pe capitol normalizat (III/IV/V) — folosit peste tot
synth_norm = {norm_cap(s.get("capitol", "")): s for s in syntheses}
CAP_SHORT = {"III": "Cap. III", "IV": "Cap. IV", "V": "Cap. V"}


# ─────────────────────────────────────────────────────────────────────────────
# 00 — SUMAR EXECUTIV
# ─────────────────────────────────────────────────────────────────────────────
lines = ["# SUMAR EXECUTIV — Verificare Raport CS4 (capitolele III–V)\n"]
lines.append("> Verificare automată multi-agent (Opus 4.8) a afirmațiilor din "
             "`Paun_Raluca_Raport_CS4-final.docx` contra **codului real** și **rezultatelor** "
             "proiectului `easy-gait`. Agenții au descoperit singuri proiectul (cod + CSV), "
             "fără a folosi PDF-urile de explicații.\n")
lines.append("## Cifre globale\n")
lines.append(f"- **Afirmații verificate:** {stats['afirmatii_verificate']}")
lines.append(f"- ✅ Confirmate / 🟡 Parțiale / ❌ Contrazise: vezi mai jos pe capitole")
lines.append(f"- **❌ CONTRAZISE:** {stats['contrazis']}")
lines.append(f"- **🟡 PARȚIALE / imprecise:** {stats['partial']}")
lines.append(f"- **Lacune identificate (ce ar trebui adăugat):** {stats['lacune']}\n")

# numaratoare per verdict
counts = {}
for r in reports:
    for v in r.get("verdicte", []):
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
lines.append("| Verdict | Număr |")
lines.append("| --- | --- |")
for k in ["CONFIRMAT", "PARTIAL", "CONTRAZIS", "NEVERIFICABIL"]:
    lines.append(f"| {VERDICT_ICON[k]} {k} | {counts.get(k, 0)} |")
lines.append("")

# Scoruri per capitol din sinteze
lines.append("## Scor de acuratețe per capitol\n")
lines.append("| Capitol | Scor /100 | Rezumat |")
lines.append("| --- | --- | --- |")
for cap in ["III", "IV", "V"]:
    s = synth_norm.get(cap)
    if not s:
        continue
    rez = (s.get("rezumat_executiv", "") or "").replace("\n", " ")
    lines.append(f"| **{CAP_SHORT[cap]}** | {s.get('scor_acuratete','?')} | {rez[:160]}… |")
lines.append("")

# Top probleme agregate (critice + medii)
lines.append("## ⚠️ Top probleme confirmate (toate capitolele)\n")
allprob = []
for s in syntheses:
    capshort = CAP_SHORT.get(norm_cap(s.get("capitol", "")), s.get("capitol", "?"))
    for p in s.get("top_probleme", []):
        allprob.append((capshort, p))
order = {"critic": 0, "mediu": 1, "minor": 2}
allprob.sort(key=lambda x: order.get(x[1].get("severitate", "minor"), 3))
for cap, p in allprob:
    sev = p.get("severitate", "")
    lines.append(f"- {SEV_ICON.get(sev,'')} **[{sev.upper()}] ({cap})** {p.get('descriere','')}")
    if p.get("fix"):
        lines.append(f"  - 🔧 *Fix:* {p['fix']}")
lines.append("")

lines.append("## Fișiere generate\n")
lines.append("- `01_DOSAR_PROIECT.md` — adevărul de bază extras din cod/rezultate (referință)")
lines.append("- `CAPITOL_III.md`, `CAPITOL_IV.md`, `CAPITOL_V.md` — verificare detaliată + lacune + corecturi de redactare\n")

open(os.path.join(REPORTS, "00_SUMAR_EXECUTIV.md"), "w", encoding="utf-8").write("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# 01 — DOSAR PROIECT
# ─────────────────────────────────────────────────────────────────────────────
lines = ["# DOSAR DE PROIECT — adevărul de bază (ground-truth)\n"]
lines.append("> Fapte atomice extrase **direct din cod și din rezultatele reale** de doi agenți "
             "Opus 4.8 care au explorat proiectul. Acesta este reperul contra căruia au fost "
             "verificate afirmațiile din raport.\n")
for i, d in enumerate(dosare):
    lines.append(f"## Domeniu {i+1}\n")
    lines.append(d.get("rezumat", "") + "\n")
    if d.get("fisiere_cheie"):
        lines.append("**Fișiere cheie:**")
        for fc in d["fisiere_cheie"]:
            lines.append(f"- {fc}")
        lines.append("")
    lines.append("**Fapte verificate:**\n")
    for f in d.get("fapte", []):
        lines.append(f"- {f.get('fapt','')}  \n  `{f.get('sursa','')}`")
    if d.get("discrepante_interne"):
        lines.append("\n**Discrepanțe interne observate (cod vs. docstring / între module):**")
        for x in d["discrepante_interne"]:
            lines.append(f"- ⚠️ {x}")
    lines.append("")
open(os.path.join(REPORTS, "01_DOSAR_PROIECT.md"), "w", encoding="utf-8").write("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# CAPITOL_*.md — sinteza + detalii per work-unit
# ─────────────────────────────────────────────────────────────────────────────
reports_by_cap = {}
for r in reports:
    reports_by_cap.setdefault(chapter_of(r.get("work_unit", "")), []).append(r)

CAP_TITLES = {
    "III": "CAPITOLUL III — Prezentarea conceptului propriu",
    "IV": "CAPITOLUL IV — Platformă, date, algoritmi, FSM, dashboard",
    "V": "CAPITOLUL V — Validare și rezultate",
}

for cap in ["III", "IV", "V"]:
    revs = reports_by_cap.get(cap, [])
    s = synth_norm.get(cap)
    L = [f"# {CAP_TITLES[cap]}\n"]
    L.append("> Verificare detaliată (Opus 4.8) a fiecărei afirmații contra codului și "
             "rezultatelor reale. Legendă verdicte: ✅ CONFIRMAT · 🟡 PARȚIAL/imprecis · "
             "❌ CONTRAZIS · ⚪ NEVERIFICABIL.\n")

    # --- Sinteza capitolului ---
    if s:
        L.append("## 📋 Sinteză capitol\n")
        L.append(f"**Scor de acuratețe: {s.get('scor_acuratete','?')}/100**\n")
        L.append(s.get("rezumat_executiv", "") + "\n")
        if s.get("top_probleme"):
            L.append("### Top probleme confirmate\n")
            for p in s["top_probleme"]:
                sev = p.get("severitate", "")
                L.append(f"- {SEV_ICON.get(sev,'')} **[{sev.upper()}]** {p.get('descriere','')}")
                if p.get("fix"):
                    L.append(f"  - 🔧 *Fix:* {p['fix']}")
            L.append("")
        if s.get("recomandari_de_scris"):
            L.append("### ✍️ Recomandări de scris (ce să adaugi)\n")
            for rec in s["recomandari_de_scris"]:
                L.append(f"- {rec}")
            L.append("")

    # --- Detalii per work-unit ---
    L.append("---\n\n## 🔍 Verificare detaliată pe sub-secțiuni\n")
    for r in revs:
        L.append(f"### {r.get('work_unit','?')}\n")
        if r.get("concluzie_sectiune"):
            L.append(f"*{r['concluzie_sectiune']}*\n")

        # Verdicte
        vs = r.get("verdicte", [])
        if vs:
            L.append("#### Verdicte pe afirmații\n")
            for v in vs:
                icon = VERDICT_ICON.get(v.get("verdict", ""), "")
                sev = v.get("severitate", "")
                sevtag = f" {SEV_ICON.get(sev,'')}" if sev and sev != "n/a" else ""
                flags = ""
                if v.get("dublu_confirmat"):
                    flags += " 🔁²"
                if v.get("refutat"):
                    flags += " ↩️revizuit"
                L.append(f"**{icon} {v.get('af_id','')} — {v.get('verdict','')}{sevtag}**{flags}  ")
                L.append(f"{v.get('afirmatie_rezumat','')}  ")
                if v.get("dovada"):
                    L.append(f"📎 *Dovadă:* `{v['dovada']}`  ")
                if v.get("explicatie"):
                    L.append(f"💬 {v['explicatie']}")
                L.append("")

        # Figuri/tabele
        ft = r.get("figuri_tabele", [])
        if ft:
            L.append("#### Figuri / tabele\n")
            L.append("| Referință | Există | Sursă | Observații |")
            L.append("| --- | --- | --- | --- |")
            for x in ft:
                L.append(f"| {x.get('ref','')} | {x.get('exista','')} | "
                         f"`{x.get('sursa_fisier','') or '—'}` | {x.get('observatii','').replace(chr(10),' ')} |")
            L.append("")

        # Corecturi de redactare
        cr = r.get("corecturi_redactare", [])
        if cr:
            L.append("#### ✏️ Corecturi de redactare propuse\n")
            for x in cr:
                L.append(f"**{x.get('af_id','')}**  ")
                L.append(f"- ❌ Original: *{x.get('text_original_problema','')}*")
                L.append(f"- ✅ Corectat: **{x.get('text_corectat','')}**")
                L.append("")

        # Lacune
        lac = r.get("lacune", [])
        if lac:
            L.append("#### 📌 Lacune — ce ar trebui adăugat\n")
            for x in lac:
                imp = x.get("importanta", "")
                L.append(f"- **[{imp}]** {x.get('lacuna','')}")
                if x.get("dovada_proiect"):
                    L.append(f"  - 📎 `{x['dovada_proiect']}`")
                if x.get("propunere_text"):
                    L.append(f"  - ✍️ *Text propus:* {x['propunere_text']}")
            L.append("")
        L.append("---\n")

    open(os.path.join(REPORTS, f"CAPITOL_{cap}.md"), "w", encoding="utf-8").write("\n".join(L))

# raport sumar in consola
print("Rapoarte generate in verification/reports/:")
for fn in sorted(os.listdir(REPORTS)):
    p = os.path.join(REPORTS, fn)
    print(f"  {fn}  ({os.path.getsize(p)} bytes)")
print()
print("STATISTICI:")
print(f"  Afirmatii verificate: {stats['afirmatii_verificate']}")
for k in ["CONFIRMAT", "PARTIAL", "CONTRAZIS", "NEVERIFICABIL"]:
    print(f"    {k}: {counts.get(k,0)}")
print(f"  Lacune: {stats['lacune']}")
print()
print("SCORURI CAPITOLE:")
for cap in ["III", "IV", "V"]:
    s = synth_norm.get(cap)
    if s:
        print(f"  Cap. {cap}: {s.get('scor_acuratete','?')}/100")
