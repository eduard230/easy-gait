"""Screenshot-uri la fiecare 0.2 s pe primele 6 s pentru subiect S01 W1 level left.

Reproduce EXACT pipeline-ul din pagina 6 Streamlit ca să văd ce vede utilizatorul.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "dashboard"))

from easy_gait import preprocessing, gait_events, fsm, ankle_controller  # noqa
from easy_gait.io_utils import (  # noqa
    SAMALA_SHANK_GYRO_COLS, detect_prosthetic_side, compute_ankle_angle,
)
from easy_gait.prosthesis_viz import (  # noqa
    compute_segments, FSM_COLORS, FSM_NAMES, GROUND_Y, PYLON_TILT_DEG,
)
from _shared import list_samala_subjects_cached, load_samala_imu_cached  # noqa


def _draw(ax, ankle_angle_deg: float, fsm_state: int, title: str):
    seg = compute_segments(ankle_angle_deg, fsm_state)
    color = FSM_COLORS.get(int(fsm_state), "#888")

    ax.axhline(GROUND_Y, color="#888", lw=1)
    # Tibia
    ax.plot([seg["ankle"][0], seg["knee"][0]],
            [seg["ankle"][1], seg["knee"][1]],
            color="#444", lw=8, solid_capstyle="round")
    # Talpa
    poly = seg["foot_poly"]
    ax.fill(poly[:, 0], poly[:, 1], color=color, alpha=0.85, edgecolor=color)
    # Gleznă
    ax.plot(*seg["ankle"], "o", ms=10, mec="black", mfc="white", mew=2)
    # Genunchi
    ax.plot(*seg["knee"], "o", ms=11, mec="black", mfc="#666", mew=1)

    ax.set_xlim(-0.40, 0.50)
    ax.set_ylim(-0.05, 0.60)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_title(title, fontsize=9)


def main():
    subject = "S01"
    trial = 1
    activity = "level"
    side = "left"  # forțat conform cererii

    df, fs, _ = load_samala_imu_cached(subject, trial)
    prost_side = detect_prosthetic_side(df)
    is_prost = (side == prost_side)
    print(f"S01 W1 | side requested: {side} | prosthetic side detected: {prost_side} "
          f"| is_prosthetic: {is_prost} | fs: {fs}")

    pitch_col = SAMALA_SHANK_GYRO_COLS[side]["pitch"]
    omega = preprocessing.gyro_pitch_dps(df, pitch_col, fs=fs)
    events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=is_prost)
    ref_idx = int(events.hs_idx[0]) if len(events.hs_idx) > 0 else 100
    ankle_real = compute_ankle_angle(df, side, reference_idx=ref_idx)
    trace = fsm.run_fsm(
        n_samples=len(df), fs=fs,
        hs_idx=events.hs_idx, to_idx=events.to_idx,
        omega_shank_dps=omega, ankle_angle_estimate_deg=ankle_real,
        config=fsm.FSMConfig(activity=activity),
    )
    ankle_fsm = ankle_controller.generate_trajectory(trace, fs=fs)

    # Eșantioane la fiecare 0.2 s pe primele 6 s
    times = np.arange(0.0, 6.001, 0.2)
    n_frames = len(times)
    cols = 6
    rows = int(np.ceil(n_frames / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.6, rows * 2.6))
    axes = axes.flatten()

    print("\nFrame timeline (PYLON_TILT_DEG =", PYLON_TILT_DEG, "deg):")
    print(f"{'t(s)':>6} {'idx':>5} {'state':>6} {'theta':>8} "
          f"{'ankle_x':>8} {'ankle_y':>8} {'knee_x':>8} {'knee_y':>8} "
          f"{'toe_y':>8} {'heel_y':>8} {'foot_y_min':>10}")

    for i, t in enumerate(times):
        idx = int(round(t * fs))
        if idx >= len(ankle_fsm):
            axes[i].axis("off")
            continue
        a = float(ankle_fsm[idx])
        s = int(trace.state_per_sample[idx])
        seg = compute_segments(a, s)
        foot_y_min = float(seg["foot_poly"][:, 1].min())
        print(f"{t:6.2f} {idx:5d} S{s:1d}    {a:+8.2f} "
              f"{seg['ankle'][0]:+8.3f} {seg['ankle'][1]:+8.3f} "
              f"{seg['knee'][0]:+8.3f} {seg['knee'][1]:+8.3f} "
              f"{seg['toe'][1]:+8.3f} {seg['heel'][1]:+8.3f} {foot_y_min:+10.3f}")
        _draw(axes[i], a, s, f"t={t:.1f}s | S{s} | θ={a:+.1f}°")

    # Hide unused axes
    for j in range(n_frames, len(axes)):
        axes[j].axis("off")

    fig.suptitle(
        f"Timeline 0..6s la 0.2s pas — {subject} W{trial} {activity} side={side} "
        f"({'PROTETIC' if is_prost else 'INTACT'})",
        fontsize=11, y=1.0,
    )
    fig.tight_layout()
    out = ROOT / "scripts" / "debug_timeline.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    print(f"\nSalvat: {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
