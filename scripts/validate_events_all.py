"""Validare HS/TO IMU vs. OMC ground truth (Zeni 2008) pe TOȚI subiecții Samala.

Output: `data/processed/events_validation.csv` cu un rând per (subject, trial, side, algorithm)
și coloanele: hs_mae_ms, hs_sens, hs_ppv, hs_f1, to_mae_ms, to_sens, to_ppv, to_f1,
plus n_omc_events, n_imu_events, align_offset_s.

Algoritmi testați: Trojaniello (offline) și Maqbool (real-time).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from easy_gait import preprocessing, gait_events, validation
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS,
    compute_ankle_angle, load_samala_imu,
    load_samala_omc, list_samala_subjects, accel_magnitude,
)
from easy_gait.omc_events import (
    detect_omc_events_from_c3d, samala_c3d_path, align_omc_to_imu,
)

SAMALA_DIR = ROOT / "data" / "raw" / "samala_2024"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "events_validation.csv"

TOL_HS_MS = 150.0   # tolerance, Pacini Panebianco 2018: 50-150 ms acceptable for IC
TOL_TO_MS = 150.0   # idem pentru TO


def process_one(subject: str, trial: int, side: str) -> list[dict]:
    """Procesează un trial pe o latură; întoarce 2 rânduri (Trojaniello + Maqbool)."""
    rows: list[dict] = []
    try:
        g = load_samala_imu(SAMALA_DIR, subject, trial)
        df_imu = g.df
        fs = g.fs

        # OMC events ground truth
        omc_path = samala_c3d_path(SAMALA_DIR, subject, trial)
        if not omc_path.exists():
            return rows
        omc_ev = detect_omc_events_from_c3d(omc_path, side)
        if len(omc_ev.hs_idx) < 2 or len(omc_ev.to_idx) < 2:
            return rows
        if fs != omc_ev.fs:
            # Skipăm — fs diferit nesuportat (Samala ambele 200 Hz)
            return rows

        # Aliniere via cross-corr pe ankle (IMU vs OMC, ambele unghi în grade,
        # convenție identică dorsi(+)/plantar(-)). Cea mai robustă metodă.
        ankle_imu = compute_ankle_angle(df_imu, side, reference_idx=100, fs=fs)
        try:
            omc_trials = load_samala_omc(SAMALA_DIR, subject)
            omc_key = f"Walking{trial}"
            if omc_key not in omc_trials:
                return rows
            ankle_col = f"{'L' if side.startswith('l') else 'R'}ANKLE_X"
            ankle_omc = omc_trials[omc_key][ankle_col].to_numpy()
            # Trim to OMC event length (sometimes CSV is longer than C3D)
            n_omc = omc_ev.n_frames
            ankle_omc = ankle_omc[:n_omc]
        except Exception:
            return rows

        if len(ankle_omc) >= len(ankle_imu):
            align_offset = 0
        else:
            align_offset = align_omc_to_imu(
                imu_signal=ankle_imu,
                omc_signal=ankle_omc,
                fs_imu=fs, fs_omc=omc_ev.fs,
            )

        # OMC events in IMU frame coordinates:
        omc_hs_in_imu = omc_ev.hs_idx + align_offset
        omc_to_in_imu = omc_ev.to_idx + align_offset

        # Algoritmi IMU
        omega = preprocessing.gyro_pitch_dps(df_imu, SAMALA_SHANK_GYRO_COLS[side]['pitch'], fs=fs)
        is_prosthetic = True  # validăm cu prag relaxat (lot mixt — pe sigur)

        # Trojaniello
        ev_tro = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=is_prosthetic)
        m_hs_tro = validation.event_mae(ev_tro.hs_idx, omc_hs_in_imu, fs=fs, tol_ms=TOL_HS_MS)
        m_to_tro = validation.event_mae(ev_tro.to_idx, omc_to_in_imu, fs=fs, tol_ms=TOL_TO_MS)

        # Maqbool
        ev_maq = None
        m_hs_maq = {"mae_ms": np.nan, "sens": np.nan, "ppv": np.nan, "f1": np.nan, "n_matched": 0}
        m_to_maq = {"mae_ms": np.nan, "sens": np.nan, "ppv": np.nan, "f1": np.nan, "n_matched": 0}
        try:
            accel_cols = SAMALA_SHANK_ACCEL_COLS[side]
            accel_mag = accel_magnitude(df_imu, accel_cols)
            ev_maq = gait_events.detect_events_maqbool(
                shank_pitch_rate=omega, shank_accel_mag=accel_mag,
                fs=fs, prosthetic=is_prosthetic,
            )
            m_hs_maq = validation.event_mae(ev_maq.hs_idx, omc_hs_in_imu, fs=fs, tol_ms=TOL_HS_MS)
            m_to_maq = validation.event_mae(ev_maq.to_idx, omc_to_in_imu, fs=fs, tol_ms=TOL_TO_MS)
        except Exception as exc:
            print(f"  Maqbool err {subject} W{trial} {side}: {exc}")

        common = {
            "subject": subject,
            "trial": trial,
            "side": side,
            "align_offset_s": round(align_offset / fs, 3),
            "n_omc_hs": int(len(omc_ev.hs_idx)),
            "n_omc_to": int(len(omc_ev.to_idx)),
        }

        rows.append({
            **common,
            "algorithm": "Trojaniello",
            "n_imu_hs": int(len(ev_tro.hs_idx)),
            "n_imu_to": int(len(ev_tro.to_idx)),
            "hs_mae_ms": round(m_hs_tro["mae_ms"], 1) if not np.isnan(m_hs_tro["mae_ms"]) else np.nan,
            "hs_sens": round(m_hs_tro["sens"], 3),
            "hs_ppv": round(m_hs_tro["ppv"], 3),
            "hs_f1": round(m_hs_tro["f1"], 3),
            "to_mae_ms": round(m_to_tro["mae_ms"], 1) if not np.isnan(m_to_tro["mae_ms"]) else np.nan,
            "to_sens": round(m_to_tro["sens"], 3),
            "to_ppv": round(m_to_tro["ppv"], 3),
            "to_f1": round(m_to_tro["f1"], 3),
        })
        rows.append({
            **common,
            "algorithm": "Maqbool",
            "n_imu_hs": int(len(ev_maq.hs_idx)) if ev_maq is not None else 0,
            "n_imu_to": int(len(ev_maq.to_idx)) if ev_maq is not None else 0,
            "hs_mae_ms": round(m_hs_maq["mae_ms"], 1) if not np.isnan(m_hs_maq["mae_ms"]) else np.nan,
            "hs_sens": round(m_hs_maq["sens"], 3) if not np.isnan(m_hs_maq["sens"]) else np.nan,
            "hs_ppv": round(m_hs_maq["ppv"], 3) if not np.isnan(m_hs_maq["ppv"]) else np.nan,
            "hs_f1": round(m_hs_maq["f1"], 3) if not np.isnan(m_hs_maq["f1"]) else np.nan,
            "to_mae_ms": round(m_to_maq["mae_ms"], 1) if not np.isnan(m_to_maq["mae_ms"]) else np.nan,
            "to_sens": round(m_to_maq["sens"], 3) if not np.isnan(m_to_maq["sens"]) else np.nan,
            "to_ppv": round(m_to_maq["ppv"], 3) if not np.isnan(m_to_maq["ppv"]) else np.nan,
            "to_f1": round(m_to_maq["f1"], 3) if not np.isnan(m_to_maq["f1"]) else np.nan,
        })
    except Exception as e:
        print(f"  ERROR {subject} W{trial} {side}: {type(e).__name__}: {e}")
    return rows


def main():
    subjects = list_samala_subjects(SAMALA_DIR)
    print(f"Subiecți Samala: {len(subjects)}")
    all_rows: list[dict] = []
    n_total = len(subjects) * 5 * 2  # subjects × trials × sides
    n_done = 0
    for subj in subjects:
        for trial in range(1, 6):
            for side in ['left', 'right']:
                rows = process_one(subj, trial, side)
                all_rows.extend(rows)
                n_done += 1
                if n_done % 30 == 0 or n_done == n_total:
                    print(f"  Progres: {n_done}/{n_total} ({100*n_done/n_total:.0f}%)")

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("Nicio linie de rezultate.")
        return
    df.to_csv(OUT_PATH, index=False)
    print(f"\nSalvat: {OUT_PATH} ({len(df)} rânduri)")

    # Sumar
    print("\n=== Sumar Trojaniello ===")
    sub = df[df["algorithm"] == "Trojaniello"]
    print(f"  HS MAE: {sub['hs_mae_ms'].mean():.1f} ± {sub['hs_mae_ms'].std():.1f} ms"
          f" (median {sub['hs_mae_ms'].median():.1f})")
    print(f"  HS sens: {sub['hs_sens'].mean():.3f}")
    print(f"  TO MAE: {sub['to_mae_ms'].mean():.1f} ± {sub['to_mae_ms'].std():.1f} ms"
          f" (median {sub['to_mae_ms'].median():.1f})")
    print(f"  TO sens: {sub['to_sens'].mean():.3f}")
    print("\n=== Sumar Maqbool ===")
    sub = df[df["algorithm"] == "Maqbool"]
    print(f"  HS MAE: {sub['hs_mae_ms'].mean():.1f} ± {sub['hs_mae_ms'].std():.1f} ms"
          f" (median {sub['hs_mae_ms'].median():.1f})")
    print(f"  HS sens: {sub['hs_sens'].mean():.3f}")
    print(f"  TO MAE: {sub['to_mae_ms'].mean():.1f} ± {sub['to_mae_ms'].std():.1f} ms"
          f" (median {sub['to_mae_ms'].median():.1f})")
    print(f"  TO sens: {sub['to_sens'].mean():.3f}")


if __name__ == "__main__":
    main()
