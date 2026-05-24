"""Detecție evenimente HS/TO din date OMC (motion capture), ground truth pentru
validarea algoritmilor pe IMU.

## Algoritm Zeni 2008 — standard gold în literatura clinică

Zeni J.A., Richards J.G., Higginson J.S. (2008) "Two simple methods for determining
gait events during treadmill and overground walking using kinematic data."
Gait & Posture 27(4):710-714.

Algoritmul folosește poziția X (direcția de mers) a markerilor în raport cu un
punct de referință proximal (sacrum sau centru pelvis):
  - HS (Heel Strike) = maxim local al (HEEL.x − SACRUM.x)
  - TO (Toe Off) = minim local al (TOE.x − SACRUM.x)

Avantaje față de detecția pe înălțime verticală (Z):
  - Robust la variații de înălțime (treadmill incline, salturi minime de marker)
  - Citat în peste 2000 lucrări biomecanice
  - Aplicabil atât pe treadmill cât și pe overground walking

## Markeri Samala 2024 disponibili

Per `[OMC]SXX_WalkingN.c3d`:
  - HEEL_L / HEEL_R: marker pe călcâi
  - MTH1_L / MTH1_R: metatarsal head 1 (folosit ca toe)
  - MTH3_L / MTH3_R, MTH5_L / MTH5_R: alți metatarsali (alternative)
  - PELVIS_R / PELVIS_L: markeri lateral pelvis → mid = pelvis center (proxy sacrum)

## Detalii implementare

  - Filtru low-pass Butterworth 6 Hz pe pozițiile markerilor (standard Winter 1991
    pentru kinematica articulară la mers)
  - Maxim/minim local detectat cu `scipy.signal.find_peaks` cu distanță minimă
    între evenimente (0.4 s) pentru a evita dublu-trigger
  - Frecvență Samala OMC = 200 Hz (confirmat din `RATE` în C3D)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


@dataclass
class OMCEvents:
    """Evenimente HS/TO derivate din OMC pentru un singur picior."""
    hs_idx: np.ndarray  # indici frame OMC pentru Heel Strike
    to_idx: np.ndarray  # indici frame OMC pentru Toe Off
    fs: float           # frecvența OMC (Hz)
    side: str           # "left" | "right"
    n_frames: int       # nr. total frame-uri trial


def load_c3d_markers(path: str | Path) -> dict:
    """Citește un fișier C3D și returnează markerii ca dict.

    Returns:
        dict cu chei: 'fs' (Hz), 'n_frames' (int), 'markers' (dict marker_name -> array 3 x n_frames în mm).
    """
    import ezc3d
    c = ezc3d.c3d(str(path))
    labels = c['parameters']['POINT']['LABELS']['value']
    rate = float(c['parameters']['POINT']['RATE']['value'][0])
    pts = c['data']['points']  # shape (4, n_markers, n_frames) — [x,y,z,residual]
    markers = {label: pts[:3, i, :] for i, label in enumerate(labels)}
    return {
        'fs': rate,
        'n_frames': pts.shape[2],
        'markers': markers,
        'units': c['parameters']['POINT']['UNITS']['value'][0],
    }


def _lowpass_filter(x: np.ndarray, fs: float, cutoff_hz: float = 6.0, order: int = 4) -> np.ndarray:
    """Butterworth low-pass zero-phase pe semnal 1D (filtfilt)."""
    nyq = fs / 2
    wn = min(cutoff_hz / nyq, 0.99)
    b, a = butter(order, wn, btype='low')
    padlen = min(3 * max(len(a), len(b)), len(x) - 1)
    return filtfilt(b, a, x, padlen=padlen)


def detect_events_zeni(
    heel_xyz: np.ndarray,        # 3 x n_frames, marker HEEL
    toe_xyz: np.ndarray,          # 3 x n_frames, marker MTH (toe proxy)
    pelvis_center_xyz: np.ndarray,  # 3 x n_frames, mid PELVIS_L/R (sacrum proxy)
    fs: float,
    *,
    min_event_gap_s: float = 0.4,
    cutoff_hz: float = 6.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Detecție HS/TO via Zeni 2008 — folosește direcția de mers (X) relativă la pelvis.

    Args:
        heel_xyz, toe_xyz, pelvis_center_xyz: arrays 3 x n_frames (mm).
        fs: frecvența OMC (Hz).
        min_event_gap_s: distanța minimă între două evenimente consecutive.
        cutoff_hz: cutoff filtru pe poziții markeri.

    Returns:
        (hs_idx, to_idx) — arrays cu indici de frame OMC.
    """
    n = heel_xyz.shape[1]
    if n < int(fs * 0.5):  # mai puțin de 0.5 s, prea scurt
        return np.array([], dtype=int), np.array([], dtype=int)

    # Direcția X = direcția dominantă de mers; verificăm că e cea cu range maxim
    ranges = np.ptp(pelvis_center_xyz, axis=1)
    walk_axis = int(np.argmax(ranges))  # de obicei 0 (X)

    heel_rel = heel_xyz[walk_axis] - pelvis_center_xyz[walk_axis]
    toe_rel = toe_xyz[walk_axis] - pelvis_center_xyz[walk_axis]

    heel_rel_f = _lowpass_filter(heel_rel, fs, cutoff_hz)
    toe_rel_f = _lowpass_filter(toe_rel, fs, cutoff_hz)

    min_gap_samples = int(min_event_gap_s * fs)

    # HS = max local pe (heel - pelvis).x → călcâiul cel mai în față față de centrul corpului
    hs_idx, _ = find_peaks(heel_rel_f, distance=min_gap_samples)
    # TO = min local pe (toe - pelvis).x → vârful cel mai în spate față de centrul corpului
    to_idx, _ = find_peaks(-toe_rel_f, distance=min_gap_samples)

    return hs_idx.astype(int), to_idx.astype(int)


