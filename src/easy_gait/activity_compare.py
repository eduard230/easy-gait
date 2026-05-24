"""Comparație parametri de mers inter-activități pe datasetul Wassall 2025.

Furnizează funcții reutilizabile pentru:
  - procesarea unui trial Wassall (IMU PS — shank protetic)
  - agregarea parametrilor per teren (flat/grass/stairs/slope/gravel/uneven)
  - calcul statistici inter-subiect (mean ± std, n_trials) pe lot

Folosit de `dashboard/pages/5_🔬_Activity_Compare.py` și de `scripts/compute_wassall_summary.py`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from easy_gait import gait_events, segmentation, parameters
from easy_gait.io_utils import (
    list_wassall_trials, load_wassall_trial, parse_wassall_filename,
)


TERRAIN_LABELS = {
    "FL": "flat",
    "GR": "grass",
    "ST": "stair",         # ascent + descent combinate; clarificate prin alte fișiere dacă disponibil
    "SL": "slope",
    "GV": "gravel",
    "UN": "uneven",
}

WALKAID_LABELS = {
    "wi": "with_aid",
    "wo": "without_aid",
}


@dataclass
class TrialResult:
    """Rezultatul procesării unui trial Wassall (PS senzor)."""
    participant: str
    trial_id: str
    terrain: str           # "flat", "grass", etc.
    walkaid: str           # "with_aid", "without_aid"
    n_cycles: int
    cadence_steps_min: float
    stride_mean_s: float
    stride_std_s: float
    stride_cv: float
    stance_mean_pct: float
    swing_mean_pct: float

    def to_dict(self) -> dict:
        return {
            "participant": self.participant,
            "trial_id": self.trial_id,
            "terrain": self.terrain,
            "walkaid": self.walkaid,
            "n_cycles": self.n_cycles,
            "cadence_steps_min": round(self.cadence_steps_min, 2),
            "stride_mean_s": round(self.stride_mean_s, 3),
            "stride_std_s": round(self.stride_std_s, 3),
            "stride_cv": round(self.stride_cv, 4),
            "stance_mean_pct": round(self.stance_mean_pct, 2),
            "swing_mean_pct": round(self.swing_mean_pct, 2),
        }


def process_wassall_trial_ps(path: str | Path) -> TrialResult | None:
    """Procesează un trial Wassall (CSV PS) și returnează parametrii.

    Returns:
        TrialResult sau None dacă trial-ul nu produce cicluri valide.
    """
    g = load_wassall_trial(path)
    df = g.df
    fs = g.fs
    meta = g.meta

    # Gyro Y = pitch sagital. Wassall e în rad/s → convertim la deg/s.
    omega_dps = np.rad2deg(df["Gyr_Y"].to_numpy())
    events = gait_events.detect_events_trojaniello(omega_dps, fs=fs, prosthetic=True)
    cycles = segmentation.reject_outliers(segmentation.build_cycles(events))
    if not cycles:
        return None
    p = parameters.compute_gait_params(cycles)
    if p.n_cycles == 0:
        return None

    terrain_code = (meta["terrain"] or "").upper()
    walkaid_code = (meta.get("walkaid") or "").lower()
    participant_id = Path(meta["path"]).parent.name

    return TrialResult(
        participant=participant_id,
        trial_id=Path(meta["path"]).stem,
        terrain=TERRAIN_LABELS.get(terrain_code, terrain_code),
        walkaid=WALKAID_LABELS.get(walkaid_code, walkaid_code or "unknown"),
        n_cycles=p.n_cycles,
        cadence_steps_min=p.cadence_steps_per_min,
        stride_mean_s=p.stride_s_mean,
        stride_std_s=p.stride_s_std,
        stride_cv=p.stride_cv,
        stance_mean_pct=p.stance_pct_mean,
        swing_mean_pct=p.swing_pct_mean,
    )


def process_participant(root: str | Path, participant: str) -> pd.DataFrame:
    """Procesează toate trial-urile PS pentru un participant Wassall.

    Returns:
        DataFrame cu un rând per trial (coloanele din TrialResult.to_dict()).
        Gol dacă nu există trial-uri.
    """
    trials_df = list_wassall_trials(root, participant, sensor="PS")
    if trials_df.empty:
        return pd.DataFrame()
    rows = []
    for path in trials_df["path"]:
        res = process_wassall_trial_ps(path)
        if res is not None:
            rows.append(res.to_dict())
    return pd.DataFrame(rows)


def aggregate_by_terrain(df: pd.DataFrame) -> pd.DataFrame:
    """Agregare statistici per teren (mean, std, n) peste rezultatele individuale.

    Args:
        df: DataFrame cu coloanele din TrialResult.to_dict() (de la `process_participant`
            sau combinat peste mai mulți).

    Returns:
        DataFrame indexat pe terrain, cu mean/std/n per parametru.
    """
    if df.empty:
        return pd.DataFrame()
    numeric_cols = [
        "cadence_steps_min", "stride_mean_s", "stride_cv",
        "stance_mean_pct", "swing_mean_pct",
    ]
    agg = df.groupby("terrain").agg(
        n_trials=("cadence_steps_min", "count"),
        **{f"{c}_mean": (c, "mean") for c in numeric_cols},
        **{f"{c}_std": (c, "std") for c in numeric_cols},
    ).round(3)
    return agg


def aggregate_by_terrain_and_walkaid(df: pd.DataFrame) -> pd.DataFrame:
    """Agregare suplimentară per (terrain, walkaid) pentru a vedea efectul bastonului."""
    if df.empty:
        return pd.DataFrame()
    numeric_cols = [
        "cadence_steps_min", "stride_mean_s", "stride_cv",
        "stance_mean_pct", "swing_mean_pct",
    ]
    agg = df.groupby(["terrain", "walkaid"]).agg(
        n_trials=("cadence_steps_min", "count"),
        **{f"{c}_mean": (c, "mean") for c in numeric_cols},
        **{f"{c}_std": (c, "std") for c in numeric_cols},
    ).round(3)
    return agg
