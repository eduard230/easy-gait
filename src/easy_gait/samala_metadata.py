"""Metadate per-subiect pentru datasetul Samala 2024 (Sci Data 11:922).

Sursa: Tabelul 3 din Samala et al. 2024, "A dataset of optical camera and IMU
sensor derived kinematics of thirty transtibial prosthesis wearers",
Scientific Data 11:922 (Nature). DOI 10.1038/s41597-024-03677-3.
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC11344789/

Toate cele 30 de proteze din studiu sunt PASIVE (mecanice). Nu există nicio
proteză cu gleznă acționată (BiOM/Empower/Proprio). Asta explică ROM-ul mic
al gleznei observat pe partea protetică în toate trial-urile.

Tipuri foot (toate pasive):
  - SACH (Solid Ankle Cushion Heel): rigid, fără mișcare gleznă → cel mai
    simplu și restrictiv (ROM ~0-5°). 24/30 subiecți.
  - Dynamic (ESR — Energy Storing & Return): lamă de carbon care stochează
    și eliberează energie elastic; oferă "push-off" pasiv. 3/30 subiecți.
  - sPace (Endolite): proteză pasivă multi-axială cu absorbție hidraulică.
    2/30 subiecți.
  - Single axis: o singură axă de rotație în gleznă, pasivă. 1/30 subiecți.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProsthesisMeta:
    subject: str
    gender: str            # "M" | "F"
    age_y: int
    weight_kg: float
    height_m: float
    amputated_side: str    # "left" | "right"
    structure: str         # "endoskeletal" | "exoskeletal"
    socket: str            # PTB | TSB | PTB-SC | TSB-SC
    liner: str             # Pe-lite | Silicone | Aero liner
    suspension: str        # Cuff | Self | Suction | Sleeve
    foot_type: str         # SACH | Dynamic | sPace | Single axis
    activity_type: str     # "passive" (toate sunt pasive în acest dataset)


# Tabelul 3 din Samala et al. 2024 — toate 30 de subiecți
SAMALA_META: dict[str, ProsthesisMeta] = {
    "S01": ProsthesisMeta("S01", "M", 70, 63.0, 1.74, "left",  "endoskeletal", "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S02": ProsthesisMeta("S02", "M", 32, 82.0, 1.69, "left",  "endoskeletal", "TSB",    "Silicone",   "Suction", "Dynamic",     "passive"),
    "S03": ProsthesisMeta("S03", "M", 56, 93.0, 1.72, "left",  "endoskeletal", "PTB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S04": ProsthesisMeta("S04", "M", 35, 67.0, 1.67, "left",  "endoskeletal", "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S05": ProsthesisMeta("S05", "M", 50, 86.0, 1.80, "right", "endoskeletal", "TSB-SC", "Aero liner", "Self",    "SACH",        "passive"),
    "S06": ProsthesisMeta("S06", "F", 64, 77.0, 1.62, "left",  "endoskeletal", "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S07": ProsthesisMeta("S07", "M", 45, 59.0, 1.60, "right", "endoskeletal", "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S08": ProsthesisMeta("S08", "M", 49, 58.0, 1.60, "right", "endoskeletal", "TSB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S09": ProsthesisMeta("S09", "M", 59, 57.0, 1.59, "right", "endoskeletal", "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S10": ProsthesisMeta("S10", "M", 24, 47.0, 1.68, "left",  "endoskeletal", "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S11": ProsthesisMeta("S11", "M", 54, 66.0, 1.61, "left",  "endoskeletal", "TSB",    "Silicone",   "Cuff",    "SACH",        "passive"),
    "S12": ProsthesisMeta("S12", "M", 64, 62.0, 1.65, "left",  "exoskeletal",  "PTB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S13": ProsthesisMeta("S13", "M", 44, 82.0, 1.70, "left",  "endoskeletal", "TSB",    "Silicone",   "Sleeve",  "sPace",       "passive"),
    "S14": ProsthesisMeta("S14", "M", 53, 65.0, 1.60, "left",  "exoskeletal",  "TSB-SC", "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S15": ProsthesisMeta("S15", "M", 58, 68.0, 1.60, "left",  "exoskeletal",  "PTB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S16": ProsthesisMeta("S16", "F", 58, 50.0, 1.55, "left",  "exoskeletal",  "PTB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S17": ProsthesisMeta("S17", "M", 41, 85.0, 1.74, "right", "exoskeletal",  "PTB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S18": ProsthesisMeta("S18", "M", 51, 80.0, 1.72, "right", "exoskeletal",  "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S19": ProsthesisMeta("S19", "M", 64, 72.0, 1.74, "left",  "exoskeletal",  "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S20": ProsthesisMeta("S20", "M", 51, 70.0, 1.70, "right", "endoskeletal", "PTB-SC", "Pe-lite",    "Self",    "Single axis", "passive"),
    "S21": ProsthesisMeta("S21", "M", 53, 54.0, 1.70, "right", "exoskeletal",  "PTB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S22": ProsthesisMeta("S22", "M", 54, 84.0, 1.65, "right", "endoskeletal", "TSB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S23": ProsthesisMeta("S23", "M", 46, 59.0, 1.59, "right", "endoskeletal", "TSB",    "Silicone",   "Sleeve",  "sPace",       "passive"),
    "S24": ProsthesisMeta("S24", "F", 43, 60.7, 1.58, "left",  "endoskeletal", "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S25": ProsthesisMeta("S25", "M", 68, 65.0, 1.67, "right", "exoskeletal",  "PTB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S26": ProsthesisMeta("S26", "M", 75, 63.5, 1.64, "left",  "endoskeletal", "PTB-SC", "Pe-lite",    "Self",    "SACH",        "passive"),
    "S27": ProsthesisMeta("S27", "F", 69, 47.0, 1.50, "right", "exoskeletal",  "PTB-SC", "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S28": ProsthesisMeta("S28", "M", 64, 54.0, 1.63, "right", "endoskeletal", "PTB",    "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S29": ProsthesisMeta("S29", "F", 72, 75.0, 1.56, "left",  "endoskeletal", "PTB-SC", "Pe-lite",    "Cuff",    "SACH",        "passive"),
    "S30": ProsthesisMeta("S30", "M", 33, 68.0, 1.73, "right", "endoskeletal", "PTB-SC", "Pe-lite",    "Sleeve",  "Dynamic",     "passive"),
}


# Descrieri scurte ale tipurilor de foot (pentru tooltip-uri în UI)
FOOT_TYPE_DESC: dict[str, str] = {
    "SACH": (
        "Solid Ankle Cushion Heel — proteză pasivă rigidă, fără mișcare la "
        "gleznă. Călcâiul moale absoarbe șocul la HS. ROM gleznă ~0-5°. "
        "Cea mai simplă și ieftină proteză transtibială."
    ),
    "Dynamic": (
        "Dynamic foot (ESR — Energy Storing & Return) — lamă de carbon "
        "care stochează energie elastic în stance și o eliberează la push-off. "
        "Pasivă, dar oferă propulsie mai bună decât SACH. ROM ~10-20°."
    ),
    "sPace": (
        "Endolite sPace — proteză pasivă multi-axială cu absorbție hidraulică "
        "în plan sagital. Permite mers pe teren neregulat. ROM ~15-25°."
    ),
    "Single axis": (
        "Single axis foot — pasivă cu o singură axă de rotație în gleznă "
        "(doar plantarflexie/dorsiflexie). Permite contact rapid al tălpii "
        "la HS. ROM limitat ~10°."
    ),
}


def get_meta(subject: str) -> ProsthesisMeta | None:
    """Returnează metadatele pentru un subiect Samala, sau None dacă nu există."""
    return SAMALA_META.get(subject)
