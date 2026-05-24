"""Notebook 01 — Explorare dataset Samala 2024.

Generează figuri și tabele pentru capitolul "Material și metodă" / "Rezultate"
din dizertație. Reproduce vizualizările cheie din CS3 plus statistici extinse.

Rulare: `python notebooks/01_explore_samala.py`
Output: figuri PNG în `notebooks/figs/` și tabele TXT în `notebooks/tables/`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from easy_gait import preprocessing, gait_events, segmentation, parameters
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS,
    compute_ankle_angle, load_samala_imu, list_samala_subjects, accel_magnitude,
    detect_prosthetic_side,
)

SAMALA_DIR = ROOT / "data" / "raw" / "samala_2024"
FIG_DIR = ROOT / "notebooks" / "figs"
TAB_DIR = ROOT / "notebooks" / "tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)


def fig_1_signal_overview(subject: str = "S01", trial: int = 1):
    """Fig 1: pitch shank + |accel| + ankle real pentru un trial reprezentativ."""
    g = load_samala_imu(SAMALA_DIR, subject, trial)
    df = g.df
    fs = g.fs
    prost = detect_prosthetic_side(df)
    t = np.arange(len(df)) / fs

    fig, axes = plt.subplots(3, 2, figsize=(13, 8), sharex=True)
    for col, side in enumerate(['left', 'right']):
        omega = preprocessing.gyro_pitch_dps(df, SAMALA_SHANK_GYRO_COLS[side]['pitch'], fs=fs)
        a_mag = accel_magnitude(df, SAMALA_SHANK_ACCEL_COLS[side])
        ankle = compute_ankle_angle(df, side, reference_idx=100, fs=fs)
        ev = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=(side == prost))

        tag = "PROTETIC" if side == prost else "INTACT"
        axes[0, col].plot(t, omega, lw=0.8, color="#1f77b4")
        for h in ev.hs_idx: axes[0, col].axvline(h/fs, color="r", lw=0.5, alpha=0.5)
        for o in ev.to_idx: axes[0, col].axvline(o/fs, color="b", lw=0.5, alpha=0.5)
        axes[0, col].set_title(f"{subject} W{trial} — {side.upper()} ({tag})\nShank pitch rate (gyro Y)")
        axes[0, col].set_ylabel("ω [°/s]")
        axes[0, col].grid(alpha=0.3)

        axes[1, col].plot(t, a_mag, lw=0.8, color="#ff7f0e")
        axes[1, col].set_ylabel("|a| [m/s²]")
        axes[1, col].grid(alpha=0.3)
        axes[1, col].set_title("Magnitude accelerație shank")

        axes[2, col].plot(t, ankle, lw=0.8, color="#2ca02c")
        axes[2, col].set_ylabel("θ ankle [°]")
        axes[2, col].set_xlabel("Timp [s]")
        axes[2, col].grid(alpha=0.3)
        axes[2, col].set_title("Unghi gleznă (dorsi+/plantar−)")

    fig.tight_layout()
    out = FIG_DIR / f"fig01_signal_overview_{subject}_W{trial}.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {out}")


def fig_2_stride_cycles(subject: str = "S01", trial: int = 1, side: str = "right"):
    """Fig 2: time-normalize stride-uri și suprapune (gait cycle 0-100%)."""
    g = load_samala_imu(SAMALA_DIR, subject, trial)
    df = g.df
    fs = g.fs
    omega = preprocessing.gyro_pitch_dps(df, SAMALA_SHANK_GYRO_COLS[side]['pitch'], fs=fs)
    ankle = compute_ankle_angle(df, side, reference_idx=100, fs=fs)
    ev = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=False)
    cycles = segmentation.reject_outliers(segmentation.build_cycles(ev))

    if not cycles:
        print(f"  Niciun ciclu pentru {subject} W{trial} {side}")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    gc_pct = np.linspace(0, 100, 101)
    omega_cycles, ankle_cycles = [], []
    for c in cycles:
        s, e = c.hs_start, c.hs_end
        if e - s < 5:
            continue
        local_t = np.linspace(0, 100, e - s)
        omega_cycles.append(np.interp(gc_pct, local_t, omega[s:e]))
        ankle_cycles.append(np.interp(gc_pct, local_t, ankle[s:e]))
        ax1.plot(gc_pct, omega_cycles[-1], lw=0.5, alpha=0.4, color="#1f77b4")
        ax2.plot(gc_pct, ankle_cycles[-1], lw=0.5, alpha=0.4, color="#2ca02c")

    if omega_cycles:
        om_arr = np.stack(omega_cycles)
        an_arr = np.stack(ankle_cycles)
        ax1.plot(gc_pct, om_arr.mean(0), lw=2.5, color="darkblue", label=f"Media (n={len(om_arr)})")
        ax1.fill_between(gc_pct, om_arr.mean(0)-om_arr.std(0), om_arr.mean(0)+om_arr.std(0),
                          alpha=0.2, color="darkblue")
        ax2.plot(gc_pct, an_arr.mean(0), lw=2.5, color="darkgreen", label=f"Media (n={len(an_arr)})")
        ax2.fill_between(gc_pct, an_arr.mean(0)-an_arr.std(0), an_arr.mean(0)+an_arr.std(0),
                          alpha=0.2, color="darkgreen")

    ax1.set_xlabel("Gait Cycle [%]")
    ax1.set_ylabel("ω shank [°/s]")
    ax1.set_title(f"Shank pitch rate normalizat ciclu — {subject} W{trial} {side.upper()}")
    ax1.legend(); ax1.grid(alpha=0.3); ax1.axhline(0, color="k", lw=0.3)
    ax2.set_xlabel("Gait Cycle [%]")
    ax2.set_ylabel("θ ankle [°]")
    ax2.set_title("Unghi gleznă normalizat ciclu")
    ax2.legend(); ax2.grid(alpha=0.3); ax2.axhline(0, color="k", lw=0.3)

    fig.tight_layout()
    out = FIG_DIR / f"fig02_stride_overlay_{subject}_W{trial}_{side}.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  → {out}")


def table_1_population_summary():
    """Tabel 1: cohorta Samala — n stride per subiect, cadența, ROM ankle, etc."""
    subjects = list_samala_subjects(SAMALA_DIR)
    rows = []
    for subj in subjects:
        try:
            g = load_samala_imu(SAMALA_DIR, subj, 1)
            df = g.df
            fs = g.fs
            prost = detect_prosthetic_side(df)
            for side in ['left', 'right']:
                omega = preprocessing.gyro_pitch_dps(df, SAMALA_SHANK_GYRO_COLS[side]['pitch'], fs=fs)
                ankle = compute_ankle_angle(df, side, reference_idx=100, fs=fs)
                ev = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=(side == prost))
                cycles = segmentation.reject_outliers(segmentation.build_cycles(ev))
                if not cycles:
                    continue
                p = parameters.compute_gait_params(cycles)
                rows.append({
                    "subject": subj,
                    "side": side,
                    "type": "prosth" if side == prost else "intact",
                    "n_cycles": p.n_cycles,
                    "cadence_steps_min": round(p.cadence_steps_per_min, 1),
                    "stride_mean_s": round(p.stride_s_mean, 3),
                    "stance_pct": round(p.stance_pct_mean, 1),
                    "ankle_rom_deg": round(float(ankle.max() - ankle.min()), 1),
                })
        except Exception as e:
            print(f"  ERR {subj}: {e}")
    df = pd.DataFrame(rows)
    out = TAB_DIR / "tab01_population_summary.csv"
    df.to_csv(out, index=False)
    print(f"  → {out} ({len(df)} rânduri)")

    # Sumar text
    sm = []
    for tag in ['prosth', 'intact']:
        sub = df[df["type"] == tag]
        sm.append(f"\n{tag.upper()} (n={len(sub)} laturi):")
        sm.append(f"  Cadență: {sub['cadence_steps_min'].mean():.1f} ± {sub['cadence_steps_min'].std():.1f} pași/min")
        sm.append(f"  Stride: {sub['stride_mean_s'].mean():.3f} ± {sub['stride_mean_s'].std():.3f} s")
        sm.append(f"  Stance: {sub['stance_pct'].mean():.1f} ± {sub['stance_pct'].std():.1f} %")
        sm.append(f"  ROM ankle: {sub['ankle_rom_deg'].mean():.1f} ± {sub['ankle_rom_deg'].std():.1f} °")
    txt = "\n".join(sm)
    (TAB_DIR / "tab01_population_summary.txt").write_text(txt, encoding="utf-8")
    print(txt)


def main():
    print("=== Notebook 01 — Explorare Samala 2024 ===\n")
    print("Fig 1: Signal overview (S01 W1)")
    fig_1_signal_overview("S01", 1)
    print("\nFig 2: Stride cycles overlay (S01 W1 right intact)")
    fig_2_stride_cycles("S01", 1, "right")
    print("\nFig 2 (variant prosth): S01 W1 left protetic")
    fig_2_stride_cycles("S01", 1, "left")
    print("\nTab 1: Population summary (toți 30 subiecți)")
    table_1_population_summary()
    print(f"\nTerminat. Output: {FIG_DIR} și {TAB_DIR}")


if __name__ == "__main__":
    main()