def detect_omc_events_from_c3d(
    c3d_path: str | Path,
    side: str,                # 'left' | 'right'
    *,
    toe_marker: str = 'MTH3',  # MTH1, MTH3 (default — mijloc), MTH5
) -> OMCEvents:
    """Wrapper care încarcă un C3D Samala și returnează evenimente OMC pe un picior.

    Args:
        c3d_path: cale către `[OMC]SXX_WalkingN.c3d`.
        side: 'left' sau 'right'.
        toe_marker: care marker MTH se folosește ca toe (MTH3 = mijloc, recomandat).

    Returns:
        OMCEvents cu hs_idx și to_idx.
    """
    suffix = 'L' if side.lower().startswith('l') else 'R'
    data = load_c3d_markers(c3d_path)
    m = data['markers']

    heel_key = f'HEEL_{suffix}'
    toe_key = f'{toe_marker}_{suffix}'
    if heel_key not in m or toe_key not in m:
        raise KeyError(f"Markers missing in C3D: need {heel_key} and {toe_key}, found: {list(m.keys())[:20]}")

    # Centrul pelvisului = media (PELVIS_L + PELVIS_R)
    if 'PELVIS_L' in m and 'PELVIS_R' in m:
        pelvis_center = (m['PELVIS_L'] + m['PELVIS_R']) / 2.0
    elif 'PELVIS_SUP' in m:
        pelvis_center = m['PELVIS_SUP']
    else:
        # Fallback: media ASIS_L + ASIS_R
        pelvis_center = (m['ASIS_L'] + m['ASIS_R']) / 2.0

    hs_idx, to_idx = detect_events_zeni(
        heel_xyz=m[heel_key],
        toe_xyz=m[toe_key],
        pelvis_center_xyz=pelvis_center,
        fs=data['fs'],
    )
    return OMCEvents(
        hs_idx=hs_idx, to_idx=to_idx,
        fs=data['fs'], side=side, n_frames=data['n_frames'],
    )


def samala_c3d_path(root: str | Path, subject: str, trial: int) -> Path:
    """Calea către `[OMC]SXX_WalkingN.c3d`."""
    return Path(root) / subject / f"[OMC]{subject}_Walking{trial}.c3d"


def align_omc_to_imu(
    imu_signal: np.ndarray,
    omc_signal: np.ndarray,
    fs_imu: float = 200.0,
    fs_omc: float = 200.0,
) -> int:
    """Aliniază fereastra OMC peste semnalul IMU complet via cross-correlation.

    Datasetul Samala 2024 furnizează IMU pentru întregul trial (~14 s) iar OMC
    pentru doar fereastra de captură mocap (~4.5 s). Pentru a compara evenimente
    și traiectorii, găsim offset-ul OMC-în-IMU prin cross-correlation pe
    semnalul de aliniere (de obicei unghiul gleznei).

    Args:
        imu_signal: semnal 1D din IMU (ex. ankle_real lungime ~2800).
        omc_signal: semnal 1D din OMC (lungime ~900).
        fs_imu, fs_omc: frecvențe (Hz). Asumăm egale pentru Samala.

    Returns:
        Indexul în IMU unde începe fereastra OMC. Ex. 820 = OMC corespunde IMU[820:820+len(omc)].
    """
    from scipy.signal import correlate

    if fs_imu != fs_omc:
        raise ValueError(f"Cross-correlation requires equal sample rates; "
                         f"got IMU={fs_imu}, OMC={fs_omc}")
    if len(omc_signal) >= len(imu_signal):
        return 0
    imu_norm = (imu_signal - np.mean(imu_signal)) / (np.std(imu_signal) + 1e-9)
    omc_norm = (omc_signal - np.mean(omc_signal)) / (np.std(omc_signal) + 1e-9)
    xcorr = correlate(imu_norm, omc_norm, mode='valid')
    return int(np.argmax(xcorr))
