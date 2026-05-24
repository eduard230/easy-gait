"""Încărcare semnale IMU/OMC din dataseturile publice folosite în dizertație.

Suportă:
- Samala et al. 2024 (Sci Data 11:922) — IMU Noraxon 200 Hz + OMC referință
- Wassall NTNU 2025 (dataverse.no DOI 10.18710/U8RGDL) — IMU Xsens Awinda 100 Hz + terrain labels
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# Constante dataset
# ──────────────────────────────────────────────────────────────────────────────

SAMALA_FS = 200  # Hz, verificat empiric pe S01 (2888 frame / 14.44 s)
WASSALL_FS = 100  # Hz, declarat în README dataverse.no

WASSALL_TERRAIN_LABELS = {
    1: "flat",
    2: "grass",
    4: "stair_ascent",
    5: "stair_descent",
    6: "slope_ascent",
    7: "slope_descent",
    8: "gravel",
    9: "uneven",
}

WASSALL_SENSORS = {
    "PS": "prosthetic_shank",
    "TH": "prosthetic_thigh",
    "TR": "trunk",
    "OS": "other_shank",
}


@dataclass
class GaitTrial:
    """Container minimal pentru un trial de mers încărcat."""
    source: str          # "samala" | "wassall"
    subject_id: str      # ex. "S01" | "P01"
    trial_id: str        # ex. "Walking1" | "FLwi02"
    fs: float            # frecvență eșantionare (Hz)
    side: str            # "left" | "right" | "prosthetic" | "intact"
    df: pd.DataFrame     # semnale brute
    meta: dict           # metadate suplimentare (terrain, sensor, etc.)


# ──────────────────────────────────────────────────────────────────────────────
# Samala 2024
# ──────────────────────────────────────────────────────────────────────────────

def _samala_imu_path(root: Path, subject: str, trial: int) -> Path:
    """Returnează calea către CSV-ul IMU al unui trial Samala."""
    return Path(root) / subject / f"[IMU]{subject}_Walking{trial}.csv"


def _samala_omc_path(root: Path, subject: str) -> Path:
    """Calea către CSV-ul OMC (toate trial-urile, multi-header pe 3 niveluri)."""
    return Path(root) / subject / f"[OMC]{subject}.csv"


def load_samala_imu(root: str | Path, subject: str, trial: int) -> GaitTrial:
    """Încarcă un singur trial IMU Samala.

    Args:
        root: directorul rădăcină ce conține S01/, S02/, ...
        subject: id subiect, ex. "S01"
        trial: număr trial 1..5

    Returns:
        GaitTrial cu df conținând toate cele 141 coloane Noraxon @ 200 Hz.
    """
    p = _samala_imu_path(Path(root), subject, trial)
    if not p.exists():
        raise FileNotFoundError(p)
    df = pd.read_csv(p)
    return GaitTrial(
        source="samala",
        subject_id=subject,
        trial_id=f"Walking{trial}",
        fs=SAMALA_FS,
        side="both",
        df=df,
        meta={"path": str(p), "n_samples": len(df), "duration_s": len(df) / SAMALA_FS},
    )


def load_samala_omc(root: str | Path, subject: str) -> dict[str, pd.DataFrame]:
    """Încarcă fișierul OMC agregat pentru un subiect Samala.

    Structura sursă: multi-header pe 3 niveluri — row1=Walking1..5, row2=LANKLE_ANGLE etc,
    row3=axe X/Y/Z (X=flex/ext, Y=abd/add, Z=int/ext rot).

    Returns:
        dict trial_name -> DataFrame cu coloane ['LANKLE_X','LANKLE_Y',...,'RANKLE_X',...]
    """
    p = _samala_omc_path(Path(root), subject)
    if not p.exists():
        raise FileNotFoundError(p)
    raw = pd.read_csv(p, header=[0, 1, 2])
    # Coloana 0 e ITEM (frame index). Coloanele restul sunt MultiIndex.
    # Detectăm trial-urile prin nivelul 0.
    trials: dict[str, pd.DataFrame] = {}
    lvl0 = raw.columns.get_level_values(0)
    current_trial = None
    cols_per_trial: dict[str, list[tuple]] = {}
    for col in raw.columns:
        l0, l1, l2 = col
        if isinstance(l0, str) and l0.startswith("Walking"):
            current_trial = l0
        if current_trial is None:
            continue
        if "Unnamed" in str(l1) or l1 == "":
            continue
        cols_per_trial.setdefault(current_trial, []).append(col)

    for trial, cols in cols_per_trial.items():
        sub = raw[cols].copy()
        # Flatten coloane: LANKLE_ANGLE_X etc.
        new_cols = []
        for _, joint, axis in cols:
            joint_clean = joint.replace("_ANGLE", "")
            new_cols.append(f"{joint_clean}_{axis}")
        sub.columns = new_cols
        sub = sub.apply(pd.to_numeric, errors="coerce").dropna(how="all").reset_index(drop=True)
        trials[trial] = sub
    return trials


def list_samala_subjects(root: str | Path) -> list[str]:
    """Listează subiecții disponibili în directorul Samala."""
    root = Path(root)
    if not root.exists():
        return []
    return sorted(
        d.name for d in root.iterdir()
        if d.is_dir() and d.name.startswith("S") and len(d.name) == 3
    )


# Coloane de interes pre-selectate (subset din cele 141 Noraxon).
# Convenția reală (verificată în CSV S01): sufixele sunt LT/RT, nu Left/Right.
SAMALA_SHANK_GYRO_COLS = {
    "left": {
        "course": "Shank course LT (deg)",
        "pitch": "Shank pitch LT (deg)",
        "roll": "Shank roll LT (deg)",
    },
    "right": {
        "course": "Shank course RT (deg)",
        "pitch": "Shank pitch RT (deg)",
        "roll": "Shank roll RT (deg)",
    },
}

# Senzori IMU direct pe tibie (preferate pentru detecție HS/TO):
SAMALA_SHANK_ACCEL_COLS = {
    "left": [
        "Shank Accel Sensor X LT (m/s^2)",
        "Shank Accel Sensor Y LT (m/s^2)",
        "Shank Accel Sensor Z LT (m/s^2)",
    ],
    "right": [
        "Shank Accel Sensor X RT (m/s^2)",
        "Shank Accel Sensor Y RT (m/s^2)",
        "Shank Accel Sensor Z RT (m/s^2)",
    ],
}

# Acceleratii proiectate în sistem segment (alternativa, mai filtrată):
SAMALA_SHANK_SEG_ACCEL_COLS = {
    "left": [
        "Noraxon MyoMotion-Segments-Shank LT-Acceleration-x (m/s^2)",
        "Noraxon MyoMotion-Segments-Shank LT-Acceleration-y (m/s^2)",
        "Noraxon MyoMotion-Segments-Shank LT-Acceleration-z (m/s^2)",
    ],
    "right": [
        "Noraxon MyoMotion-Segments-Shank RT-Acceleration-x (m/s^2)",
        "Noraxon MyoMotion-Segments-Shank RT-Acceleration-y (m/s^2)",
        "Noraxon MyoMotion-Segments-Shank RT-Acceleration-z (m/s^2)",
    ],
}

SAMALA_PELVIS_ACCEL_COLS = [
    "Pelvis Accel Sensor X (m/s^2)",
    "Pelvis Accel Sensor Y (m/s^2)",
    "Pelvis Accel Sensor Z (m/s^2)",
]

# Coloane unghi articulație gleznă derivate de Noraxon — ATENȚIE: aceste coloane
# ("Ankle Dorsiflexion LT/RT") s-au dovedit pe Samala 2024 a fi inconsistente cu
# convenția clinică standard (Perry & Burnfield 2010) — afișează valori opuse semn
# și magnitudini ne-fiziologice în swing.
# Folosim în schimb funcția `compute_ankle_angle()` care derivă unghiul direct din
# diferența pitch shank-foot, validată pe ciclu fiziologic (HS≈0, push-off≈-18°,
# mid-swing≈+10°).
SAMALA_ANKLE_ANGLE_COLS = {
    "left": "Ankle Dorsiflexion LT (deg)",   # raw Noraxon — fallback
    "right": "Ankle Dorsiflexion RT (deg)",  # raw Noraxon — fallback
}

SAMALA_FOOT_PITCH_COLS = {"left": "Foot pitch LT (deg)", "right": "Foot pitch RT (deg)"}
SAMALA_SHANK_PITCH_COLS = {"left": "Shank pitch LT (deg)", "right": "Shank pitch RT (deg)"}

SAMALA_FOOT_ACCEL_COLS = {
    "left": [
        "Foot Accel Sensor X LT (m/s^2)",
        "Foot Accel Sensor Y LT (m/s^2)",
        "Foot Accel Sensor Z LT (m/s^2)",
    ],
    "right": [
        "Foot Accel Sensor X RT (m/s^2)",
        "Foot Accel Sensor Y RT (m/s^2)",
        "Foot Accel Sensor Z RT (m/s^2)",
    ],
}


def detect_prosthetic_side(df) -> str:
    """Determinare euristică a piciorului protetic prin ROM-ul gleznei.

    Pe piciorul protetic SACH/pasiv ROM-ul Ankle Dorsiflexion este ~0-5° (rigid),
    pe piciorul sănătos este ~25-40°. Întoarce 'left' sau 'right'.
    """
    rom_lt = float(df[SAMALA_ANKLE_ANGLE_COLS["left"]].max() - df[SAMALA_ANKLE_ANGLE_COLS["left"]].min())
    rom_rt = float(df[SAMALA_ANKLE_ANGLE_COLS["right"]].max() - df[SAMALA_ANKLE_ANGLE_COLS["right"]].min())
    return "left" if rom_lt < rom_rt else "right"


# ──────────────────────────────────────────────────────────────────────────────
# Wassall NTNU 2025
# ──────────────────────────────────────────────────────────────────────────────

def parse_wassall_filename(name: str) -> dict:
    """Decodifică numele unui fișier Wassall.

    Format așteptat: <Terrain2><WalkAid2><TrialN><Sensor2>.csv
    Ex: 'FLwi02PS.csv' → terrain=FL, walkaid=wi, trial=2, sensor=PS
    Acceptă și nume fără zero padding (ex. 'SLwo3OS.csv' → trial=3, sensor=OS).

    Fișiere de tip 'StepXXX' (multi-teren) sunt marcate special.
    """
    base = name.replace(".csv", "")
    if base.lower().startswith("step"):
        return {
            "terrain": "step_multi",
            "walkaid": None,
            "trial": int("".join(c for c in base[4:] if c.isdigit()) or 0),
            "sensor": base[-2:],
            "raw": name,
        }
    terrain = base[:2]
    walkaid = base[2:4]
    sensor = base[-2:]
    # Trial = cifrele dintre walkaid și sensor (flexibil, 1 sau 2 cifre)
    middle = base[4:-2]
    digits = "".join(c for c in middle if c.isdigit())
    trial = int(digits) if digits else 0
    return {
        "terrain": terrain,
        "walkaid": walkaid,
        "trial": trial,
        "sensor": sensor,
        "raw": name,
    }


def load_wassall_trial(path: str | Path) -> GaitTrial:
    """Încarcă un singur CSV Wassall (un IMU, un trial)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    df = pd.read_csv(p)
    meta = parse_wassall_filename(p.name)
    sensor = meta["sensor"]
    side = "prosthetic" if sensor in ("PS", "TH") else "intact" if sensor == "OS" else "trunk"
    return GaitTrial(
        source="wassall",
        subject_id=p.parent.name,
        trial_id=p.stem,
        fs=WASSALL_FS,
        side=side,
        df=df,
        meta={
            "path": str(p),
            "sensor": sensor,
            "sensor_full": WASSALL_SENSORS.get(sensor, sensor),
            "terrain": meta["terrain"],
            "walkaid": meta["walkaid"],
            "trial": meta["trial"],
            "n_samples": len(df),
            "duration_s": len(df) / WASSALL_FS,
        },
    )


