"""Pagina 5 — Comparație inter-activități pe datasetul Wassall 2025."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from _shared import (
    header, list_wassall_participants_cached, load_wassall_trial_cached, WASSALL_DIR,
)
from easy_gait import preprocessing, gait_events, segmentation, parameters
from easy_gait.io_utils import (
    list_wassall_trials, WASSALL_TERRAIN_LABELS,
)

header("Comparație activități")
st.caption(
    "Cum se schimbă parametrii mersului în funcție de teren — plat, scări, pante, iarbă, "
    "pietriș, suprafață denivelată — pentru un participant sau pentru întregul lot Wassall."
)

participants = list_wassall_participants_cached()
if not participants:
    st.error("Niciun participant Wassall găsit.")
    st.stop()

mode = st.radio("Mod", ["Un participant", "Mai mulți participanți"], horizontal=True)


def process_wassall_trial(path: str) -> dict | None:
    df, fs, meta = load_wassall_trial_cached(path)
    omega_dps = np.rad2deg(df["Gyr_Y"].to_numpy())
    accel_mag = np.sqrt((df[["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy() ** 2).sum(axis=1))
    events = gait_events.detect_events_trojaniello(omega_dps, fs=fs, prosthetic=True)
    cycles = segmentation.reject_outliers(segmentation.build_cycles(events))
    p = parameters.compute_gait_params(cycles)
    if p.n_cycles == 0:
        return None
    d = p.to_dict()
    terrain_code = meta["terrain"]
    # Cod teren → etichetă în română.
    terrain_map = {
        "FL": "plat", "ST": "scări", "SL": "pantă",
        "GR": "iarbă", "GV": "pietriș", "UN": "denivelat",
    }
    walkaid_map = {"wi": "cu sprijin", "wo": "fără sprijin", "w0": "fără sprijin"}
    d.update({
        "participant": meta["path"].split("\\")[-2].split("/")[-1],
        "trial_id": Path(meta["path"]).stem,
        "terrain": terrain_map.get(terrain_code, terrain_code),
        "walkaid": walkaid_map.get(meta["walkaid"], meta["walkaid"]),
    })
    return d


LBL = {
    "terrain": "Teren", "walkaid": "Condiție mers",
    "cadence [steps/min]": "Cadență (pași/min)",
    "stance mean [%]": "Procentajul fazei de sprijin (%)",
    "stride mean [s]": "Durată pas (s)",
}

if mode == "Un participant":
    participant = st.selectbox("Participant", participants)
    trials_df = list_wassall_trials(WASSALL_DIR, participant, sensor="PS")
    if trials_df.empty:
        st.warning(f"Nicio probă pentru {participant}.")
        st.stop()
    st.caption(f"Se procesează {len(trials_df)} probe pentru {participant}…")
    rows = []
    prog = st.progress(0)
    for i, path in enumerate(trials_df["path"]):
        d = process_wassall_trial(path)
        if d:
            rows.append(d)
        prog.progress((i + 1) / len(trials_df))
    df_res = pd.DataFrame(rows)
    if df_res.empty:
        st.warning("Niciun rezultat valid.")
        st.stop()
    st.dataframe(df_res, use_container_width=True)

    fig = px.box(df_res, x="terrain", y="cadence [steps/min]", color="walkaid",
                  title=f"Cadență pe teren — {participant}", labels=LBL)
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.box(df_res, x="terrain", y="stance mean [%]", color="walkaid",
                   title="Procentajul fazei de sprijin pe teren", labels=LBL)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.box(df_res, x="terrain", y="stride mean [s]", color="walkaid",
                   title="Durata pasului pe teren", labels=LBL)
    st.plotly_chart(fig3, use_container_width=True)

else:
    n_max = st.slider("Câți participanți?", 1, len(participants), min(5, len(participants)))
    rows = []
    prog = st.progress(0)
    for i, part in enumerate(participants[:n_max]):
        trials_df = list_wassall_trials(WASSALL_DIR, part, sensor="PS")
        for path in trials_df["path"]:
            d = process_wassall_trial(path)
            if d:
                rows.append(d)
        prog.progress((i + 1) / n_max)
    df_all = pd.DataFrame(rows)
    st.dataframe(df_all, use_container_width=True)

    if not df_all.empty:
        fig = px.box(df_all, x="terrain", y="cadence [steps/min]", color="walkaid",
                      title="Cadență pe tip de teren", labels=LBL)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.box(df_all, x="terrain", y="stance mean [%]", color="walkaid",
                       title="Procentajul fazei de sprijin pe tip de teren", labels=LBL)
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.box(df_all, x="terrain", y="stride mean [s]", color="walkaid",
                       title="Durata pasului pe tip de teren", labels=LBL)
        st.plotly_chart(fig3, use_container_width=True)
