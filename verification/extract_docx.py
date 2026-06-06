# -*- coding: utf-8 -*-
"""
Extrage structura documentului Word in fisiere .md, capitol cu capitol.
- Parcurge body-ul in ordinea reala (paragrafe + tabele intercalate).
- Detecteaza heading-urile (dupa stil sau dupa numerotare 1 / 1.1 / 1.1.1).
- Numeroteaza fiecare afirmatie (paragraf de continut) pentru verificare.
- Capteaza tabelele si referintele la figuri (legende "Figura X").
- Salveaza un fisier per capitol top-level + un index global.
"""
import os
import re
import json
from docx import Document
from docx.document import Document as _Doc
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

DOCX = r"D:/OneDrive - Realworld Holding b.v/Documents/67/Word/Paun_Raluca_Raport_CS4-final.docx"
OUT = r"D:/OneDrive - Realworld Holding b.v/Documents/67/verification/extracted"

os.makedirs(OUT, exist_ok=True)


def iter_block_items(parent):
    """Genereaza Paragraph si Table in ordinea reala din document."""
    if isinstance(parent, _Doc):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("parent necunoscut")
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}


def heading_info(para):
    """
    Returneaza (top_level_num, display_level, is_top) pentru un heading,
    sau None daca nu este heading.
    top_level_num = numarul capitolului (1..5, sau 'BIB', 'FRONT').
    display_level = nivelul de afisare markdown (1 = ##, 2 = ###, ...).
    is_top = True daca este capitol top-level (CAPITOLUL X sau BIBLIOGRAFIE).
    """
    txt = para.text.strip()
    if not txt:
        return None
    name = (para.style.name or "").lower()

    # 1) Capitol top-level: "CAPITOLUL I ..." (in orice stil)
    m = re.match(r"^CAPITOLUL\s+([IVX]+)\b", txt)
    if m:
        num = ROMAN.get(m.group(1).upper())
        if num:
            return (str(num), 1, True)

    # 2) Bibliografie top-level
    if re.match(r"^BIBLIOGRAFIE\b", txt, re.I):
        return ("BIB", 1, True)

    # 3) Subsectiune numerotata "N.N ..." sau "N.N.N ..."
    m2 = re.match(r"^(\d+)\.(\d+)(\.\d+)?\.?\s+\S", txt)
    if m2 and len(txt) < 150:
        depth = txt[: txt.index(" ")].rstrip(".").count(".") + 1
        return (m2.group(1), depth, False)

    # 4) Heading prin stil (Heading 2/3/4) – subsectiune sub capitolul curent
    mh = re.match(r"heading\s*(\d+)", name)
    if mh and len(txt) < 150:
        lvl = int(mh.group(1))
        return (None, lvl, False)

    return None


def table_to_md(table):
    rows = []
    for row in table.rows:
        cells = [c.text.strip().replace("\n", " ") for c in row.cells]
        rows.append(cells)
    if not rows:
        return ""
    out = []
    header = rows[0]
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join(["---"] * len(header)) + " |")
    for r in rows[1:]:
        # normalizeaza la lungimea header
        while len(r) < len(header):
            r.append("")
        out.append("| " + " | ".join(r[: len(header)]) + " |")
    return "\n".join(out)


def has_image(para):
    """Detecteaza daca paragraful contine o imagine inline."""
    blips = para._p.findall(
        ".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
    )
    return len(blips) > 0


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE).strip().lower()
    s = re.sub(r"[\s_-]+", "_", s)
    return s[:60] or "sectiune"


doc = Document(DOCX)

# Prima trecere: construieste o lista liniara de blocuri (heading/para/image/table)
blocks = []
for item in iter_block_items(doc):
    if isinstance(item, Paragraph):
        hi = heading_info(item)
        txt = item.text.strip()
        if hi is not None:
            blocks.append(("heading", hi, txt))
        elif has_image(item):
            blocks.append(("image", None, txt))
        elif txt:
            blocks.append(("para", None, txt))
    elif isinstance(item, Table):
        blocks.append(("table", None, table_to_md(item)))