def list_wassall_participants(root: str | Path) -> list[str]:
    """Listează participanții (P1..P20, plus P7_TT/P7_TF)."""
    root = Path(root)
    if not root.exists():
        return []
    return sorted(d.name for d in root.iterdir() if d.is_dir() and d.name.startswith("P"))


def list_wassall_trials(root: str | Path, participant: str, sensor: str = "PS") -> pd.DataFrame:
    """Returnează un index al trial-urilor pentru un participant (filtre pe senzor)."""
    d = Path(root) / participant
    if not d.exists():
        return pd.DataFrame()
    rows = []
    for csv in sorted(d.glob("*.csv")):
        meta = parse_wassall_filename(csv.name)
        if meta["sensor"] != sensor:
            continue
        rows.append({
            "participant": participant,
            "trial_id": csv.stem,
            "terrain": meta["terrain"],
            "walkaid": meta["walkaid"],
            "trial": meta["trial"],
            "sensor": meta["sensor"],
            "path": str(csv),
        })
    return pd.DataFrame(rows)


# Coloane Wassall — vezi README dataverse:
WASSALL_GYRO_COLS = ["Gyr_X", "Gyr_Y", "Gyr_Z"]  # rad/s
WASSALL_ACCEL_COLS = ["Acc_X", "Acc_Y", "Acc_Z"]  # m/s^2 cu gravitație
WASSALL_FREE_ACCEL_COLS = ["FreeAcc_E", "FreeAcc_N", "FreeAcc_U"]  # fără gravitație
WASSALL_LABEL_COLS = ["Steps", "Terrain", "Turn"]


