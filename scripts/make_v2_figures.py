"""Figuri pentru rezultatele îmbunătățite (v2).

1. fig_v2_events_before_after.png — PPV/F1/MAE raw vs windowed vs debiased.
2. fig_v2_fsm_profile_band.png    — profilul FSM comandat vs banda ±1SD intact.
3. fig_v2_fsm_impedance.png       — RMSE/PCC: fsm_eq vs fsm_impedance vs imu.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
FIGS = ROOT / "notebooks" / "figs"
FIGS.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
from easy_gait import gait_profile as gp
from easy_gait import gait_events, preprocessing, fsm, ankle_controller as ac
from easy_gait.io_utils import SAMALA_SHANK_GYRO_COLS, compute_ankle_angle, load_samala_imu
from easy_gait.samala_metadata import get_meta

# ── Fig 1: events before/after ──────────────────────────────────────────────
ev = pd.read_csv(PROC / "events_validation_v2.csv")
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
algs = ["Trojaniello", "Maqbool"]
x = np.arange(len(algs)); w = 0.35
for ax, (metric, raw_c, win_c, ttl) in zip(axes, [
    ("PPV", "hs_ppv_raw", "hs_ppv_win", "HS Positive Predictive Value"),
    ("F1", "hs_f1_raw", "hs_f1_win", "HS F1-score"),
]):
    raw = [ev[ev.algorithm == a][raw_c].mean() for a in algs]
    win = [ev[ev.algorithm == a][win_c].mean() for a in algs]
    ax.bar(x - w/2, raw, w, label="v1 (full trial)", color="#d62728", alpha=.8)
    ax.bar(x + w/2, win, w, label="v2 (fereastra OMC)", color="#2ca02c", alpha=.8)
    ax.set_xticks(x); ax.set_xticklabels(algs); ax.set_title(ttl); ax.legend()
    ax.set_ylim(0, 1); ax.grid(axis="y", alpha=.3)
# MAE raw vs debiased
axm = axes[2]
raw = [ev[ev.algorithm == a]["hs_mae_raw_ms"].mean() for a in algs]
deb = [ev[ev.algorithm == a]["hs_mae_debiased_ms"].mean() for a in algs]
axm.bar(x - w/2, raw, w, label="v1 (raw)", color="#d62728", alpha=.8)
axm.bar(x + w/2, deb, w, label="v2 (debiased)", color="#2ca02c", alpha=.8)
axm.axhline(50, ls="--", c="orange", label="țintă acceptabil 50 ms")
axm.axhline(25, ls="--", c="green", label="țintă strict 25 ms")
axm.set_xticks(x); axm.set_xticklabels(algs); axm.set_title("HS MAE [ms]")
axm.legend(fontsize=8); axm.grid(axis="y", alpha=.3)
fig.suptitle("Detecție evenimente HS — îmbunătățiri v2 (fereastra OMC + corecție bias)", fontweight="bold")
fig.tight_layout()
fig.savefig(FIGS / "fig_v2_events_before_after.png", dpi=130)
plt.close(fig)
print("fig_v2_events_before_after.png OK")

# ── Fig 2: FSM impedance ─────────────────────────────────────────────────────
fv = pd.read_csv(PROC / "fsm_validation_v2.csv")
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
srcs = ["fsm_eq", "fsm_impedance", "imu"]
labels = ["FSM θ_eq\n(comandă brută, v1)", "FSM impedanță\nθ_eq+M·GRF/K (v2)", "Unghi IMU"]
colors = ["#d62728", "#1f77b4", "#2ca02c"]
rmse = [fv[fv.source == s]["rmse_deg"].mean() for s in srcs]
pcc = [fv[fv.source == s]["pcc"].mean() for s in srcs]
axes[0].bar(labels, rmse, color=colors, alpha=.85)
axes[0].axhline(5, ls="--", c="green", label="țintă <5°")
axes[0].set_ylabel("RMSE [°]"); axes[0].set_title("RMSE vs OMC"); axes[0].legend(); axes[0].grid(axis="y", alpha=.3)
axes[1].bar(labels, pcc, color=colors, alpha=.85)
axes[1].axhline(0, c="k", lw=.8)
axes[1].set_ylabel("PCC"); axes[1].set_title("Corelație Pearson vs OMC")
axes[1].grid(axis="y", alpha=.3)
fig.suptitle("Validare traiectorie gleznă: bucla de impedanță corectează semnul corelației", fontweight="bold")
fig.tight_layout()
fig.savefig(FIGS / "fig_v2_fsm_impedance.png", dpi=130)
plt.close(fig)
print("fig_v2_fsm_impedance.png OK")

# ── Fig 3: profil FSM vs banda intact ────────────────────────────────────────
prof = pd.read_csv(PROC / "intact_ankle_profile.csv")
# reconstruiesc un profil FSM mediu reprezentativ (S01 protetic)
subj = "S01"; side = get_meta(subj).amputated_side
g = load_samala_imu(ROOT / "data" / "raw" / "samala_2024", subj, 1)
omega = preprocessing.gyro_pitch_dps(g.df, SAMALA_SHANK_GYRO_COLS[side]['pitch'], fs=g.fs)
events = gait_events.detect_events_trojaniello(omega, fs=g.fs, prosthetic=True)
ref_idx = int(events.hs_idx[0]) if len(events.hs_idx) else 100
ankle_real = compute_ankle_angle(g.df, side, reference_idx=ref_idx, fs=g.fs)
trace = fsm.run_fsm(n_samples=len(g.df), fs=g.fs, hs_idx=events.hs_idx, to_idx=events.to_idx,
                    omega_shank_dps=omega, ankle_angle_estimate_deg=ankle_real,
                    config=fsm.FSMConfig(activity="level"))
theta_eq = ac.generate_trajectory(trace, fs=g.fs)
cyc = gp.cycles_from_events(theta_eq, events.hs_idx)
fsm_prof = gp.build_mean_profile(cyc)

fig, ax = plt.subplots(figsize=(9, 5))
pct = prof["pct"].to_numpy()
ax.fill_between(pct, prof["mean_deg"] - prof["sd_deg"], prof["mean_deg"] + prof["sd_deg"],
                color="#2ca02c", alpha=.25, label="Intact ±1SD (OMC, 357 cicluri)")
ax.plot(pct, prof["mean_deg"], color="#2ca02c", lw=2, label="Intact mediu (referință fiziologică)")
if fsm_prof is not None:
    ax.plot(fsm_prof.pct, fsm_prof.mean, color="#d62728", lw=2, ls="--",
            label="FSM θ_eq comandat (S01 protetic)")
ax.axhline(0, c="k", lw=.6)
ax.set_xlabel("% gait cycle"); ax.set_ylabel("unghi gleznă [°] (dorsi+ / plantar−)")
ax.set_title("Validare pe FORMĂ DE PROFIL: comanda FSM (impedanță) vs banda fiziologică intactă", fontweight="bold")
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout()
fig.savefig(FIGS / "fig_v2_fsm_profile_band.png", dpi=130)
plt.close(fig)
print("fig_v2_fsm_profile_band.png OK")
print("Toate figurile v2 generate in notebooks/figs/")
