# -*- coding: utf-8 -*-
"""Generează raportul final de comparație cu literatura din rezultatul workflow-ului."""
import json
import os

OUTPUT = r"C:/Users/Eduard/AppData/Local/Temp/claude/D--OneDrive---Realworld-Holding-b-v-Documents-67/dd53a181-5b96-43b8-8d22-597f9af57634/tasks/wqcc2decm.output"
REPORTS = r"D:/OneDrive - Realworld Holding b.v/Documents/67/verification/reports"

d = json.loads(open(OUTPUT, encoding="utf-8").read())["result"]
comp = d["comparison"]
ref = d["refutation"]
code = d["code_check"]

ICON = {"mai bine": "[OK]", "comparabil": "[OK]", "in interval": "[~]",
        "sub literatura": "[!]", "n/a": "[-]"}

INTRO = """# Comparatie cu literatura - rezultate imbunatatite (v2)

> Verificare multi-agent (Opus 4.8): research literatura cu surse + verificare cod
> + recenzent critic adversarial. Toate cifrele v2 reproduse din
> `events_validation_v2.csv` (29 subiecti) si `fsm_validation_v2.csv` (145 trial-uri protetice).

## AVERTISMENT DE ONESTITATE (de la recenzentul critic)

Recenzentul adversarial a marcat verdictul initial ca PREA OPTIMIST pe doua puncte,
iar eu AM VERIFICAT si a avut dreptate. Le prezint deschis, pentru ca schimba cum
trebuie scrise rezultatele in lucrare:

1. **Sign-flip-ul FSM (PCC -0.22 -> +0.11) e in mare parte ARTEFACT DE TEMPLATE,
   NU dovada fizica.** Am descompus corelatia: termenul de deflexie GRF SINGUR
   (fara echilibrul FSM) coreleaza deja **+0.36** cu OMC. Profilul GRF normativ in
   forma de M e phase-locked ca si OMC, deci adunarea lui ridica mecanic corelatia
   cu ORICE semnal phase-locked. ROM-ul creste la 17.7 grade > OMC 12.5 grade,
   confirmand supra-adaugarea. CONCLUZIE CORECTA: bucla de impedanta arata corect
   DIRECTIA/SEMNUL fizic, dar nu demonstreaza ca reconstruieste unghiul real al
   subiectului. De prezentat ca 'model conceptual al directiei de impedanta', nu ca
   'validare reusita'.

2. **Corectia de bias e FITTING IN-SAMPLE per-trial, NU un offset sistematic global.**
   Biasul e estimat din chiar trial-ul scorat si are SD 50-67 ms (mai mare decat
   MAE-ul debiased de 26-30 ms). Deci 26-30 ms NU e o acuratete deployabila in camp
   - e MAE dupa scaderea unui parametru fitat pe datele scorate. Recomandare:
   raporteaza MAE-ul FARA debias ca metrica principala (60-80 ms), sau un offset
   global unic.

3. Nuante de framing de corectat: sensibilitatea identica raw/windowed e tautologica
   (nu 'dovada de integritate'); PPV windowed se masoara pe ~3.7 s median (nu 4.5 s),
   iar detectiile din afara ferestrei sunt NEETICHETATE, nu fals-pozitive confirmate
   - deci precizia reala ramane nemasurabila; shape PCC -0.54 inseamna forma
   ANTI-CORELATA, nu doar 'necoincidenta'.

**Verificare cod:** implementarea e corecta tehnic si onesta (pastreaza metricile raw
alaturi de cele noi), dar contine o discrepanta minora: docstring-ul spune 'bias
median' iar codul foloseste MEDIA (np.mean). De aliniat textul sau codul.
"""

L = [INTRO]

L.append("\n## Tabel comparativ - rezultate v2 vs literatura\n")
L.append("| | Metrica | Rezultatul tau (v2) | Literatura | Sursa |")
L.append("|---|---|---|---|---|")
for r in comp.get("tabel_comparativ", []):
    ic = ICON.get(r.get("incadrare", ""), "")
    cell = lambda s: str(s).replace("|", "/").replace("\n", " ")
    L.append(f"| {ic} {cell(r.get('incadrare',''))} | {cell(r['metrica'])} | "
             f"{cell(r['rezultat_nostru'])} | {cell(r['literatura'])} | {cell(r['sursa'])} |")

L.append("\n## Verdict global (corectat dupa recenzie)\n")
L.append(comp.get("verdict_global", ""))

L.append("\n## Ce e SOLID si onest\n")
for p in comp.get("puncte_forte", []):
    L.append(f"- {p}")

L.append("\n## Limitari ramase (de scris in lucrare ca atare)\n")
for x in comp.get("limitari_ramase", []):
    L.append(f"- {x}")

L.append("\n## Concluzia recenzentului critic\n")
verdict = "DA" if ref.get("concluzie_rezista") else "NU - necesita corecturile de mai sus"
L.append(f"**Verdictul initial rezista integral?** {verdict}.\n")
L.append(ref.get("observatii", ""))
if ref.get("corecturi"):
    L.append("\n**Corecturi cerute de recenzent:**\n")
    for c in ref["corecturi"]:
        L.append(f"- {c}")

if comp.get("text_pentru_lucrare"):
    L.append("\n## Paragraf propus pentru lucrare (de ajustat cu nuantele oneste de mai sus)\n")
    L.append("> " + comp["text_pentru_lucrare"].replace("\n", "\n> "))

path = os.path.join(REPORTS, "COMPARATIE_LITERATURA_v2.md")
open(path, "w", encoding="utf-8").write("\n".join(L))
print(f"Raport salvat: {path} ({os.path.getsize(path)} bytes)")
print(f"Randuri tabel: {len(comp.get('tabel_comparativ',[]))}")
print(f"Recenzent - verdict rezista: {ref.get('concluzie_rezista')}")