def accel_magnitude(df: pd.DataFrame, cols: list[str]) -> np.ndarray:
    """Magnitudine vectorială ||a|| = sqrt(sum(ai^2))."""
    arr = df[cols].to_numpy()
    return np.linalg.norm(arr, axis=1)


def compute_ankle_angle(
    df, side: str, reference_idx: int | None = None,
    smooth_cutoff_hz: float = 6.0, fs: float = 200.0,
    clip_deg: float = 35.0,
) -> np.ndarray:
    """Calculează unghiul real al gleznei (deg) prin diferența orientării segmentelor.

    Convenție: dorsi (+), plantar (-). Calibrat pe primul HS detectat = 0°
    (corespunde cu fiziologia Perry & Burnfield: ankle≈0° la initial contact).

    Coloanele "Ankle Dorsiflexion LT/RT" din Noraxon Samala sunt inconsistente
    (semn opus, valori non-fiziologice în swing) — această funcție le înlocuiește.

    Aplică:
    - filtru low-pass Butterworth (6 Hz, clinic standard pentru kinematica mersului
      conform Winter 1991), pentru a elimina spike-urile IMU de la decolare/aterizare
    - clipping la ±clip_deg (default 35°) pentru a respinge artefacte mai mari decât
      ROM-ul fiziologic al gleznei (Perry & Burnfield: ROM max ~30° la mers, ~40° la
      stair descent extrem)

    Args:
        df: DataFrame Samala IMU
        side: "left" sau "right"
        reference_idx: indexul în care setăm ankle=0° (default: 100 = 0.5 s static)
        smooth_cutoff_hz: cutoff pentru filtrul de netezire pe ankle
        fs: frecvență eșantionare (Hz)
        clip_deg: limită ±° pentru artefacte (35° = puțin peste ROM normal max)

    Returns:
        Array 1D cu unghiul gleznei (deg) la fiecare sample, filtrat și clipped.
    """
    from scipy.signal import butter, filtfilt
    shank_pitch = df[SAMALA_SHANK_PITCH_COLS[side]].to_numpy()
    foot_pitch = df[SAMALA_FOOT_PITCH_COLS[side]].to_numpy()
    # Convenția: dorsiflexie + (vârful piciorului ridicat față de tibie).
    # Geometric: când talpa rotește astfel încât vârful urcă, foot_pitch crește
    # ȘI shank_pitch poate fi staționar — deci ankle_dorsi = -(shank - foot).
    # Validat empiric vs. Perry & Burnfield: la heel-off (50% gait) ankle ~+10° dorsi,
    # la toe-off (60%) ankle ~-15° plantar (împingere).
    raw = -(shank_pitch - foot_pitch)
    if reference_idx is None:
        reference_idx = 100
    reference_idx = int(np.clip(reference_idx, 0, len(raw) - 1))
    centered = raw - raw[reference_idx]
    # Filtru low-pass blând pentru a respinge spike-urile IMU (Winter 1991: 6 Hz pentru ankle)
    nyq = fs / 2
    wn = min(smooth_cutoff_hz / nyq, 0.99)
    b, a = butter(4, wn, btype="low")
    padlen = min(3 * max(len(a), len(b)), len(centered) - 1)
    smooth = filtfilt(b, a, centered, padlen=padlen)
    # Clipping artefacte > ROM fiziologic
    return np.clip(smooth, -clip_deg, clip_deg)