# A doua trecere: grupeaza pe capitole top-level
TOP_TITLES = {
    "1": "CAPITOLUL I", "2": "CAPITOLUL II", "3": "CAPITOLUL III",
    "4": "CAPITOLUL IV", "5": "CAPITOLUL V", "BIB": "BIBLIOGRAFIE",
}
chapters = []
current = {"num": "0", "title": "Front matter / Pre-capitol (titlu, rezumat, cuprins)", "blocks": []}

for kind, meta, payload in blocks:
    if kind == "heading":
        top_num, disp_lvl, is_top = meta
        if is_top:
            if current["blocks"] or current["num"] != "0":
                chapters.append(current)
            current = {"num": top_num, "title": payload, "blocks": []}
            continue
        # subsectiune: daca top_num e cunoscut si difera de capitolul curent,
        # foloseste-l doar ca eticheta de numerotare (nu schimba capitolul).
        current["blocks"].append(("heading", disp_lvl, payload))
    else:
        current["blocks"].append((kind, meta, payload))
chapters.append(current)

# Scrie fisierele per capitol + index
index_lines = ["# INDEX — Extragere document\n"]
index_lines.append(f"Sursa: `{os.path.basename(DOCX)}`\n")
manifest = {"source": os.path.basename(DOCX), "chapters": []}

stmt_global = 0
fig_global = 0
tab_global = 0

for ch in chapters:
    chnum = ch["num"]
    fname = f"capitol_{chnum}_{slugify(ch['title'])}.md"
    path = os.path.join(OUT, fname)
    lines = [f"# {ch['title']}\n"]
    lines.append(f"> Capitol extras automat din `{os.path.basename(DOCX)}`. "
                 f"Fiecare AFIRMATIE este numerotata pentru verificare independenta.\n")
    stmt_in_ch = 0
    fig_in_ch = 0
    tab_in_ch = 0
    for kind, lvl, payload in ch["blocks"]:
        if kind == "heading":
            prefix = "#" * min(lvl + 1, 6)
            lines.append(f"\n{prefix} {payload}\n")
        elif kind == "para":
            # Detecteaza legende de figura/tabel
            if re.match(r"^(Figura|Fig\.|Figure)\s*\d", payload, re.I):
                fig_global += 1
                fig_in_ch += 1
                lines.append(f"\n**[FIGURA {fig_global}] (legenda):** {payload}\n")
            elif re.match(r"^(Tabel|Tabelul|Table)\s*\d", payload, re.I):
                tab_global += 1
                tab_in_ch += 1
                lines.append(f"\n**[LEGENDA TABEL {tab_global}]:** {payload}\n")
            else:
                stmt_global += 1
                stmt_in_ch += 1
                lines.append(f"- **[AF-{chnum}.{stmt_in_ch} | #{stmt_global}]** {payload}")
        elif kind == "image":
            fig_global += 1
            fig_in_ch += 1
            cap = payload if payload else "(fara legenda in paragraful imaginii)"
            lines.append(f"\n**[FIGURA {fig_global} — imagine inline]** {cap}\n")
        elif kind == "table":
            tab_global += 1
            tab_in_ch += 1
            lines.append(f"\n**[TABEL {tab_global}]**\n")
            lines.append(payload + "\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    index_lines.append(
        f"- **Capitol {chnum}** — {ch['title']}  →  `{fname}`  "
        f"(afirmatii: {stmt_in_ch}, figuri: {fig_in_ch}, tabele: {tab_in_ch})"
    )
    manifest["chapters"].append({
        "num": chnum, "title": ch["title"], "file": fname,
        "statements": stmt_in_ch, "figures": fig_in_ch, "tables": tab_in_ch,
    })

index_lines.append(
    f"\n**TOTAL:** afirmatii={stmt_global}, figuri={fig_global}, tabele={tab_global}"
)
with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(index_lines))
with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("Extragere completa.")
print(f"Capitole: {len(chapters)}")
print(f"Total afirmatii: {stmt_global}, figuri: {fig_global}, tabele: {tab_global}")
for c in manifest["chapters"]:
    print(f"  [{c['num']}] {c['title'][:70]} -> af={c['statements']} fig={c['figures']} tab={c['tables']}")
