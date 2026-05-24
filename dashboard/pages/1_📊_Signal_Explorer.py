"""Pagina 1 — Vizualizare semnale IMU brute și filtrate."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from _shared import (
    header, list_samala_subjects_cached, list_wassall_participants_cached,
    load_samala_imu_cached, load_wassall_trial_cached, SAMALA_DIR, WASSALL_DIR,
)
from easy_gait import preprocessing
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS, SAMALA_ANKLE_ANGLE_COLS,
    detect_prosthetic_side, list_wassall_trials, WASSALL_GYRO_COLS, WASSALL_ACCEL_COLS,
)

header("Signal Explorer", icon="📊")

dataset = st.sidebar.radio("Dataset", ["Samala 2024", "Wassall 2025"], index=0)

if dataset == "Samala 2024":
    subjects = list_samala_subjects_cached()
    if not subjects:
        st.error("Niciun subiect Samala găsit. Verifică `data/raw/samala_2024/`.")
        st.stop()
    subject = st.sidebar.selectbox("Subiect", subjects, index=0)
    trial = st.sidebar.selectbox("Trial", [1, 2, 3, 4, 5], index=0)

    df, fs, meta = load_samala_imu_cached(subject, trial)
    prost_side = detect_prosthetic_side(df)
    intact_side = "right" if prost_side == "left" else "left"

    st.caption(
        f"Subiect **{subject}** trial **Walking{trial}** | "
        f"fs = {fs} Hz | durata = {meta['duration_s']:.2f} s | "
        f"partea protetică detectată: **{prost_side.upper()}** (ROM scăzut)"
    )

    side = st.sidebar.radio("Picior afișat", [intact_side, prost_side],
                             format_func=lambda s: f"{s.upper()} ({'INTACT' if s == intact_side else 'PROTETIC'})")
    cutoff = st.sidebar.slider("Cutoff filtru (Hz)", 5, 50, 15)

    pitch_col = SAMALA_SHANK_GYRO_COLS[side]["pitch"]
    accel_cols = SAMALA_SHANK_ACCEL_COLS[side]
    ankle_col = SAMALA_ANKLE_ANGLE_COLS[side]

    t = np.arange(len(df)) / fs
    pitch_raw = df[pitch_col].to_numpy()
    pitch_filt = preprocessing.butter_lowpass(pitch_raw, fs=fs, cutoff_hz=cutoff)
    omega = preprocessing.gyro_pitch_dps(df, pitch_col, fs=fs, cutoff_hz=cutoff)

    fig_pitch = go.Figure()
    fig_pitch.add_trace(go.Scatter(x=t, y=pitch_raw, name="brut", opacity=0.5, line=dict(color="lightgray")))
    fig_pitch.add_trace(go.Scatter(x=t, y=pitch_filt, name=f"filtrat ({cutoff} Hz)", line=dict(color="steelblue")))
    fig_pitch.update_layout(
        title=f"Shank pitch — {side.upper()}", height=300,
        xaxis_title="Timp (s)", yaxis_title="Unghi (°)",
    )
    st.plotly_chart(fig_pitch, use_container_width=True)

    fig_omega = go.Figure()
    fig_omega.add_trace(go.Scatter(x=t, y=omega, name="ω shank pitch rate", line=dict(color="darkorange")))
    fig_omega.add_hline(y=0, line=dict(color="gray", dash="dot"))
    fig_omega.update_layout(
        title="Viteza unghiulară shank (pitch rate) — utilizată pentru detecția HS/TO",
        height=300, xaxis_title="Timp (s)", yaxis_title="ω (deg/s)",
    )
    st.plotly_chart(fig_omega, use_container_width=True)

    from easy_gait.io_utils import accel_magnitude
    amag = accel_magnitude(df, accel_cols)
    fig_a = go.Figure()
    for c in accel_cols:
        fig_a.add_trace(go.Scatter(x=t, y=df[c], name=c.split(" ")[2] + "-axis", opacity=0.6))
    fig_a.add_trace(go.Scatter(x=t, y=amag, name="‖a‖", line=dict(color="black", width=2)))
    fig_a.update_layout(
        title=f"Acceleratii shank — {side.upper()}", height=300,
        xaxis_title="Timp (s)", yaxis_title="Acc. (m/s²)",
    )
    st.plotly_chart(fig_a, use_container_width=True)

    fig_ankle = go.Figure()
    fig_ankle.add_trace(go.Scatter(x=t, y=df[ankle_col], name=ankle_col, line=dict(color="green")))
    fig_ankle.update_layout(
        title=f"Unghi gleznă (dorsi +, plantar −) — {side.upper()}", height=300,
        xaxis_title="Timp (s)", yaxis_title="Unghi (°)",
    )
    st.plotly_chart(fig_ankle, use_container_width=True)

    st.caption(f"ROM ankle {side.upper()}: {df[ankle_col].max() - df[ankle_col].min():.1f}°")

else:  # Wassall
    participants = list_wassall_participants_cached()
    if not participants:
        st.error("Niciun participant Wassall găsit. Verifică `data/raw/wassall_2025/`.")
        st.stop()
    participant = st.sidebar.selectbox("Participant", participants)
    sensor = st.sidebar.selectbox("Senzor", ["PS (prosthetic shank)", "TH (thigh)", "TR (trunk)", "OS (other shank)"], index=0)
    sensor_code = sensor.split(" ")[0]

    trials_df = list_wassall_trials(WASSALL_DIR, participant, sensor=sensor_code)
    if trials_df.empty:
        st.warning(f"Niciun trial pentru senzorul {sensor_code} la {participant}.")
        st.stop()
    st.dataframe(trials_df[["trial_id", "terrain", "walkaid", "trial"]].head(20), use_container_width=True)

    trial_id = st.sidebar.selectbox("Trial", trials_df["trial_id"].tolist())
    path = trials_df.loc[trials_df["trial_id"] == trial_id, "path"].iloc[0]
    df, fs, meta = load_wassall_trial_cached(path)
    cutoff = st.sidebar.slider("Cutoff filtru (Hz)", 5, 25, 15)

    t = np.arange(len(df)) / fs
    st.caption(
        f"{participant} — {trial_id} | fs={fs} Hz | dur={meta['duration_s']:.2f}s | "
        f"teren={meta['terrain']} | walkaid={meta['walkaid']}"
    )

    # Gyro Y (medio-lateral) e cel ml-axis pentru HS/TO detection în Wassall (vezi README)
    gy_rad = df["Gyr_Y"].to_numpy()
    gy_dps = np.rad2deg(gy_rad)
    gy_filt = preprocessing.butter_lowpass(gy_dps, fs=fs, cutoff_hz=cutoff)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=gy_dps, name="brut", opacity=0.5, line=dict(color="lightgray")))
    fig.add_trace(go.Scatter(x=t, y=gy_filt, name=f"filtrat ({cutoff} Hz)", line=dict(color="steelblue")))
    fig.update_layout(title=f"Gyroscope Y ({sensor_code})", height=300,
                       xaxis_title="Timp (s)", yaxis_title="ω (deg/s)")
    st.plotly_chart(fig, use_container_width=True)

    # Acceleratii
    fig_a = go.Figure()
    for c in WASSALL_ACCEL_COLS:
        fig_a.add_trace(go.Scatter(x=t, y=df[c], name=c, opacity=0.7))
    fig_a.update_layout(title=f"Acceleratii ({sensor_code})", height=300,
                         xaxis_title="Timp (s)", yaxis_title="Acc. (m/s²)")
    st.plotly_chart(fig_a, use_container_width=True)

    # Strides & terrain labels
    fig_lbl = go.Figure()
    fig_lbl.add_trace(go.Scatter(x=t, y=df["Steps"], name="Stride #", line=dict(color="purple")))
    fig_lbl.add_trace(go.Scatter(x=t, y=df["Terrain"], name="Terrain label", line=dict(color="orange")))
    fig_lbl.update_layout(title="Stride numbering și terrain label (din dataset)", height=250,
                           xaxis_title="Timp (s)")
    st.plotly_chart(fig_lbl, use_container_width=True)
