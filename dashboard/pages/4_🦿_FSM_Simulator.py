"""Pagina 4 — Simulator FSM control gleznă protetică."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from _shared import (
    header, list_samala_subjects_cached, load_samala_imu_cached, SAMALA_DIR,
)
from easy_gait import preprocessing, gait_events, segmentation, fsm, ankle_controller, validation
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS,
    accel_magnitude, detect_prosthetic_side, compute_ankle_angle,
)

header("FSM Simulator — Control gleznă protetică", icon="🦿")

st.markdown(
    "Rulează FSM cu 5 stări (Loading → Mid-Stance → Push-Off → Early Swing → Late Swing), "
    "generează traiectoria de referință pentru unghi gleznă și compară cu unghiul real "
    "măsurat (din IMU Noraxon-Joints-Ankle)."
)

subjects = list_samala_subjects_cached()
c1, c2, c3, c4 = st.columns(4)
subject = c1.selectbox("Subiect", subjects)
trial = c2.selectbox("Trial", [1, 2, 3, 4, 5])
activity = c3.selectbox("Activitate", list(fsm.SETPOINTS.keys()), index=0)
method = c4.selectbox("Detecție evenimente", ["Trojaniello", "Maqbool"])

df, fs, _meta = load_samala_imu_cached(subject, trial)
prost = detect_prosthetic_side(df)
intact = "right" if prost == "left" else "left"

side = st.radio("Picior simulat", [intact, prost], horizontal=True,
                  format_func=lambda s: f"{s.upper()} ({'INTACT' if s == intact else 'PROTETIC'})")
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

# Metrice
rmse = validation.traj_rmse(traj, ankle_real)
nrmse = validation.traj_nrmse(traj, ankle_real)
pcc = validation.traj_pcc(traj, ankle_real)
m1, m2, m3, m4 = st.columns(4)
m1.metric("RMSE [°]", f"{rmse:.2f}", help="țintă < 5° (Bartlett 2021)")
m2.metric("NRMSE [%]", f"{nrmse*100:.1f}", help="țintă < 15%")
m3.metric("PCC", f"{pcc:.3f}", help="țintă > 0.90")
m4.metric("Cicluri", len(segmentation.reject_outliers(segmentation.build_cycles(events))))

fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    subplot_titles=("FSM state per sample", "Setpoint discret și traiectorie continuă",
                    "Comparație unghi gleznă: traiectorie generată vs. unghi real (IMU joint)"),
    row_heights=[0.2, 0.4, 0.4],
)
fig.add_trace(go.Scatter(x=t, y=trace.state_per_sample, line=dict(color="purple", shape="hv"),
                          name="State"), row=1, col=1)
fig.update_yaxes(tickmode="array", tickvals=[1, 2, 3, 4, 5],
                  ticktext=["S1", "S2", "S3", "S4", "S5"], row=1, col=1)

fig.add_trace(go.Scatter(x=t, y=trace.setpoint_per_sample, name="Setpoint",
                          line=dict(color="gray", dash="dash", shape="hv")), row=2, col=1)
fig.add_trace(go.Scatter(x=t, y=traj, name="Traiectorie FSM (spline)",
                          line=dict(color="darkorange", width=2)), row=2, col=1)

fig.add_trace(go.Scatter(x=t, y=ankle_real, name="Unghi gleznă real (IMU joint)",
                          line=dict(color="green", width=2)), row=3, col=1)
fig.add_trace(go.Scatter(x=t, y=traj, name="Traiectorie FSM",
                          line=dict(color="darkorange", dash="dot", width=1.5)), row=3, col=1)

fig.update_layout(height=750, showlegend=True,
                   yaxis2_title="Unghi (°)", yaxis3_title="Unghi (°)",
                   xaxis3_title="Timp (s)")
st.plotly_chart(fig, use_container_width=True)

# Setpoint table
st.subheader("Setpoint-uri FSM curente (deg)")
import pandas as pd
sp_df = pd.DataFrame({s.name: [round(v, 1)] for s, v in fsm.SETPOINTS[activity].items()})
sp_df.index = [f"activitate: {activity}"]
st.dataframe(sp_df, use_container_width=True)
