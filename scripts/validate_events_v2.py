"""Validare HS/TO IMU vs. OMC — VERSIUNEA ÎMBUNĂTĂȚITĂ (v2).

Față de `validate_events_all.py`, adaugă trei corecții metodologice care elimină
artefacte de comparație (NU truchează rezultatele):

1. EVALUARE PE FEREASTRA OMC: evenimentele IMU sunt restrânse la intervalul
   acoperit de OMC (~4.5 s) înainte de matching. Elimină fals-pozitivele
   artificiale (evenimente IMU reale din afara ferestrei OMC) care prăbușeau PPV.
2. CORECȚIE DE BIAS: se raportează și MAE după scăderea biasului median dintre
   definiția IMU și definiția Zeni-OMC (practică standard de calibrare).
3. RAPORTARE ONESTĂ: păstrează și metricile „raw" (full-trial) alături de cele
   windowed, ca diferența să fie transparentă.

Output: `data/processed/events_validation_v2.csv`.
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
    compute_ankle_angle, load_samala_imu, load_samala_omc,
    list_samala_subjects, accel_magnitude,
)
from easy_gait.omc_events import (
    detect_omc_events_from_c3d, samala_c3d_path, align_omc_to_imu,
)

SAMALA_DIR = ROOT / "data" / "raw" / "samala_2024"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "events_validation_v2.csv"

TOL_HS_MS = 150.0
TOL_TO_MS = 150.0


def _metrics_pair(det_idx, truth_in_imu, fs):
    """Întoarce (raw, windowed+debias) pentru un set de evenimente."""
    raw = validation.event_mae(det_idx, truth_in_imu, fs=fs, tol_ms=TOL_HS_MS)
    win = validation.event_mae_windowed(
        det_idx, truth_in_imu, fs=fs, tol_ms=TOL_HS_MS, debias=True
    )
    return raw, win


def process_one(subject: str, trial: int, side: str) -> list[dict]:
    rows: list[dict] = []
    try:
        g = load_samala_imu(SAMALA_DIR, subject, trial)
        df_imu, fs = g.df, g.fs

        omc_path = samala_c3d_path(SAMALA_DIR, subject, trial)
        if not omc_path.exists():
            return rows
        omc_ev = detect_omc_events_from_c3d(omc_path, side)
        if len(omc_ev.hs_idx) < 2 or len(omc_ev.to_idx) < 2 or fs != omc_ev.fs:
            return rows

        ankle_imu = compute_ankle_angle(df_imu, side, reference_idx=100, fs=fs)
        try:
            omc_trials = load_samala_omc(SAMALA_DIR, subject)
            omc_key = f"Walking{trial}"
            if omc_key not in omc_trials:
                return rows
            ankle_col = f"{'L' if side.startswith('l') else 'R'}ANKLE_X"
            ankle_omc = omc_trials[omc_key][ankle_col].to_numpy()[:omc_ev.n_frames]
        except Exception:
            return rows

        align_offset = (0 if len(ankle_omc) >= len(ankle_imu)
                        else align_omc_to_imu(ankle_imu, ankle_omc, fs, omc_ev.fs))
        omc_hs_in_imu = omc_ev.hs_idx + align_offset
        omc_to_in_imu = omc_ev.to_idx + align_offset

        omega = preprocessing.gyro_pitch_dps(df_imu, SAMALA_SHANK_GYRO_COLS[side]['pitch'], fs=fs)

        for alg, ev in [
            ("Trojaniello", gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=True)),
            ("Maqbool", gait_events.detect_events_maqbool(
                omega, accel_magnitude(df_imu, SAMALA_SHANK_ACCEL_COLS[side]),
                fs=fs, prosthetic=True)),
        ]:
            hs_raw, hs_win = _metrics_pair(ev.hs_idx, omc_hs_in_imu, fs)
            to_raw, to_win = _metrics_pair(ev.to_idx, omc_to_in_imu, fs)
            rows.append({
                "subject": subject, "trial": trial, "side": side, "algorithm": alg,
                "align_offset_s": round(align_offset / fs, 3),
                "n_omc_hs": int(len(omc_ev.hs_idx)), "n_imu_hs": int(len(ev.hs_idx)),
                "n_imu_hs_in_window": hs_win["n_detected_in_window"],
                # RAW (full trial) — ca în v1, pentru transparență
                "hs_mae_raw_ms": _r(hs_raw["mae_ms"]), "hs_sens_raw": _r(hs_raw["sens"], 3),
                "hs_ppv_raw": _r(hs_raw["ppv"], 3), "hs_f1_raw": _r(hs_raw["f1"], 3),
                "to_mae_raw_ms": _r(to_raw["mae_ms"]), "to_sens_raw": _r(to_raw["sens"], 3),
                "to_ppv_raw": _r(to_raw["ppv"], 3), "to_f1_raw": _r(to_raw["f1"], 3),
                # WINDOWED (pe fereastra OMC) — comparație corectă
                "hs_mae_win_ms": _r(hs_win["mae_ms"]), "hs_bias_ms": _r(hs_win["bias_ms"]),
                "hs_mae_debiased_ms": _r(hs_win["mae_debiased_ms"]),
                "hs_sens_win": _r(hs_win["sens"], 3), "hs_ppv_win": _r(hs_win["ppv"], 3),
                "hs_f1_win": _r(hs_win["f1"], 3),
                "to_mae_win_ms": _r(to_win["mae_ms"]), "to_bias_ms": _r(to_win["bias_ms"]),
                "to_mae_debiased_ms": _r(to_win["mae_debiased_ms"]),
                "to_sens_win": _r(to_win["sens"], 3), "to_ppv_win": _r(to_win["ppv"], 3),
                "to_f1_win": _r(to_win["f1"], 3),
            })
    except Exception as e:
        print(f"  ERROR {subject} W{trial} {side}: {type(e).__name__}: {e}")
    return rows


def _r(x, nd=1):
    return round(float(x), nd) if x is not None and not (isinstance(x, float) and np.isnan(x)) else np.nan


def main():
    subjects = list_samala_subjects(SAMALA_DIR)
    print(f"Subiecți: {len(subjects)}")
    rows = []
    n_total, n_done = len(subjects) * 5 * 2, 0
    for subj in subjects:
        for trial in range(1, 6):
            for side in ["left", "right"]:
                rows.extend(process_one(subj, trial, side))
                n_done += 1
                if n_done % 60 == 0 or n_done == n_total:
                    print(f"  {n_done}/{n_total}")
    df = pd.DataFrame(rows)
    if df.empty:
        print("Nicio linie."); return
    df.to_csv(OUT_PATH, index=False)
    print(f"\nSalvat: {OUT_PATH} ({len(df)} rânduri)")

    for alg in ["Trojaniello", "Maqbool"]:
        s = df[df.algorithm == alg]
        print(f"\n=== {alg} — RAW vs WINDOWED vs DEBIASED ===")
        print(f"  HS sens: raw {s.hs_sens_raw.mean():.3f} → win {s.hs_sens_win.mean():.3f}")
        print(f"  HS PPV : raw {s.hs_ppv_raw.mean():.3f} → win {s.hs_ppv_win.mean():.3f}")
        print(f"  HS F1  : raw {s.hs_f1_raw.mean():.3f} → win {s.hs_f1_win.mean():.3f}")
        print(f"  HS MAE : raw {s.hs_mae_raw_ms.mean():.1f} → win {s.hs_mae_win_ms.mean():.1f} → debiased {s.hs_mae_debiased_ms.mean():.1f} ms (bias {s.hs_bias_ms.mean():+.1f})")
        print(f"  TO sens: raw {s.to_sens_raw.mean():.3f} → win {s.to_sens_win.mean():.3f}")
        print(f"  TO PPV : raw {s.to_ppv_raw.mean():.3f} → win {s.to_ppv_win.mean():.3f}")
        print(f"  TO F1  : raw {s.to_f1_raw.mean():.3f} → win {s.to_f1_win.mean():.3f}")
        print(f"  TO MAE : raw {s.to_mae_raw_ms.mean():.1f} → win {s.to_mae_win_ms.mean():.1f} → debiased {s.to_mae_debiased_ms.mean():.1f} ms (bias {s.to_bias_ms.mean():+.1f})")


if __name__ == "__main__":
    main()
