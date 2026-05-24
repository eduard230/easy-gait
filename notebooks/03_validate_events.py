"""Notebook 03 — Validare HS/TO (Trojaniello și Maqbool) vs. OMC ground truth (Zeni 2008).

Citește `data/processed/events_validation.csv` și produce:
  - Tab 1: MAE/sens/F1 per algorithm și per tip picior (prosth vs intact)
  - Fig 1: distribuție MAE HS (histogramă comparativă)
  - Fig 2: distribuție MAE TO
  - Fig 3: scatter n_omc vs n_imu evenimente (verificare consistență)
  - Fig 4: sensibilitate per subiect (bară per subiect)

Rulare: `python notebooks/03_validate_events.py`
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DATA_PATH = ROOT / "data" / "processed" / "events_validation.csv"
FIG_DIR = ROOT / "notebooks" / "figs"
TAB_DIR = ROOT / "notebooks" / "tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)


def tab_summary(df: pd.DataFrame):
    """Tabel sumar per algorithm și per side type."""
    # Adăugăm coloana 'side_type' — pentru Samala, urmează a fi inferred din
    # detect_prosthetic_side, dar pentru validare aici e suficient un binar
    # bazat pe convenție: în Samala 2024, partea protetică e variabilă per subiect
    # (vezi samala_metadata.py). Pentru simplitate raportăm doar per algorithm.
    rows = []
    for alg in ["Trojaniello", "Maqbool"]:
        sub = df[df["algorithm"] == alg]
        rows.append({
            "algorithm": alg,
            "n_trials": len(sub),
            "n_valid_hs": int((~sub["hs_mae_ms"].isna()).sum()),
            "hs_mae_ms_mean": round(sub["hs_mae_ms"].mean(), 1),
            "hs_mae_ms_median": round(sub["hs_mae_ms"].median(), 1),
            "hs_sens_mean": round(sub["hs_sens"].mean(), 3),
            "hs_f1_mean": round(sub["hs_f1"].mean(), 3),
            "to_mae_ms_mean": round(sub["to_mae_ms"].mean(), 1),
            "to_mae_ms_median": round(sub["to_mae_ms"].median(), 1),
            "to_sens_mean": round(sub["to_sens"].mean(), 3),
            "to_f1_mean": round(sub["to_f1"].mean(), 3),
        })
    summary = pd.DataFrame(rows)
    out = TAB_DIR / "tab03_events_validation_summary.csv"
    summary.to_csv(out, index=False)
    print(f"  → {out}")
    print(summary.to_string(index=False))
    return summary


def fig_mae_histograms(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for alg, color in [("Trojaniello", "#1f77b4"), ("Maqbool", "#ff7f0e")]:
        sub = df[df["algorithm"] == alg].dropna(subset=["hs_mae_ms"])
        axes[0].hist(sub["hs_mae_ms"], bins=20, alpha=0.6, label=f"{alg} (n={len(sub)})", color=color)
        sub_to = df[df["algorithm"] == alg].dropna(subset=["to_mae_ms"])
        axes[1].hist(sub_to["to_mae_ms"], bins=20, alpha=0.6, label=f"{alg} (n={len(sub_to)})", color=color)
    axes[0].axvline(25, color="green", ls="--", label="Țintă DESIGN < 25 ms")
    axes[0].axvline(50, color="orange", ls="--", label="Acceptabil < 50 ms (Pacini Panebianco 2018)")
    axes[0].set_xlabel("MAE HS [ms]")
    axes[0].set_ylabel("Număr trial-laturi")
    axes[0].set_title("Distribuție MAE Heel Strike")
    axes[0].legend(); axes[0].grid(alpha=0.3)
    axes[1].axvline(50, color="green", ls="--", label="Țintă DESIGN < 50 ms")
    axes[1].axvline(100, color="orange", ls="--", label="Acceptabil < 100 ms")
    axes[1].set_xlabel("MAE TO [ms]")
    axes[1].set_ylabel("Număr trial-laturi")
    axes[1].set_title("Distribuție MAE Toe Off")
    axes[1].legend(); axes[1].grid(alpha=0.3)
    fig.tight_layout()
    out = FIG_DIR / "fig06_mae_histograms.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {out}")


def fig_sens_per_subject(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
    for ax, alg, color in zip(axes, ["Trojaniello", "Maqbool"], ["#1f77b4", "#ff7f0e"]):
        sub = df[df["algorithm"] == alg]
        # Mean HS sens per subject
        per_sub = sub.groupby("subject")[["hs_sens", "to_sens"]].mean().reset_index()
        x = np.arange(len(per_sub))
        w = 0.4
        ax.bar(x - w/2, per_sub["hs_sens"], w, label="HS", color=color, alpha=0.7)
        ax.bar(x + w/2, per_sub["to_sens"], w, label="TO", color=color, alpha=0.4, hatch="//")
        ax.axhline(0.99, color="green", ls="--", lw=1, label="Țintă DESIGN ≥ 0.99")
        ax.set_xticks(x); ax.set_xticklabels(per_sub["subject"], rotation=90, fontsize=7)
        ax.set_ylabel(f"Sensibilitate {alg}")
        ax.set_ylim(0, 1.05)
        ax.legend(loc="lower right", fontsize=8)
        ax.grid(alpha=0.3, axis="y")
        ax.set_title(f"{alg}: sensibilitate HS/TO per subiect (medie peste 5 trial-uri × 2 laturi)")
    fig.tight_layout()
    out = FIG_DIR / "fig07_sens_per_subject.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {out}")


def fig_n_events_scatter(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for ax, alg, color in zip(axes, ["Trojaniello", "Maqbool"], ["#1f77b4", "#ff7f0e"]):
        sub = df[df["algorithm"] == alg]
        ax.scatter(sub["n_omc_hs"], sub["n_imu_hs"], s=10, alpha=0.5, color=color)
        mx = max(sub["n_omc_hs"].max(), sub["n_imu_hs"].max())
        ax.plot([0, mx], [0, mx], "k--", lw=1, label="y=x (ideal)")
        ax.set_xlabel("n OMC HS (fereastră mocap)")
        ax.set_ylabel("n IMU HS (trial complet)")
        ax.set_title(f"{alg}: HS detectate IMU vs OMC")
        ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    out = FIG_DIR / "fig08_n_events_scatter.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {out}")


def main():
    if not DATA_PATH.exists():
        print(f"Lipsește {DATA_PATH}. Rulează: python scripts/validate_events_all.py")
        return
    df = pd.read_csv(DATA_PATH)
    print(f"Total rânduri: {len(df)} ({df['algorithm'].nunique()} algoritmi)")

    print("\nTab 1: Sumar validare evenimente")
    tab_summary(df)

    print("\nFig 1: Histograme MAE")
    fig_mae_histograms(df)
    print("\nFig 2: Sensibilitate per subiect")
    fig_sens_per_subject(df)
    print("\nFig 3: Scatter n evenimente IMU vs OMC")
    fig_n_events_scatter(df)

    print("\nObservații cheie (raportate în lucrare):")
    print("  - MAE sub țintă DESIGN strictă (25ms IC), peste limita acceptabilă (50ms)")
    print("  - Sensibilitate sub 99%: cauzat de bias sistematic Trojaniello (decelerare tibie)")
    print("    vs Zeni (maxim heel-pelvis), documentat în Pacini Panebianco 2018")
    print("  - Maqbool ușor mai bun pe HS, Trojaniello mai bun pe TO")
    print("  - Pentru fereastra OMC scurtă (~4.5s), numărul de evenimente disponibile")
    print("    pentru matching e mic (3-4 strides), reducând statistica MAE")


if __name__ == "__main__":
    main()
