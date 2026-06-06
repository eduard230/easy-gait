"""Platformă pentru analiza mersului — punct de intrare Streamlit.

Rulează:
    streamlit run dashboard/app.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Platformă pentru analiza mersului",
    layout="wide",
    initial_sidebar_state="expanded",
)

DASHBOARD = Path(__file__).parent
PAGES_DIR = DASHBOARD / "pages"


def home():
    st.title("Platformă pentru analiza mersului")
    st.markdown(
        "Analiza ciclului de mers din semnale IMU și simularea unui control de gleznă "
        "protetică, pe două seturi de date publice."
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Seturi de date")
        st.markdown(
            """
            - **Samala 2024** — 30 purtători de proteză transtibială, IMU la 200 Hz și
              motion capture sincronizat, cinci probe de mers pe plat.
            - **Wassall 2025** — 20 de participanți, IMU la 100 Hz pe teren variat:
              plat, scări, pante, iarbă, pietriș, suprafață denivelată.
            """
        )

    with col2:
        st.subheader("Metode")
        st.markdown(
            """
            - **Evenimente HS/TO** — Trojaniello (offline) și Maqbool (timp real).
            - **Control gleznă** — automat cu 5 stări (FSM), cu praguri din literatură.
            - **Validare** — eroare și corelație față de unghiul măsurat optic.
            """
        )

    st.divider()

    st.subheader("Pagini")
    st.markdown(
        """
        - **Explorare semnale** — semnalele brute și filtrate pentru o probă.
        - **Detecție evenimente** — contactul și desprinderea piciorului, ciclurile rezultate.
        - **Parametri temporali** — cadență, durată de pas, procent de sprijin pe subiect.
        - **Simulator FSM** — unghiul de gleznă comandat față de cel real.
        - **Comparație activități** — diferențele între tipuri de teren (Wassall).
        - **Simulator proteză** — animație a protezei sincronizată cu controlul.
        """
    )


# Meniul de navigare cu titluri în română (cu diacritice).
pages = [
    st.Page(home, title="Acasă", default=True),
    st.Page(str(PAGES_DIR / "1_Explorare_semnale.py"), title="Explorare semnale"),
    st.Page(str(PAGES_DIR / "2_Detectie_evenimente.py"), title="Detecție evenimente"),
    st.Page(str(PAGES_DIR / "3_Parametri_temporali.py"), title="Parametri temporali"),
    st.Page(str(PAGES_DIR / "4_Simulator_FSM.py"), title="Simulator FSM"),
    st.Page(str(PAGES_DIR / "5_Comparatie_activitati.py"), title="Comparație activități"),
    st.Page(str(PAGES_DIR / "6_Simulator_proteza.py"), title="Simulator proteză"),
]

pg = st.navigation(pages)
pg.run()
