"""easy-gait dashboard — Streamlit entry point.

Rulează:
    streamlit run dashboard/app.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="easy-gait — Platforma analiza mers IMU",
    page_icon="🦿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🦿 easy-gait")
st.markdown(
    """
    **Platformă software pentru analiza ciclului de mers IMU și control adaptiv al gleznei**

    Dizertație, Raluca Andreea PĂUN — UPB, Facultatea de Inginerie Medicală,
    masterat *Tehnologii Moderne pentru Inginerie Medicală*. Coordonator: Conf. dr.ing.
    Mădălin-Corneliu FRUNZETE. Sesiune: ianuarie 2026.

    ---
    """
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Dataseturi")
    st.markdown(
        """
        - **Samala 2024** — 30 purtători proteză transtibială, IMU Noraxon @ 200 Hz + motion capture
          (Sci Data 11:922).
        - **Wassall NTNU 2025** — 20 utilizatori proteză membru inferior, IMU Xsens @ 100 Hz pe
          teren real (flat, scări, pante, gravel, uneven; DOI: 10.18710/U8RGDL).
        """
    )

with col2:
    st.subheader("🔬 Algoritmi")
    st.markdown(
        """
        - **HS/TO**: Trojaniello-Salarian (offline) + Maqbool R-GEDS (real-time).
        - **FSM gleznă**: 5 stări (Loading / Mid-Stance / Push-Off / Early Swing / Late Swing),
          setpoint-uri din literatura Au 2008, Sup 2008, Bartlett 2021.
        - **Validare**: MAE/F1 evenimente, RMSE/NRMSE/PCC traiectorie unghi gleznă.
        """
    )

st.divider()

st.subheader("Navigare")
st.markdown(
    """
    Folosește meniul din stânga pentru a accesa paginile:

    1. **📊 Signal Explorer** — încarcă un trial Samala/Wassall și vizualizează semnalele brute și filtrate.
    2. **👣 Gait Events** — detectează HS/TO cu Trojaniello sau Maqbool, vezi cicluri segmentate.
    3. **📈 Parameters** — parametri temporali ai mersului per subiect și trial.
    4. **🦿 FSM Simulator** — rulează FSM-ul de control al gleznei și compară cu unghi real.
    5. **🔬 Activity Compare** — comparație inter-activități (Wassall: flat vs. scări vs. pante).
    """
)

# Detectează automat locația datelor
root = Path(__file__).parent.parent
data_dir = root / "data" / "raw"
samala_dir = data_dir / "samala_2024"
wassall_dir = data_dir / "wassall_2025"

with st.sidebar:
    st.markdown("### Stare date")
    if samala_dir.exists():
        n_samala = len([d for d in samala_dir.iterdir() if d.is_dir() and d.name.startswith("S")])
        st.success(f"Samala 2024: {n_samala} subiecți disponibili")
    else:
        st.error("Samala 2024 lipsește. Vezi `docs/DATASET_NOTES.md`.")
    if wassall_dir.exists():
        n_wass = len([d for d in wassall_dir.iterdir() if d.is_dir() and d.name.startswith("P")])
        st.success(f"Wassall 2025: {n_wass} participanți disponibili")
    else:
        st.error("Wassall 2025 lipsește. Vezi `docs/DATASET_NOTES.md`.")

    st.divider()
    st.caption(
        "Acest dashboard nu necesită conexiune internet după instalare. "
        "Toate algoritmii rulează local."
    )
