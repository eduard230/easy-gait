"""Notebook 02 — Explorare dataset Wassall 2025 (terenuri reale).

Citește CSV-urile generate de `scripts/compute_wassall_summary.py` și produce:
  - Fig 1: cadență per teren (boxplot)
  - Fig 2: stride duration per teren (boxplot)
  - Fig 3: stride CV per teren (regularitate; mai mare = mai variabil)
  - Fig 4: efectul bastonului (with vs without aid) pe cadență
  - Tab 1: sumar agregat per teren

Rulare: `python notebooks/02_explore_wassall.py`
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DATA_PATH = ROOT / "data" / "processed" / "wassall_per_trial.csv"
FIG_DIR = ROOT / "notebooks" / "figs"
TAB_DIR = ROOT / "notebooks" / "tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)


# Ordinea terenurilor pentru afișare (de la cel mai simplu la cel mai complex)
TERRAIN_ORDER = ["flat", "grass", "gravel", "slope", "stair", "uneven"]
TERRAIN_COLORS = {
    "flat": "#2ca02c", "grass": "#8c564b", "gravel": "#7f7f7f",
    "slope": "#ff7f0e", "stair": "#d62728", "uneven": "#9467bd",
}


def _filter_main(df: pd.DataFrame) -> pd.DataFrame:
    """Păstrează doar terenurile principale (exclude step_multi, CS și similar)."""
    return df[df["terrain"].isin(TERRAIN_ORDER)].copy()


def fig_boxplot(df: pd.DataFrame, ycol: str, ylabel: str, title: str, fname: str,
                yref: float | None = None, yref_label: str | None = None):
    fig, ax = plt.subplots(figsize=(10, 5))
    data = [df[df["terrain"] == t][ycol].dropna().values for t in TERRAIN_ORDER]
    bp = ax.boxplot(data, labels=TERRAIN_ORDER, patch_artist=True, showmeans=True,
                     meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="black"))
    for patch, t in zip(bp["boxes"], TERRAIN_ORDER):
        patch.set_facecolor(TERRAIN_COLORS[t]); patch.set_alpha(0.7)
    if yref is not None:
        ax.axhline(yref, color="k", lw=1, ls="--", alpha=0.5,
                   label=yref_label or f"ref={yref}")
        ax.legend()
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Teren")
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = FIG_DIR / fname
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {out}")


def fig_walkaid_effect(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 5))
    width = 0.35
    x = np.arange(len(TERRAIN_ORDER))
    for offset, walkaid in zip([-width/2, width/2], ["without_aid", "with_aid"]):
        means, stds = [], []
        for t in TERRAIN_ORDER:
            sub = df[(df["terrain"] == t) & (df["walkaid"] == walkaid)]["cadence_steps_min"]
            means.append(sub.mean() if len(sub) else np.nan)
            stds.append(sub.std() if len(sub) > 1 else 0)
        ax.bar(x + offset, means, width, yerr=stds, label=walkaid.replace("_", " "),
                capsize=4, alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(TERRAIN_ORDER)
    ax.set_ylabel("Cadență [pași/min]")
    ax.set_title("Efectul bastonului asupra cadenței, per teren")
    ax.legend(); ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = FIG_DIR / "fig04_walkaid_effect.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {out}")


def main():
    if not DATA_PATH.exists():
        print(f"Lipsește {DATA_PATH}. Rulează întâi: python scripts/compute_wassall_summary.py")
        return
    df = pd.read_csv(DATA_PATH)
    print(f"Total trial-uri: {len(df)} | participanți: {df['participant'].nunique()}")
    df = _filter_main(df)
    print(f"După filtrare teren principal: {len(df)} trial-uri")

    print("\nFig 1: Cadență per teren")
    fig_boxplot(df, "cadence_steps_min", "Cadență [pași/min]",
                "Cadență pe teren — toți participanții", "fig03_cadence_per_terrain.png")

    print("\nFig 2: Stride mean per teren")
    fig_boxplot(df, "stride_mean_s", "Stride mean [s]",
                "Durată stride mediu pe teren", "fig04_stride_per_terrain.png")

    print("\nFig 3: Stride CV per teren (variabilitate)")
    fig_boxplot(df, "stride_cv", "Stride CV [-]",
                "Variabilitate stride pe teren (CV)", "fig05_stride_cv_per_terrain.png",
                yref=0.03, yref_label="ref healthy ~3%")

    print("\nFig 4: Efectul bastonului")
    fig_walkaid_effect(df)

    print("\nTab 1: Sumar agregat per teren")
    agg = df.groupby("terrain").agg(
        n_trials=("cadence_steps_min", "count"),
        cadence_mean=("cadence_steps_min", "mean"),
        cadence_std=("cadence_steps_min", "std"),
        stride_mean=("stride_mean_s", "mean"),
        stride_std=("stride_mean_s", "std"),
        stride_cv_mean=("stride_cv", "mean"),
        stance_mean=("stance_mean_pct", "mean"),
    ).round(2).reindex(TERRAIN_ORDER)
    out = TAB_DIR / "tab02_wassall_per_terrain.csv"
    agg.to_csv(out)
    print(f"  → {out}")
    print(agg)


if __name__ == "__main__":
    main()
