"""Funcții și constante partajate între paginile dashboard-ului."""
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent.parent
SAMALA_DIR = ROOT / "data" / "raw" / "samala_2024"
WASSALL_DIR = ROOT / "data" / "raw" / "wassall_2025"


@st.cache_data(show_spinner=False)
def list_samala_subjects_cached() -> list[str]:
    from easy_gait.io_utils import list_samala_subjects
    return list_samala_subjects(SAMALA_DIR)


@st.cache_data(show_spinner=False)
def list_wassall_participants_cached() -> list[str]:
    from easy_gait.io_utils import list_wassall_participants
    return list_wassall_participants(WASSALL_DIR)


@st.cache_data(show_spinner=True)
def load_samala_imu_cached(subject: str, trial: int):
    from easy_gait.io_utils import load_samala_imu
    g = load_samala_imu(SAMALA_DIR, subject, trial)
    # Streamlit cache nu serializează dataclass cu DataFrame, returnăm tuplu
    return g.df, g.fs, g.meta


@st.cache_data(show_spinner=True)
def load_wassall_trial_cached(path: str):
    from easy_gait.io_utils import load_wassall_trial
    g = load_wassall_trial(path)
    return g.df, g.fs, g.meta


def header(title: str, icon: str = "📊"):
    st.set_page_config(page_title=f"easy-gait — {title}", page_icon=icon, layout="wide")
    st.title(f"{icon} {title}")
