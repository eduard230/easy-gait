"""Validare traiectorie FSM vs. unghi gleznă OMC (ground truth) pe TOȚI subiecții Samala.

Output: `data/processed/fsm_validation.csv` cu un rând per (subject, trial, side, source)
și coloanele: rmse_deg, nrmse, pcc, dtw_dist, n_overlap, rom_omc_deg, rom_fsm_deg.

Surse comparate (toate vs. OMC):
  - "fsm"     — traiectoria comandată de FSM (ankle_controller.generate_trajectory)
  - "imu"     — unghiul real derivat din IMU (compute_ankle_angle)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from easy_gait import preprocessing, gait_events, fsm, ankle_controller, validation
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, compute_ankle_angle, load_samala_imu,
    load_samala_omc, list_samala_subjects,
)
from easy_gait.omc_events import (
    samala_c3d_path, load_c3d_markers, align_omc_to_imu,
)

SAMALA_DIR = ROOT / "data" / "raw" / "samala_2024"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "fsm_validation.csv"


def _compare(pred: np.ndarray, truth: np.ndarray) -> dict:
    rmse = validation.traj_rmse(pred, truth)
    nrmse = validation.traj_nrmse(pred, truth)
    pcc = validation.traj_pcc(pred, truth)
    return {"rmse_deg": rmse, "nrmse": nrmse, "pcc": pcc}


def process_one(subject: str, trial: int, side: str) -> list[dict]:
    rows: list[dict] = []
    try:
        g = load_samala_imu(SAMALA_DIR, subject, trial)
        df_imu = g.df
        fs = g.fs

        # OMC ankle
        omc_trials = load_samala_omc(SAMALA_DIR, subject)
        omc_key = f"Walking{trial}"
        if omc_key not in omc_trials:
            return rows
        ankle_col = f"{'L' if side.startswith('l') else 'R'}ANKLE_X"
        if ankle_col not in omc_trials[omc_key].columns:
            return rows
        ankle_omc_raw = omc_trials[omc_key][ankle_col].to_numpy()

        # Trim OMC ankle la lungime C3D (uneori CSV are mai mult)
        c3d_path = samala_c3d_path(SAMALA_DIR, subject, trial)
        if c3d_path.exists():
            data = load_c3d_markers(c3d_path)
            n_omc = data['n_frames']
            ankle_omc = ankle_omc_raw[:n_omc]
        else:
            ankle_omc = ankle_omc_raw

        # IMU ankle real
        ankle_imu = compute_ankle_angle(df_imu, side, reference_idx=100, fs=fs)
        if len(ankle_imu) < len(ankle_omc):
            return rows

        # Aliniere via cross-corr pe ankle_imu vs ankle_omc
        offset = align_omc_to_imu(ankle_imu, ankle_omc, fs, fs)

        # FSM trajectory pe IMU
        omega = preprocessing.gyro_pitch_dps(df_imu, SAMALA_SHANK_GYRO_COLS[side]['pitch'], fs=fs)
        events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=True)
        ref_idx = int(events.hs_idx[0]) if len(events.hs_idx) > 0 else 100
        ankle_real = compute_ankle_angle(df_imu, side, reference_idx=ref_idx, fs=fs)
        trace = fsm.run_fsm(
            n_samples=len(df_imu), fs=fs,
            hs_idx=events.hs_idx, to_idx=events.to_idx,
            omega_shank_dps=omega, ankle_angle_estimate_deg=ankle_real,
            config=fsm.FSMConfig(activity="level"),
        )
        ankle_fsm = ankle_controller.generate_trajectory(trace, fs=fs)

        # Fereastra IMU corespunzătoare OMC
        end = offset + len(ankle_omc)
        if end > len(ankle_fsm):
            end = len(ankle_fsm)
        n_overlap = end - offset
        if n_overlap < int(fs * 1.0):  # mai puțin de 1s overlap, skip
            return rows

        fsm_w = ankle_fsm[offset:end]
        imu_w = ankle_real[offset:end]
        omc_w = ankle_omc[:n_overlap]

        common = {
            "subject": subject,
            "trial": trial,
            "side": side,
            "n_overlap": int(n_overlap),
            "duration_s": round(n_overlap / fs, 2),
            "align_offset_s": round(offset / fs, 3),
            "rom_omc_deg": round(float(np.ptp(omc_w)), 2),
        }

        # FSM vs OMC
        m_fsm = _compare(fsm_w, omc_w)
        rows.append({
            **common, "source": "fsm",
            "rom_pred_deg": round(float(np.ptp(fsm_w)), 2),
            "rmse_deg": round(m_fsm["rmse_deg"], 2),
            "nrmse": round(m_fsm["nrmse"], 4),
            "pcc": round(m_fsm["pcc"], 3) if not np.isnan(m_fsm["pcc"]) else np.nan,
        })

        # IMU vs OMC
        m_imu = _compare(imu_w, omc_w)
        rows.append({
            **common, "source": "imu",
            "rom_pred_deg": round(float(np.ptp(imu_w)), 2),
            "rmse_deg": round(m_imu["rmse_deg"], 2),
            "nrmse": round(m_imu["nrmse"], 4),
            "pcc": round(m_imu["pcc"], 3) if not np.isnan(m_imu["pcc"]) else np.nan,
        })

    except Exception as e:
        print(f"  ERROR {subject} W{trial} {side}: {type(e).__name__}: {e}")
    return rows


def main():
    subjects = list_samala_subjects(SAMALA_DIR)
    print(f"Subiecți Samala: {len(subjects)}")
    all_rows: list[dict] = []
    n_total = len(subjects) * 5 * 2
    n_done = 0
    for subj in subjects:
        for trial in range(1, 6):
            for side in ['left', 'right']:
                rows = process_one(subj, trial, side)
                all_rows.extend(rows)
                n_done += 1
                if n_done % 30 == 0 or n_done == n_total:
                    print(f"  Progres: {n_done}/{n_total}")

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("Nicio linie.")
        return
    df.to_csv(OUT_PATH, index=False)
    print(f"\nSalvat: {OUT_PATH} ({len(df)} rânduri)")

    for src in ["fsm", "imu"]:
        sub = df[df["source"] == src]
        if sub.empty:
            continue
        print(f"\n=== Sumar {src.upper()} vs OMC (toate trial-uri & subiecți & laturi) ===")
        print(f"  RMSE: {sub['rmse_deg'].mean():.2f} ± {sub['rmse_deg'].std():.2f} ° "
              f"(median {sub['rmse_deg'].median():.2f})")
        print(f"  NRMSE: {sub['nrmse'].mean():.3f} ± {sub['nrmse'].std():.3f} "
              f"(median {sub['nrmse'].median():.3f})")
        print(f"  PCC: {sub['pcc'].mean():.3f} ± {sub['pcc'].std():.3f} "
              f"(median {sub['pcc'].median():.3f})")
        print(f"  ROM OMC mean: {sub['rom_omc_deg'].mean():.1f}°, ROM pred: {sub['rom_pred_deg'].mean():.1f}°")


if __name__ == "__main__":
    main()
