"""Pagina 4 — Simulator FSM control gleznă protetică."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from _shared import (
    header, list_samala_subjects_cached, load_samala_imu_cached, SAMALA_DIR, ROOT,
)
from easy_gait import (
    preprocessing, gait_events, segmentation, fsm, ankle_controller, validation,
    gait_profile,
)
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS,
    accel_magnitude, detect_prosthetic_side, compute_ankle_angle,
)


@st.cache_data(show_spinner=False)
def _load_intact_band():
    """Profilul fiziologic intact (±1SD) generat de scripts/validate_fsm_v2.py."""
    import pandas as pd
    p = ROOT / "data" / "processed" / "intact_ankle_profile.csv"
    if not p.exists():
        return None
    return pd.read_csv(p)

header("Simulator FSM")
st.caption(
    "Controlul de gleznă cu cinci stări generează un unghi de referință de-a lungul "
    "pasului. Graficele compară acest unghi comandat cu cel măsurat pe subiect."
)

subjects = list_samala_subjects_cached()
c1, c2, c3, c4 = st.columns(4)
subject = c1.selectbox("Subiect", subjects)
trial = c2.selectbox("Proba", [1, 2, 3, 4, 5])
activity = c3.selectbox("Activitate", list(fsm.SETPOINTS.keys()), index=0)
method = c4.selectbox("Detecție evenimente", ["Trojaniello", "Maqbool"])

df, fs, _meta = load_samala_imu_cached(subject, trial)
prost = detect_prosthetic_side(df)
intact = "right" if prost == "left" else "left"

side = st.radio("Picior simulat", [intact, prost], horizontal=True,
                  format_func=lambda s: f"{s.upper()} ({'intact' if s == intact else 'protetic'})")
is_prost = (side == prost)

pitch_col = SAMALA_SHANK_GYRO_COLS[side]["pitch"]
omega = preprocessing.gyro_pitch_dps(df, pitch_col, fs=fs)
amag = accel_magnitude(df, SAMALA_SHANK_ACCEL_COLS[side])

if method == "Trojaniello":
    events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=is_prost)
else:
    events = gait_events.detect_events_maqbool(omega, amag, fs=fs, prosthetic=is_prost)

# Calibrăm ankle = 0° la primul HS detectat (convenția clinică Perry & Burnfield)
ref_idx = int(events.hs_idx[0]) if len(events.hs_idx) > 0 else 100
ankle_real = compute_ankle_angle(df, side, reference_idx=ref_idx)

trace = fsm.run_fsm(
    n_samples=len(df), fs=fs,
    hs_idx=events.hs_idx, to_idx=events.to_idx,
    omega_shank_dps=omega, ankle_angle_estimate_deg=ankle_real,
    config=fsm.FSMConfig(activity=activity),
)
traj = ankle_controller.generate_trajectory(trace, fs=fs)
t = np.arange(len(df)) / fs

# ── NOU (v2): bucla de impedanță — unghiul OBSERVAT din θ_eq + M_GRF/K ──
# Setpoint-urile FSM sunt echilibre de impedanță, nu unghiuri observate. Unghiul
# fizic real rezultă din complianța gleznei sub momentul GRF (Sup/Goldfarb 2008).
try:
    from easy_gait.samala_metadata import get_meta as _samala_meta
    weight_kg = float(_samala_meta(subject).weight_kg)
except Exception:
    weight_kg = 75.0
phase_pct = ankle_controller.phase_from_states(trace.state_per_sample, events.hs_idx, len(df))
traj_imp = ankle_controller.observed_angle_from_impedance(
    traj, phase_pct, body_weight_n=weight_kg * 9.80665,
    stiffness_nm_per_deg=3.0, moment_arm_m=0.06,
)

opt1, opt2 = st.columns(2)
show_impedance = opt1.toggle(
    "Afișează unghiul observat din impedanță (θ_eq + M·GRF/K)", value=True,
    help="Unghiul fizic estimat al gleznei — diferit de comanda brută. Urcă în dorsiflexie pe stance (rocker).")
show_band = opt2.toggle(
    "Suprapune banda fiziologică intactă (±1SD)", value=True,
    help="Profilul mediu al gleznei intacte (OMC), ca referință de formă.")

# Metrice — comandă brută (v1) vs impedanță (v2)
rmse = validation.traj_rmse(traj, ankle_real)
nrmse = validation.traj_nrmse(traj, ankle_real)
pcc = validation.traj_pcc(traj, ankle_real)
rmse_imp = validation.traj_rmse(traj_imp, ankle_real)
pcc_imp = validation.traj_pcc(traj_imp, ankle_real)
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("RMSE θ_eq [°]", f"{rmse:.2f}", help="comandă brută vs real — țintă < 5°")
m2.metric("PCC θ_eq", f"{pcc:.3f}", help="comandă brută — poate fi negativ (impedanță)")
m3.metric("RMSE impedanță [°]", f"{rmse_imp:.2f}",
          delta=f"{rmse_imp - rmse:+.2f}", delta_color="inverse",
          help="v2: unghi observat θ_eq+M·GRF/K vs real")
m4.metric("PCC impedanță", f"{pcc_imp:.3f}",
          delta=f"{pcc_imp - pcc:+.3f}",
          help="v2: corelația devine pozitivă când comparăm unghiul fizic")
m5.metric("Cicluri", len(segmentation.reject_outliers(segmentation.build_cycles(events))))

fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    subplot_titles=("Faza controlului în timp",
                    "Unghi de referință: țintă pe faze și traiectorie netezită",
                    "Unghi de gleznă: comandat față de cel real"),
    row_heights=[0.2, 0.4, 0.4],
)
fig.add_trace(go.Scatter(x=t, y=trace.state_per_sample, line=dict(color="purple", shape="hv"),
                          name="fază"), row=1, col=1)
fig.update_yaxes(tickmode="array", tickvals=[1, 2, 3, 4, 5],
                  ticktext=["1", "2", "3", "4", "5"], row=1, col=1)

fig.add_trace(go.Scatter(x=t, y=trace.setpoint_per_sample, name="țintă pe faze",
                          line=dict(color="gray", dash="dash", shape="hv")), row=2, col=1)
fig.add_trace(go.Scatter(x=t, y=traj, name="traiectorie netezită",
                          line=dict(color="darkorange", width=2)), row=2, col=1)

fig.add_trace(go.Scatter(x=t, y=ankle_real, name="unghi real (măsurat)",
                          line=dict(color="green", width=2)), row=3, col=1)
fig.add_trace(go.Scatter(x=t, y=traj, name="θ_eq comandat (impedanță)",
                          line=dict(color="darkorange", dash="dot", width=1.5)), row=3, col=1)

# ── NOU (v2): curba unghiului observat din bucla de impedanță ──
if show_impedance:
    fig.add_trace(go.Scatter(x=t, y=traj_imp, name="θ observat (θ_eq + M·GRF/K)",
                             line=dict(color="crimson", width=2)), row=3, col=1)

# ── NOU (v2): banda fiziologică intactă ±1SD, mapată pe fiecare ciclu detectat ──
if show_band:
    band = _load_intact_band()
    if band is not None and len(events.hs_idx) >= 2:
        pct = band["pct"].to_numpy()
        lo = (band["mean_deg"] - band["sd_deg"]).to_numpy()
        hi = (band["mean_deg"] + band["sd_deg"]).to_numpy()
        first = True
        for i in range(len(events.hs_idx) - 1):
            a, b = int(events.hs_idx[i]), int(events.hs_idx[i + 1])
            if b - a < 4:
                continue
            tc = t[a:b]
            x_cycle = np.linspace(0, 100, b - a)
            lo_c = np.interp(x_cycle, pct, lo)
            hi_c = np.interp(x_cycle, pct, hi)
            fig.add_trace(go.Scatter(
                x=np.concatenate([tc, tc[::-1]]),
                y=np.concatenate([hi_c, lo_c[::-1]]),
                fill="toself", fillcolor="rgba(44,160,44,0.15)",
                line=dict(width=0), name="bandă intact ±1SD",
                legendgroup="band", showlegend=first, hoverinfo="skip",
            ), row=3, col=1)
            first = False

fig.update_layout(height=750, showlegend=True,
                   yaxis_title="Fază", yaxis2_title="Unghi (°)", yaxis3_title="Unghi (°)",
                   xaxis3_title="Timp (s)")
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Faze: 1 — contact inițial, 2 — sprijin median, 3 — desprindere, "
    "4 — început de balans, 5 — sfârșit de balans."
)

# Tabel unghiuri-țintă
st.subheader("Unghiuri-țintă pe faze (grade)")
import pandas as pd
sp_df = pd.DataFrame({s.name: [round(v, 1)] for s, v in fsm.SETPOINTS[activity].items()})
sp_df.index = [f"activitate: {activity}"]
st.dataframe(sp_df, use_container_width=True)
