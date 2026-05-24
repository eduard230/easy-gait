"""Vizualizează fiecare fază FSM (S1..S5) ca snapshot static pentru un subiect.

Salvează un PNG cu 5 subploturi (câte o stare) ca să verificăm vizual că
tibia se mișcă fiziologic peste talpă în stance și se ridică în swing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "dashboard"))

from easy_gait import preprocessing, gait_events, fsm, ankle_controller  # noqa: E402
from easy_gait.io_utils import (  # noqa: E402
    SAMALA_SHANK_GYRO_COLS, detect_prosthetic_side, compute_ankle_angle,
)
from easy_gait.prosthesis_viz import (  # noqa: E402
    compute_segments, FSM_COLORS, FSM_NAMES, GROUND_Y,
)
from _shared import list_samala_subjects_cached, load_samala_imu_cached  # noqa: E402


def _draw_frame(ax, ankle_angle_deg: float, fsm_state: int, title: str):
    seg = compute_segments(ankle_angle_deg, fsm_state)
    color = FSM_COLORS[fsm_state]

    # Sol
    ax.axhline(GROUND_Y, color="#888", lw=1)
    # Tibia
    ax.plot([seg["ankle"][0], seg["knee"][0]],
            [seg["ankle"][1], seg["knee"][1]],
            color="#444", lw=10, solid_capstyle="round")
    # Talpa
    poly = seg["foot_poly"]
    ax.fill(poly[:, 0], poly[:, 1], color=color, alpha=0.85, edgecolor=color)
    # Gleznă
    ax.plot(*seg["ankle"], "o", ms=12, mec="black", mfc="white", mew=2)
    # Genunchi
    ax.plot(*seg["knee"], "o", ms=14, mec="black", mfc="#666", mew=1)

    ax.set_xlim(-0.45, 0.55)
    ax.set_ylim(-0.05, 0.65)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_title(f"{title}\nθ = {ankle_angle_deg:+.1f}°", fontsize=10)

    # Print în consolă pentru inspecție
    print(f"  {title}: θ={ankle_angle_deg:+.1f}° | tilt_tibie={seg.get('tibia_tilt_deg', 0):+.1f}° | "
          f"ankle=({seg['ankle'][0]:+.3f}, {seg['ankle'][1]:+.3f}) | "
          f"knee=({seg['knee'][0]:+.3f}, {seg['knee'][1]:+.3f}) | "
          f"foot_y_min={min(seg['foot_poly'][:, 1]):+.3f}")


def main(subject: str | None = None, trial: int = 1, activity: str = "level"):
    subjects = list_samala_subjects_cached()
    if subject is None:
        subject = subjects[0]
    print(f"\n=== Subiect: {subject} | Trial: W{trial} | Activitate: {activity} ===\n")

    df, fs, _ = load_samala_imu_cached(subject, trial)
    prost = detect_prosthetic_side(df)
    side = prost

    pitch_col = SAMALA_SHANK_GYRO_COLS[side]["pitch"]
    omega = preprocessing.gyro_pitch_dps(df, pitch_col, fs=fs)
    events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=True)
    ref_idx = int(events.hs_idx[0]) if len(events.hs_idx) > 0 else 100
    ankle_real = compute_ankle_angle(df, side, reference_idx=ref_idx)
    trace = fsm.run_fsm(
        n_samples=len(df), fs=fs,
        hs_idx=events.hs_idx, to_idx=events.to_idx,
        omega_shank_dps=omega, ankle_angle_estimate_deg=ankle_real,
        config=fsm.FSMConfig(activity=activity),
    )
    ankle_fsm = ankle_controller.generate_trajectory(trace, fs=fs)

    # Pentru fiecare stare, găsește un sample reprezentativ (la mijlocul primei apariții)
    fig, axes = plt.subplots(1, 5, figsize=(18, 4.5))
    print("Sample reprezentativ per stare (poziții cheie):")
    for s_int in range(1, 6):
        mask = trace.state_per_sample == s_int
        if not mask.any():
            axes[s_int - 1].set_title(f"{FSM_NAMES[s_int]}\n(absent)")
            axes[s_int - 1].axis("off")
            continue
        idxs = np.where(mask)[0]
        # Mijlocul primei serii consecutive
        diffs = np.diff(idxs)
        breaks = np.where(diffs > 1)[0]
        if len(breaks) > 0:
            first_run = idxs[: breaks[0] + 1]
        else:
            first_run = idxs
        center_idx = int(first_run[len(first_run) // 2])
        a = float(ankle_fsm[center_idx])
        _draw_frame(axes[s_int - 1], a, s_int, FSM_NAMES[s_int])

    fig.suptitle(
        f"Faze FSM static — {subject} W{trial} ({activity}) — pivot pe sol fiziologic",
        fontsize=12, y=1.02,
    )
    fig.tight_layout()
    out = ROOT / "scripts" / "debug_phases.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    print(f"\nSalvat: {out}")
    plt.close(fig)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--subject", default=None)
    p.add_argument("--trial", type=int, default=1)
    p.add_argument("--activity", default="level")
    args = p.parse_args()
    main(args.subject, args.trial, args.activity)
