"""Compară ROM (range of motion) ankle între subiecți S01..S06.

Pentru fiecare subiect, calculează:
  - ROM ankle FSM (max - min)
  - ROM ankle real (IMU joint)
  - Min/max pe stance vs swing
  - Saturatie la setpoint? (cât timp e talpa "blocată" la o valoare)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "dashboard"))

from easy_gait import preprocessing, gait_events, fsm, ankle_controller  # noqa
from easy_gait.io_utils import (  # noqa
    SAMALA_SHANK_GYRO_COLS, detect_prosthetic_side, compute_ankle_angle,
)
from _shared import list_samala_subjects_cached, load_samala_imu_cached  # noqa


def analyze(subject: str, trial: int = 1, activity: str = "level"):
    df, fs, _ = load_samala_imu_cached(subject, trial)
    prost_side = detect_prosthetic_side(df)
    print(f"\n=== {subject} W{trial} {activity} | prost_side={prost_side} | fs={fs} ===")

    for side in ["left", "right"]:
        is_prost = (side == prost_side)
        pitch_col = SAMALA_SHANK_GYRO_COLS[side]["pitch"]
        omega = preprocessing.gyro_pitch_dps(df, pitch_col, fs=fs)
        events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=is_prost)
        if len(events.hs_idx) < 2 or len(events.to_idx) < 2:
            print(f"  {side.upper():>5}: insufficient events (HS={len(events.hs_idx)}, TO={len(events.to_idx)})")
            continue
        ref_idx = int(events.hs_idx[0])
        ankle_real = compute_ankle_angle(df, side, reference_idx=ref_idx)
        trace = fsm.run_fsm(
            n_samples=len(df), fs=fs,
            hs_idx=events.hs_idx, to_idx=events.to_idx,
            omega_shank_dps=omega, ankle_angle_estimate_deg=ankle_real,
            config=fsm.FSMConfig(activity=activity),
        )
        ankle_fsm = ankle_controller.generate_trajectory(trace, fs=fs)

        # Statistici per stare
        tag = "PROST" if is_prost else "INTACT"
        print(f"  {side.upper():>5} ({tag}):")
        print(f"    ankle_real: min={np.min(ankle_real):+.1f}°, max={np.max(ankle_real):+.1f}°, "
              f"ROM={np.max(ankle_real)-np.min(ankle_real):.1f}°")
        print(f"    ankle_fsm : min={np.min(ankle_fsm):+.1f}°, max={np.max(ankle_fsm):+.1f}°, "
              f"ROM={np.max(ankle_fsm)-np.min(ankle_fsm):.1f}°")
        # Per stare
        for s_int in range(1, 6):
            mask = trace.state_per_sample == s_int
            if mask.sum() < 5:
                continue
            real_in_state = ankle_real[mask]
            fsm_in_state = ankle_fsm[mask]
            print(f"    S{s_int}: n={mask.sum():5d}, "
                  f"real=[{real_in_state.min():+6.1f}, {real_in_state.max():+6.1f}]°, "
                  f"fsm=[{fsm_in_state.min():+6.1f}, {fsm_in_state.max():+6.1f}]°")
        # Strides
        strides = np.diff(events.hs_idx) / fs
        print(f"    strides: n={len(strides)}, "
              f"mean={strides.mean():.2f}s, std={strides.std():.2f}s")


def main():
    subjects = list_samala_subjects_cached()
    print(f"Subjects available: {subjects}")
    for subj in subjects[:6]:
        analyze(subj, trial=1, activity="level")


if __name__ == "__main__":
    main()
