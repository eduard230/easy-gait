"""Pagina 3 — Parametri temporali ai mersului per subiect."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from _shared import (
    header, list_samala_subjects_cached, load_samala_imu_cached, SAMALA_DIR,
)
from easy_gait import preprocessing, gait_events, segmentation, parameters
from easy_gait.io_utils import (
    SAMALA_SHANK_GYRO_COLS, SAMALA_SHANK_ACCEL_COLS, accel_magnitude,
    detect_prosthetic_side,
)

header("Parametri temporali")
st.caption(
    "Cadență, durată de pas și procent de sprijin, calculate pe cele cinci probe ale "
    "unui subiect sau pe întregul lot, separat pentru piciorul intact și cel protetic."
)

mode = st.radio("Mod", ["Un subiect", "Toți subiecții"], horizontal=True)

# Etichete pentru afișare (cheile interne rămân neschimbate, ca să nu afectăm logica).
COL_RO = {
    "subject": "subiect",
    "trial": "proba",
    "side": "picior",
    "role": "rol",
    "n_cycles": "cicluri",
    "cadence [steps/min]": "cadență [pași/min]",
    "stride mean [s]": "durată pas medie [s]",
    "stride std [s]": "durată pas abatere [s]",
    "stride CV [%]": "variabilitate pas [%]",
    "stance mean [%]": "sprijin mediu [%]",
    "stance std [%]": "sprijin abatere [%]",
    "swing mean [%]": "balans mediu [%]",
    "swing std [%]": "balans abatere [%]",
    "duration [s]": "durată totală [s]",
}


def afiseaza(df_in: pd.DataFrame):
    st.dataframe(df_in.rename(columns=COL_RO), use_container_width=True)


def process_trial(subject: str, trial: int) -> list[dict]:
    df, fs, _meta = load_samala_imu_cached(subject, trial)
    prost = detect_prosthetic_side(df)
    rows = []
    for side in ("left", "right"):
        is_prost = (side == prost)
        pitch_col = SAMALA_SHANK_GYRO_COLS[side]["pitch"]
        omega = preprocessing.gyro_pitch_dps(df, pitch_col, fs=fs)
        events = gait_events.detect_events_trojaniello(omega, fs=fs, prosthetic=is_prost)
        cycles = segmentation.reject_outliers(segmentation.build_cycles(events))
        p = parameters.compute_gait_params(cycles)
        d = p.to_dict()
        d.update({
            "subject": subject, "trial": f"P{trial}", "side": side,
            "role": "protetic" if is_prost else "intact",
        })
        rows.append(d)
    return rows


if mode == "Un subiect":
    subjects = list_samala_subjects_cached()
    subject = st.selectbox("Subiect", subjects)
    rows = []
    for tr in range(1, 6):
        try:
            rows.extend(process_trial(subject, tr))
        except FileNotFoundError:
            continue
    if not rows:
        st.warning("Nicio probă procesabilă pentru acest subiect.")
        st.stop()
    df_params = pd.DataFrame(rows)
    afiseaza(df_params)

    fig = px.bar(df_params, x="trial", y="cadence [steps/min]", color="role", barmode="group",
                  title=f"Cadență — {subject}",
                  labels={"trial": "Proba", "cadence [steps/min]": "Cadență (pași/min)", "role": "Picior"})
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(df_params, x="trial", y="stance mean [%]", color="role", barmode="group",
                   title="Procent de sprijin",
                   labels={"trial": "Proba", "stance mean [%]": "Sprijin (%)", "role": "Picior"})
    st.plotly_chart(fig2, use_container_width=True)

else:
    subjects = list_samala_subjects_cached()
    n_max = st.slider("Câți subiecți să procesăm?", 1, len(subjects), min(5, len(subjects)))
    rows = []
    prog = st.progress(0)
    for i, s in enumerate(subjects[:n_max]):
        for tr in range(1, 6):
            try:
                rows.extend(process_trial(s, tr))
            except FileNotFoundError:
                continue
        prog.progress((i + 1) / n_max)
    df_all = pd.DataFrame(rows)
    afiseaza(df_all)

    # Cadență medie per subiect și rol
    if not df_all.empty:
        agg = df_all.groupby(["subject", "role"])["cadence [steps/min]"].mean().reset_index()
        fig = px.bar(agg, x="subject", y="cadence [steps/min]", color="role", barmode="group",
                      title="Cadență medie per subiect",
                      labels={"subject": "Subiect", "cadence [steps/min]": "Cadență (pași/min)", "role": "Picior"})
        st.plotly_chart(fig, use_container_width=True)

        agg2 = df_all.groupby("role").agg(**{
            "cadență [pași/min]": ("cadence [steps/min]", "mean"),
            "durată pas medie [s]": ("stride mean [s]", "mean"),
            "sprijin mediu [%]": ("stance mean [%]", "mean"),
            "balans mediu [%]": ("swing mean [%]", "mean"),
        }).round(2)
        agg2.index.name = "rol"
        st.subheader("Sumar: picior protetic vs. intact")
        st.dataframe(agg2, use_container_width=True)
