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
    preprocessing, gait_events, segmentation, fsm, ankle_controller,
)
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS,
    accel_magnitude, detect_prosthetic_side, compute_ankle_angle,
)

header("Simulator FSM")
st.caption(
    "Controlul gleznei cu cinci stări generează un unghi de referință de-a lungul "
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

cycles = segmentation.reject_outliers(segmentation.build_cycles(events))
stance_pct = float(np.mean([c.stance_pct for c in cycles])) if cycles else 0.0
m1, m2 = st.columns(2)
m1.metric("Fază de sprijin [%]", f"{stance_pct:.1f}",
          help="Procentajul mediu al ciclului petrecut în faza de sprijin (normal ~60%)")
m2.metric("Cicluri detectate", len(cycles))

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
fig.add_trace(go.Scatter(x=t, y=traj, name="unghi comandat FSM",
                          line=dict(color="darkorange", dash="dot", width=1.5)), row=3, col=1)

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
