"""Procesează TOȚI participanții Wassall și produce CSV-uri sumar inter-activități.

Outputs:
  - `data/processed/wassall_per_trial.csv` — un rând per trial cu parametri
  - `data/processed/wassall_per_terrain.csv` — agregare mean±std per teren
  - `data/processed/wassall_per_terrain_walkaid.csv` — agregare per (teren, baston)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from easy_gait.activity_compare import (
    process_participant, aggregate_by_terrain, aggregate_by_terrain_and_walkaid,
)
from easy_gait.io_utils import list_wassall_participants

WASSALL_DIR = ROOT / "data" / "raw" / "wassall_2025"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    participants = list_wassall_participants(WASSALL_DIR)
    print(f"Participanți Wassall: {len(participants)}")
    all_dfs = []
    for i, p in enumerate(participants, 1):
        df = process_participant(WASSALL_DIR, p)
        if not df.empty:
            all_dfs.append(df)
        print(f"  {i}/{len(participants)} {p}: {len(df)} trials")
    if not all_dfs:
        print("Nimic procesat.")
        return
    combined = pd.concat(all_dfs, ignore_index=True)
    per_trial_path = OUT_DIR / "wassall_per_trial.csv"
    combined.to_csv(per_trial_path, index=False)
    print(f"\nSalvat: {per_trial_path} ({len(combined)} rânduri)")

    agg_terrain = aggregate_by_terrain(combined)
    p1 = OUT_DIR / "wassall_per_terrain.csv"
    agg_terrain.to_csv(p1)
    print(f"Salvat: {p1}")

    agg_tw = aggregate_by_terrain_and_walkaid(combined)
    p2 = OUT_DIR / "wassall_per_terrain_walkaid.csv"
    agg_tw.to_csv(p2)
    print(f"Salvat: {p2}")

    print("\n=== Sumar per teren ===")
    print(agg_terrain[[c for c in agg_terrain.columns if c.endswith("_mean") or c == "n_trials"]])


if __name__ == "__main__":
    main()
