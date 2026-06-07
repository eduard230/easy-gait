"""Pagina 2 — Detecție Heel Strike și Toe Off."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from _shared import (
    header, list_samala_subjects_cached, load_samala_imu_cached, SAMALA_DIR,
)
from easy_gait import preprocessing, gait_events, segmentation
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS, accel_magnitude,
    detect_prosthetic_side,
)

header("Detecție evenimente")
st.caption(
    "Momentele de contact (HS - Heel Strike) și de desprindere (TO - Toe Off) ale piciorului, "
    "identificate din viteza unghiulară a gambei, și ciclurile de mers rezultate."
)

subjects = list_samala_subjects_cached()
if not subjects:
    st.error("Niciun subiect disponibil.")
    st.stop()

c1, c2, c3 = st.columns(3)
subject = c1.selectbox("Subiect", subjects)
trial = c2.selectbox("Proba", [1, 2, 3, 4, 5])
method = c3.selectbox("Algoritm", ["Trojaniello", "Maqbool"])

df, fs, meta = load_samala_imu_cached(subject, trial)
prost_side = detect_prosthetic_side(df)
intact_side = "right" if prost_side == "left" else "left"

side = st.radio("Picior analizat", [intact_side, prost_side], horizontal=True,
                  format_func=lambda s: f"{s.upper()} ({'intact' if s == intact_side else 'protetic'})")
is_prost = (side == prost_side)

pitch_col = SAMALA_SHANK_GYRO_COLS[side]["pitch"]
omega = preprocessing.gyro_pitch_dps(df, pitch_col, fs=fs)
amag = accel_magnitude(df, SAMALA_SHANK_ACCEL_COLS[side])
t = np.arange(len(df)) / fs

if method == "Trojaniello":
    events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=is_prost)
else:
    events = gait_events.detect_events_maqbool(omega, amag, fs=fs, prosthetic=is_prost)

c1, c2, c3 = st.columns(3)
c1.metric("Contacte detectate (HS)", len(events.hs_idx))
c2.metric("Desprinderi detectate (TO)", len(events.to_idx))
cycles = segmentation.reject_outliers(segmentation.build_cycles(events))
c3.metric("Cicluri (succesiuni HS-TO)", len(cycles))

fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=omega, name="viteză unghiulară gambă", line=dict(color="steelblue")))
fig.add_trace(go.Scatter(
    x=events.hs_t, y=omega[events.hs_idx], mode="markers",
    name="Contact (HS)",
    marker=dict(color="red", size=12, symbol="circle"),
))
fig.add_trace(go.Scatter(
    x=events.to_t, y=omega[events.to_idx], mode="markers",
    name="Desprindere (TO)",
    marker=dict(color="blue", size=12, symbol="diamond"),
))
fig.update_layout(
    title=f"Detecție evenimente — {method} — {side.upper()}",
    height=400, xaxis_title="Timp (s)", yaxis_title="Viteză unghiulară gambă (°/s)",
)
st.plotly_chart(fig, use_container_width=True)

# Phase timeline
phases = segmentation.label_phases(len(df), cycles)
fig_p = go.Figure()
fig_p.add_trace(go.Scatter(
    x=t, y=phases, mode="lines", line=dict(color="darkgreen", shape="hv"),
    name="fază",
))
fig_p.update_layout(
    title="Succesiunea fazelor: sprijin / balans", height=200, xaxis_title="Timp (s)",
    yaxis=dict(tickmode="array", tickvals=[0, 1, 2], ticktext=["nedefinit", "sprijin", "balans"]),
)
st.plotly_chart(fig_p, use_container_width=True)

# Tabel cicluri
if cycles:
    import pandas as pd
    rows = [
        {
            "ciclu": i + 1,
            "contact început [s]": round(c.hs_start / fs, 3),
            "desprindere [s]": round(c.to / fs, 3),
            "contact sfârșit [s]": round(c.hs_end / fs, 3),
            "durată pas [s]": round(c.stride_s, 3),
            "sprijin [%]": round(c.stance_pct, 1),
            "balans [%]": round(c.swing_pct, 1),
        }
        for i, c in enumerate(cycles)
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
