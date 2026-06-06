# -*- coding: utf-8 -*-
"""
Imparte capitolele III, IV, V pe sub-sectiuni (work-units) pentru fan-out fin.
Citeste fisierele .md extrase si grupeaza afirmatiile/figurile/tabelele pe
sub-titluri (###/####/#####), producand verification/workunits.json.
"""
import os
import re
import json

EX = r"D:/OneDrive - Realworld Holding b.v/Documents/67/verification/extracted"
OUT = r"D:/OneDrive - Realworld Holding b.v/Documents/67/verification/workunits.json"

TARGET_FILES = {
    "III": "capitol_3_capitolul_iii_prezentarea_conceptului_propriu.md",
    "IV": "capitol_4_capitolul_iv_prezentarea_conceptului_propriu.md",
    "V": "capitol_5_capitolul_v.md",
}

# Grupare sub-sectiunilor in work-units coerente tematic (ca un agent sa aiba
# context suficient si volum rezonabil). Cheia = id WU, valoarea = (capitol, [titluri/pattern-uri]).
# Fiecare WU primeste toate liniile dintre titlul de start si urmatorul titlu de grup.
WORKUNIT_PLAN = [
    # --- Capitolul III (scurt: tot intr-un singur WU) ---
    {"id": "WU-III-01", "chap": "III",
     "title": "Cap. III — Conceptul propriu, scop, obiective, definitia ciclului de mers",
     "start": None, "end": None},  # tot capitolul

    # --- Capitolul IV (impartit pe blocuri tematice; slice pe nr. de linie exact) ---
    {"id": "WU-IV-01a", "chap": "IV",
     "title": "4.1 Platforma software — cele 5 module funcționale (preproc, detecție, parametri, FSM, dashboard)",
     "start_line": 6, "end_line": 30},
    {"id": "WU-IV-01b", "chap": "IV",
     "title": "4.2 Seturile de date utilizate (Samala 2024, Wassall NTNU 2025, GaitRec) + achiziția datelor",
     "start_line": 30, "end_line": 80},
    {"id": "WU-IV-02", "chap": "IV",
     "title": "4.3 Prelucrarea/analiza datelor + figuri exploratorii (4.3.x) + fluxul de date (4.4)",
     "start_line": 80, "end_line": 138},
    {"id": "WU-IV-03", "chap": "IV",
     "title": "4.5 Preprocesare (Butterworth, magnitudine) + 4.6 Trojaniello + 4.7 Maqbool",
     "start_line": 138, "end_line": 164},
    {"id": "WU-IV-04", "chap": "IV",
     "title": "4.8 Unghi gleznă + 4.9 Segmentare + 4.10 Parametri temporali",
     "start_line": 164, "end_line": 190},
    {"id": "WU-IV-05", "chap": "IV",
     "title": "4.11 FSM control gleznă (5 stări, setpoints, PCHIP, timeout)",
     "start_line": 190, "end_line": 235},
    {"id": "WU-IV-06", "chap": "IV",
     "title": "4.12 Vizualizare + Dashboard (animație proteză, 6 pagini Streamlit)",
     "start_line": 235, "end_line": None},

    # --- Capitolul V (validare si rezultate) ---
    {"id": "WU-V-01", "chap": "V",
     "title": "5.1 Pipeline validare + 5.2 Validare evenimente HS/TO (Zeni, MAE, sens, F1)",
     "start": None, "end": "5.3. VALIDAREA TRAIECTORIEI"},
    {"id": "WU-V-02", "chap": "V",
     "title": "5.3 Validare traiectorie unghi gleznă (RMSE, NRMSE, PCC; FSM vs IMU vs OMC)",
     "start": "5.3. VALIDAREA TRAIECTORIEI", "end": "5.4. REZULTATE BIOMECANICE"},
    {"id": "WU-V-03", "chap": "V",
     "title": "5.4 Biomecanică protetic vs intact + 5.5 Mers pe teren (Wassall)",
     "start": "5.4. REZULTATE BIOMECANICE", "end": "5.6. LIMITĂRI"},
    {"id": "WU-V-04", "chap": "V",
     "title": "5.6 Limitări și discuții (dataseturi, algoritmice)",
     "start": "5.6. LIMITĂRI", "end": None},
]


def load_lines(chap):
    path = os.path.join(EX, TARGET_FILES[chap])
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def slice_section(lines, start_pat, end_pat):
    """Extrage liniile intre primul titlu ce contine start_pat si urmatorul ce contine end_pat."""
    def is_heading(ln):
        return ln.lstrip().startswith("#")

    i0 = 0
    if start_pat:
        for i, ln in enumerate(lines):
            if is_heading(ln) and start_pat.lower() in ln.lower():
                i0 = i
                break
    i1 = len(lines)
    if end_pat:
        for i in range(i0 + 1, len(lines)):
            if is_heading(lines[i]) and end_pat.lower() in lines[i].lower():
                i1 = i
                break
    return "\n".join(lines[i0:i1]).strip()


workunits = []
for wu in WORKUNIT_PLAN:
    lines = load_lines(wu["chap"])
    if "start_line" in wu:
        i0 = wu["start_line"] - 1            # 1-based -> 0-based
        i1 = (wu["end_line"] - 1) if wu.get("end_line") else len(lines)
        body = "\n".join(lines[i0:i1]).strip()
    else:
        body = slice_section(lines, wu.get("start"), wu.get("end"))
    # Numara afirmatiile / figurile / tabelele in slice
    n_af = len(re.findall(r"\*\*\[AF-", body))
    n_fig = len(re.findall(r"\[FIGURA \d+", body))
    n_tab = len(re.findall(r"\[TABEL \d+\]", body))
    workunits.append({
        "id": wu["id"],
        "chapter": wu["chap"],
        "title": wu["title"],
        "n_statements": n_af,
        "n_figures": n_fig,
        "n_tables": n_tab,
        "content": body,
    })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(workunits, f, ensure_ascii=False, indent=2)

print(f"Generate {len(workunits)} work-units -> {OUT}\n")
for wu in workunits:
    print(f"  {wu['id']:10s} [{wu['chapter']}] af={wu['n_statements']:3d} "
          f"fig={wu['n_figures']:2d} tab={wu['n_tables']:2d}  | {wu['title'][:55]}")
