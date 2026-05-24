# easy-gait

Platformă software pentru analiza ciclului de mers și control adaptiv al gleznei utilizând date IMU.

**Dizertație:** Raluca Andreea PĂUN — UPB FIM TMIM, sesiune ianuarie 2026
**Coordonator:** Conf. dr. ing. Mădălin-Corneliu FRUNZETE

## Scop

Procesare semnale IMU de la purtători de proteze transtibiale → detecție automată evenimente HS/TO → segmentare ciclu de mers → calcul parametri → simulare FSM control gleznă protetică → vizualizare interactivă în dashboard Streamlit. **Fără hardware real** — datele provin din baze publice peer-reviewed (Samala 2024, Wassall 2025).

## Quick start

```bash
git clone <repo-url>
cd easy-gait
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e .

# Descarcă dataseturile (vezi data/raw/.gitkeep pentru link-uri)
# Plasează în data/raw/samala_2024/ și data/raw/wassall_2025/

streamlit run dashboard/app.py
```

## Structura repo

```
easy-gait/
├── src/easy_gait/          # 13 module Python (pachet pip install -e .)
├── dashboard/              # Streamlit multi-pagină (6 pagini)
├── notebooks/              # 4 scripturi reproducibile + figs/ + tables/
├── scripts/                # 6 scripturi batch (validare, generate PDF)
├── tests/                  # pytest unit tests
├── data/
│   ├── raw/                # ←  pune dataseturile aici (gitignore)
│   └── processed/          # CSV-uri rezultat (incluse în repo)
├── docs/
│   ├── DESIGN.md           # arhitectura + justificări
│   ├── ALGORITHMS.md       # algoritmi + citări
│   └── easy-gait_documentatie_completa.pdf   ← 54 pagini doc
└── README.md
```

## Rezultate cheie (extras Cap. 11 documentație)

| Metric | Trojaniello | Maqbool | Țintă DESIGN |
|---|---|---|---|
| HS MAE | 80 ms | 60 ms | < 25 ms |
| HS sens | 58.4% | 63.3% | > 99% |
| TO MAE | 61 ms | 77 ms | < 50 ms |

| Validare ankle | RMSE | PCC | Țintă |
|---|---|---|---|
| FSM vs OMC | 13.7° | −0.24 | < 5° / > 0.90 |
| IMU vs OMC | 8.75° | +0.65 | (rezonabil per Pacini Panebianco 2018) |

**Confirmări biomecanice (n=30 Samala):**
- ROM ankle prosth 17° vs intact 38.6° (−56%) — confirm Hsu 2006
- Stance% prosth 51.7% vs intact 55.5% (−3.8 pp) — confirm Sanderson 1997
- Cadence prosth ≡ intact (~100 pași/min) — compensare cinematică spațială

## Reproducere rezultate

```bash
# Validare HS/TO pe toți 30 subiecți (300 trial-laturi)
python scripts/validate_events_all.py

# Validare traiectorie ankle FSM/IMU vs OMC
python scripts/validate_fsm_all.py

# Agregare Wassall per teren (506 trial-uri)
python scripts/compute_wassall_summary.py

# Generare 4 notebook-uri cu figuri și tabele
python notebooks/01_explore_samala.py
python notebooks/02_explore_wassall.py
python notebooks/03_validate_events.py
python notebooks/04_fsm_validation.py

# Generare PDF documentație 54 pagini
python scripts/generate_documentation_pdf.py
```

## Testare

```bash
pytest tests/
```

## Citare

Lucrarea folosește algoritmi din: Trojaniello 2014 (gold-standard HS/TO), Maqbool 2017 (FSM-friendly real-time), Zeni 2008 (OMC ground truth), Au & Herr 2008 + Sup 2008 + Bartlett 2021 (FSM gleznă protetică), Catalfamo 2010 + Yu 1999 + Winter 1991 (filtrare).

Vezi `docs/ALGORITHMS.md` și Anexa C din PDF pentru lista completă (26 referințe).

## Documentație completă

PDF de 54 pagini cu: arhitectura, algoritmi, FSM, vizualizare proteză, dashboard, validare, rezultate biomecanice, limitări, concluzii cantitative.

**Locație:** `docs/easy-gait_documentatie_completa.pdf`
