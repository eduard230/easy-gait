"""Validare FSM — VERSIUNEA ÎMBUNĂTĂȚITĂ (v2).

Față de `validate_fsm_all.py` (care raporta doar RMSE/PCC punct-cu-punct FSM-vs-OMC,
metrică nepotrivită pentru un controller de impedanță), adaugă DOUĂ metode corecte
din literatură:

A. VALIDARE PE FORMĂ DE PROFIL (Sup/Goldfarb, Perry & Burnfield):
   - Se construiește profilul mediu + banda ±1SD a unghiului gleznei pe piciorul
     INTACT (referință fiziologică), din OMC, normalizat 0-100% gait cycle.
   - Se compară FORMA profilului comandat de FSM (normalizat) cu această bandă:
     % acoperire ±1SD/±2SD, corelație de formă, RMSE pe profil mediu, potrivirea
     timingului push-off (plantarflexie maximă).

B. BUCLA DE IMPEDANȚĂ (θ_obs = θ_eq + M_GRF/K):
   - Se simulează unghiul OBSERVAT al gleznei din echilibrul de impedanță FSM +
     momentul extern produs de GRF normativ, scalat la greutatea reală a
     subiectului (samala_metadata.weight_kg).
   - Acesta se compară cu OMC prin RMSE/PCC — comparație fizic corectă (spre
     deosebire de θ_eq brut).

Output: `data/processed/fsm_validation_v2.csv`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from easy_gait import preprocessing, gait_events, fsm, ankle_controller as ac, validation
from easy_gait import gait_profile as gp
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, compute_ankle_angle, load_samala_imu,
    load_samala_omc, list_samala_subjects,
)
from easy_gait.omc_events import samala_c3d_path, load_c3d_markers, align_omc_to_imu
from easy_gait.samala_metadata import get_meta

SAMALA_DIR = ROOT / "data" / "raw" / "samala_2024"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "fsm_validation_v2.csv"
PROFILE_PATH = OUT_DIR / "intact_ankle_profile.csv"


def intact_side(subject: str) -> str:
    """Piciorul intact = opusul celui amputat."""
    amp = get_meta(subject).amputated_side
    return "right" if amp == "left" else "left"


def load_trial(subject, trial, side):
    """Încarcă (ankle_omc aliniat la IMU frame, omega, df_imu, fs, hs/to events) sau None."""
    g = load_samala_imu(SAMALA_DIR, subject, trial)
    df_imu, fs = g.df, g.fs
    omc_trials = load_samala_omc(SAMALA_DIR, subject)
    omc_key = f"Walking{trial}"
    if omc_key not in omc_trials:
        return None
    ankle_col = f"{'L' if side.startswith('l') else 'R'}ANKLE_X"
    if ankle_col not in omc_trials[omc_key].columns:
        return None
    ankle_omc_raw = omc_trials[omc_key][ankle_col].to_numpy()
    c3d_path = samala_c3d_path(SAMALA_DIR, subject, trial)
    n_omc = load_c3d_markers(c3d_path)['n_frames'] if c3d_path.exists() else len(ankle_omc_raw)
    ankle_omc = ankle_omc_raw[:n_omc]

    ankle_imu = compute_ankle_angle(df_imu, side, reference_idx=100, fs=fs)
    if len(ankle_imu) < len(ankle_omc):
        return None
    offset = align_omc_to_imu(ankle_imu, ankle_omc, fs, fs)

    omega = preprocessing.gyro_pitch_dps(df_imu, SAMALA_SHANK_GYRO_COLS[side]['pitch'], fs=fs)
    events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=True)
    return dict(df_imu=df_imu, fs=fs, ankle_omc=ankle_omc, offset=offset,
                omega=omega, events=events)


# ─── PASUL 1: profil mediu + bandă ±1SD pe picioarele INTACTE (din OMC) ──────────
def build_intact_band(subjects):
    """Agregă toate ciclurile OMC ale picioarelor intacte → MeanProfile fiziologic."""
    all_cycles = []
    for subj in subjects:
        side = intact_side(subj)
        for trial in range(1, 6):
            try:
                d = load_trial(subj, trial, side)
                if d is None:
                    continue
                # evenimente HS pe OMC, în propriul frame (offset doar pt IMU)
                # Folosim HS detectați pe IMU dar mapăm pe OMC: mai simplu — folosim
                # ankle_omc și detectăm cicluri prin HS-uri OMC via Zeni.
                from easy_gait.omc_events import detect_omc_events_from_c3d
                c3d = samala_c3d_path(SAMALA_DIR, subj, trial)
                omc_ev = detect_omc_events_from_c3d(c3d, side)
                if len(omc_ev.hs_idx) < 2:
                    continue
                cyc = gp.cycles_from_events(d["ankle_omc"], omc_ev.hs_idx)
                all_cycles.extend(cyc)
            except Exception:
                continue
    prof = gp.build_mean_profile(all_cycles)
    return prof


def process_one(subject, trial, side, intact_band):
    rows = []
    try:
        d = load_trial(subject, trial, side)
        if d is None:
            return rows
        df_imu, fs = d["df_imu"], d["fs"]
        ankle_omc, offset, omega, events = d["ankle_omc"], d["offset"], d["omega"], d["events"]

        ref_idx = int(events.hs_idx[0]) if len(events.hs_idx) > 0 else 100
        ankle_real = compute_ankle_angle(df_imu, side, reference_idx=ref_idx, fs=fs)
        trace = fsm.run_fsm(
            n_samples=len(df_imu), fs=fs, hs_idx=events.hs_idx, to_idx=events.to_idx,
            omega_shank_dps=omega, ankle_angle_estimate_deg=ankle_real,
            config=fsm.FSMConfig(activity="level"),
        )
        theta_eq = ac.generate_trajectory(trace, fs=fs)  # echilibru comandat

        # ── B. Bucla de impedanță: θ_obs = θ_eq + M_GRF/K ──
        weight_n = get_meta(subject).weight_kg * 9.80665
        phase = ac.phase_from_states(trace.state_per_sample, events.hs_idx, len(df_imu))
        theta_obs = ac.observed_angle_from_impedance(
            theta_eq, phase, body_weight_n=weight_n,
            stiffness_nm_per_deg=3.0, moment_arm_m=0.06,
        )

        # Fereastra de overlap cu OMC
        end = min(offset + len(ankle_omc), len(theta_eq))
        n_overlap = end - offset
        if n_overlap < int(fs * 1.0):
            return rows
        omc_w = ankle_omc[:n_overlap]
        common = {
            "subject": subject, "trial": trial, "side": side,
            "n_overlap": int(n_overlap), "duration_s": round(n_overlap / fs, 2),
            "rom_omc_deg": round(float(np.ptp(omc_w)), 2),
        }

        def cmp_block(pred_full, src):
            w = pred_full[offset:end]
            return {**common, "source": src,
                    "rom_pred_deg": round(float(np.ptp(w)), 2),
                    "rmse_deg": round(validation.traj_rmse(w, omc_w), 2),
                    "nrmse": round(validation.traj_nrmse(w, omc_w), 4),
                    "pcc": _r(validation.traj_pcc(w, omc_w), 3)}

        # comparațiile punct-cu-punct (vechi + nou)
        rows.append(cmp_block(theta_eq, "fsm_eq"))        # echilibru brut (ca v1 "fsm")
        rows.append(cmp_block(ankle_real, "imu"))          # unghi IMU (ca v1)
        rows.append(cmp_block(theta_obs, "fsm_impedance")) # NOU: bucla de impedanță

        # ── A. Validare pe formă de profil (FSM eq normalizat vs banda intact) ──
        if intact_band is not None and len(events.hs_idx) >= 2:
            cyc_fsm = gp.cycles_from_events(theta_eq, events.hs_idx)
            prof_fsm = gp.build_mean_profile(cyc_fsm)
            if prof_fsm is not None:
                sm = gp.profile_shape_metrics(prof_fsm.mean, intact_band)
                rows.append({**common, "source": "fsm_profile_shape",
                             "rom_pred_deg": round(float(np.ptp(prof_fsm.mean)), 2),
                             "coverage_1sd_pct": round(sm.coverage_1sd_pct, 1),
                             "coverage_2sd_pct": round(sm.coverage_2sd_pct, 1),
                             "profile_rmse_deg": round(sm.profile_rmse_deg, 2),
                             "shape_pcc": _r(sm.shape_pcc, 3),
                             "pushoff_pct_fsm": round(sm.pushoff_pct_cand, 1),
                             "pushoff_pct_intact": round(sm.pushoff_pct_ref, 1),
                             "pushoff_timing_err_pct": round(sm.pushoff_timing_err_pct, 1)})
    except Exception as e:
        print(f"  ERROR {subject} W{trial} {side}: {type(e).__name__}: {e}")
    return rows


def _r(x, nd=2):
    return round(float(x), nd) if x is not None and not (isinstance(x, float) and np.isnan(x)) else np.nan


def main():
    subjects = list_samala_subjects(SAMALA_DIR)
    print(f"Subiecți: {len(subjects)}")

    print("PASUL 1: construiesc banda ±1SD a profilului INTACT (OMC)...")
    intact_band = build_intact_band(subjects)
    if intact_band is not None:
        print(f"  Profil intact: {intact_band.n_cycles} cicluri agregate.")
        pd.DataFrame({"pct": intact_band.pct, "mean_deg": intact_band.mean,
                      "sd_deg": intact_band.sd}).to_csv(PROFILE_PATH, index=False)
        print(f"  Salvat profil: {PROFILE_PATH}")
    else:
        print("  ATENȚIE: nu s-a putut construi banda intact.")

    print("PASUL 2: validare per trial (protetic — comandat de FSM)...")
    rows = []
    n_total, n_done = len(subjects) * 5 * 2, 0
    for subj in subjects:
        side = get_meta(subj).amputated_side  # validăm pe piciorul PROTETIC
        for trial in range(1, 6):
            rows.extend(process_one(subj, trial, side, intact_band))
            n_done += 1
            if n_done % 30 == 0:
                print(f"  {n_done}/{len(subjects)*5}")
    df = pd.DataFrame(rows)
    if df.empty:
        print("Nicio linie."); return
    df.to_csv(OUT_PATH, index=False)
    print(f"\nSalvat: {OUT_PATH} ({len(df)} rânduri)")

    print("\n=== COMPARAȚIE PUNCT-CU-PUNCT vs OMC ===")
    for src in ["fsm_eq", "fsm_impedance", "imu"]:
        s = df[df.source == src]
        if s.empty:
            continue
        print(f"  {src:15s}: RMSE {s.rmse_deg.mean():5.2f}° | NRMSE {s.nrmse.mean():.3f} | "
              f"PCC {s.pcc.mean():+.3f} | ROM pred {s.rom_pred_deg.mean():.1f}° (OMC {s.rom_omc_deg.mean():.1f}°)")

    sp = df[df.source == "fsm_profile_shape"]
    if not sp.empty:
        print("\n=== VALIDARE PE FORMĂ DE PROFIL (FSM comandat vs banda intact ±1SD) ===")
        print(f"  Acoperire ±1SD: {sp.coverage_1sd_pct.mean():.0f}%  |  ±2SD: {sp.coverage_2sd_pct.mean():.0f}%")
        print(f"  Corelație de formă (shape PCC): {sp.shape_pcc.mean():+.3f}")
        print(f"  Timing push-off — eroare: {sp.pushoff_timing_err_pct.mean():.0f}% gait cycle "
              f"(FSM {sp.pushoff_pct_fsm.mean():.0f}% vs intact {sp.pushoff_pct_intact.mean():.0f}%)")


if __name__ == "__main__":
    main()
