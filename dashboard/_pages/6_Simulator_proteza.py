"""Pagina 6 — Simulator vizual al protezei animat în sincron cu FSM-ul."""
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
from easy_gait import preprocessing, gait_events, segmentation, fsm, ankle_controller
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS,
    accel_magnitude, detect_prosthetic_side, compute_ankle_angle,
)
from easy_gait.prosthesis_viz import build_animation_figure, build_legend_figure, FSM_COLORS

header("Simulator proteză")

# Controale
c1, c2, c3, c4 = st.columns(4)
subjects = list_samala_subjects_cached()
subject = c1.selectbox("Subiect", subjects, key="anim_subject")
trial = c2.selectbox("Proba", [1, 2, 3, 4, 5], key="anim_trial")
activity = c3.selectbox("Activitate", list(fsm.SETPOINTS.keys()), key="anim_activity")
viz_mode = c4.selectbox(
    "Sursa unghiului de gleznă",
    ["Unghi comandat (control)", "Unghi real (măsurat)"],
    key="anim_mode",
)

# Încărcare date
df, fs, _meta = load_samala_imu_cached(subject, trial)
prost = detect_prosthetic_side(df)
intact = "right" if prost == "left" else "left"

side = st.radio(
    "Picior simulat", [prost, intact],
    format_func=lambda s: f"{s.upper()} ({'protetic' if s == prost else 'intact'})",
    horizontal=True, key="anim_side",
)
is_prost = (side == prost)

# Procesare
pitch_col = SAMALA_SHANK_GYRO_COLS[side]["pitch"]
omega = preprocessing.gyro_pitch_dps(df, pitch_col, fs=fs)
events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=is_prost)
# Calibrăm ankle = 0° la primul HS detectat (convenția clinică Perry & Burnfield)
ref_idx = int(events.hs_idx[0]) if len(events.hs_idx) > 0 else 100
ankle_real = compute_ankle_angle(df, side, reference_idx=ref_idx)
trace = fsm.run_fsm(
    n_samples=len(df), fs=fs,
    hs_idx=events.hs_idx, to_idx=events.to_idx,
    omega_shank_dps=omega, ankle_angle_estimate_deg=ankle_real,
    config=fsm.FSMConfig(activity=activity),
)
ankle_fsm = ankle_controller.generate_trajectory(trace, fs=fs)

# Selectare sursă unghi pentru animație
if viz_mode == "Unghi comandat (control)":
    ankle_to_animate = ankle_fsm
    src_label = "comandat"
else:
    ankle_to_animate = ankle_real
    src_label = "măsurat"

# Decupare la primele 6 secunde pentru fluiditate (animație 60 fps = 360 cadre)
window_s = st.slider("Fereastra de animație (s)", 2.0, min(15.0, len(df) / fs), 6.0, step=0.5)
n_window = int(window_s * fs)
# Default start: primul HS detectat (intrare în S1) — același punct de plecare
# pentru toți subiecții. Rotunjit la cel mai apropiat pas de 0.5 s în jos.
first_hs_s = float(events.hs_idx[0] / fs) if len(events.hs_idx) > 0 else 0.0
max_start = max(0.0, len(df) / fs - window_s)
default_start_s = float(np.clip(np.floor(first_hs_s * 2) / 2, 0.0, max_start))
start_s = st.slider(
    "Start (s)", 0.0, max_start, default_start_s, step=0.5,
    help=f"Default: chiar înainte de primul HS detectat ({first_hs_s:.2f} s), "
         f"ca animația să înceapă cu intrare în S1.",
)
playback_speed = st.select_slider(
    "Viteză animație",
    options=[0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0],
    value=0.5,
    format_func=lambda v: f"{v}× ({'real-time' if v == 1.0 else 'lentă' if v < 1.0 else 'rapidă'})",
)
i0 = int(start_s * fs)
i1 = min(i0 + n_window, len(df))

times_w = np.arange(i0, i1) / fs
ang_w = ankle_to_animate[i0:i1]
fsm_w = trace.state_per_sample[i0:i1]

st.caption(
    f"Subiect **{subject}** · proba **{trial}** · picior **{side.upper()}** "
    f"({'protetic' if is_prost else 'intact'}) · activitate **{activity}** · "
    f"unghi **{src_label}** · fereastră {start_s:.1f}–{start_s+window_s:.1f} s"
)

# Două coloane: animație + graficul sincronizat
left, right = st.columns([1.2, 1.5])

with left:
    st.markdown("#### Vedere laterală (sagitală)")
    fig_anim = build_animation_figure(
        times_w, ang_w, fsm_w, resample_hz=60, height=480,
        playback_speed=playback_speed,
    )
    st.plotly_chart(fig_anim, use_container_width=True)
    st.plotly_chart(build_legend_figure(), use_container_width=True)

with right:
    st.markdown("#### Unghiul gleznei și faza pasului (sincron)")
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=("Unghi gleznă (dorsiflexie +, plantarflexie −)", "Faza pasului"),
    )
    fig.add_trace(go.Scatter(
        x=times_w, y=ang_w, name=f"unghi {src_label}",
        line=dict(color="darkorange", width=2),
    ), row=1, col=1)
    # Marcaje HS/TO în fereastră
    hs_in = [t for t in events.hs_t if start_s <= t <= start_s + window_s]
    to_in = [t for t in events.to_t if start_s <= t <= start_s + window_s]
    for h in hs_in:
        fig.add_vline(x=h, line=dict(color="red", width=1, dash="dot"), row=1, col=1)
    for t in to_in:
        fig.add_vline(x=t, line=dict(color="blue", width=1, dash="dot"), row=1, col=1)

    # Faza pasului, colorată
    fig.add_trace(go.Scatter(
        x=times_w, y=fsm_w, mode="lines",
        line=dict(color="purple", shape="hv", width=2), name="faza pasului",
    ), row=2, col=1)

    fig.update_yaxes(title="Unghi (°)", row=1, col=1)
    fig.update_yaxes(
        title="Fază", row=2, col=1, tickmode="array",
        tickvals=[1, 2, 3, 4, 5], ticktext=["1", "2", "3", "4", "5"],
    )
    fig.update_xaxes(title="Timp (s)", row=2, col=1)
    fig.update_layout(height=480, template="plotly_white", showlegend=True,
                       margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

# Info biomecanică sub
st.divider()
st.markdown(
    """
    **Repere în desen.** Pilonul vertical este gamba, cercul alb de la bază este glezna,
    iar dreptunghiul colorat este talpa; cercul gri de sus marchează genunchiul.

    **Fazele mersului**, în ordinea în care apar (culoarea tălpii urmează aceeași codare ca în legendă):

    - **Contactul inițial** — călcâiul atinge solul, gamba începe să se rotească peste el.
    - **Sprijin median** — talpa e plată, greutatea trece peste gleznă, gamba se înclină înainte.
    - **Desprindere** — călcâiul se ridică, vârful se împinge înainte de a părăsi solul.
    - **Începutul fazei de balans** — piciorul s-a desprins și se ridică.
    - **Sfârșitul fazei de balans** — gamba se duce înainte, vârful coboară pentru următorul contact.
    """
)
