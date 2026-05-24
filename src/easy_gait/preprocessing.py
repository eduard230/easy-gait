"""Preprocesare semnale IMU: filtrare zero-phase, magnitudine, derivare numerică.

Bazat pe:
- Catalfamo P., Ghoussayni S., Ewins D. (2010). *Gait Event Detection on Level Ground
  and Incline Walking Using a Rate Gyroscope.* Sensors 10(6):5683-5702.
- Yu B., Gabriel D., Noble L., An K.N. (1999). *Estimate of the Optimum Cutoff
  Frequency for the Butterworth Low-Pass Digital Filter.* J Appl Biomech 15(3):318-329.
- Pacini Panebianco G., et al. (2018). Gait & Posture 66:76-82.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt


def butter_lowpass(
    signal: np.ndarray,
    fs: float,
    cutoff_hz: float = 15.0,
    order: int = 4,
) -> np.ndarray:
    """Filtru Butterworth low-pass zero-phase (filtfilt).

    Aplicarea zero-phase elimină defazarea — esențial pentru ca timpii evenimentelor
    detectate să fie nedistorsionați (recomandare uniformă în literatura gait).

    Args:
        signal: array 1D
        fs: frecvență eșantionare (Hz)
        cutoff_hz: frecvență tăiere (Hz). Default 15 Hz pentru gait standard
                   pe gyro shank la fs=200 Hz (Catalfamo 2010, Pacini Panebianco 2018).
        order: ordinul filtrului (filtfilt dublează efectul → ordin efectiv 2*order).

    Returns:
        signal filtrat, aceeași formă.
    """
    if signal.ndim != 1:
        raise ValueError(f"Expected 1D array, got shape {signal.shape}")
    nyq = 0.5 * fs
    wn = cutoff_hz / nyq
    if not 0 < wn < 1:
        raise ValueError(f"cutoff {cutoff_hz} Hz invalid pentru fs={fs} Hz")
    b, a = butter(order, wn, btype="low")
    # padlen explicit pentru semnale scurte
    padlen = min(3 * max(len(a), len(b)), len(signal) - 1)
    return filtfilt(b, a, signal, padlen=padlen)


def butter_lowpass_df(
    df, cols: list[str], fs: float, cutoff_hz: float = 15.0, order: int = 4
):
    """Aplică Butterworth low-pass pe un set de coloane dintr-un DataFrame.

    Returns:
        DataFrame cu aceleași coloane, valori filtrate.
    """
    out = df[cols].copy()
    for c in cols:
        out[c] = butter_lowpass(df[c].to_numpy(), fs=fs, cutoff_hz=cutoff_hz, order=order)
    return out


def derivative(signal: np.ndarray, fs: float) -> np.ndarray:
    """Derivată numerică centrată (gradient)."""
    return np.gradient(signal, 1.0 / fs)


def gyro_pitch_dps(df, axis_col: str, fs: float, cutoff_hz: float = 15.0) -> np.ndarray:
    """Derivă viteza unghiulară (deg/s) din unghiul (deg) prin diferențiere + filtrare.

    Util pentru datasetul Samala unde Noraxon furnizează doar unghiuri shank
    (pitch în deg), nu giroscop direct. Pentru Wassall avem Gyr_Y direct în rad/s.
    """
    angle = df[axis_col].to_numpy()
    omega = derivative(angle, fs)  # deg/s
    return butter_lowpass(omega, fs=fs, cutoff_hz=cutoff_hz)


def normalize_to_g(accel_ms2: np.ndarray) -> np.ndarray:
    """m/s² → g (9.80665 m/s²)."""
    return accel_ms2 / 9.80665


def detect_quiet_segments(
    omega: np.ndarray, threshold_dps: float = 30.0, min_samples: int = 25
) -> np.ndarray:
    """Returnează indici unde |ω| < prag pentru cel puțin min_samples consecutive.

    Folosit pentru detecția foot-flat (mid-stance) în FSM. Default 25 samples
    @ 200 Hz = 125 ms quiet — peste limita 50 ms recomandată de Skvortsov 2023.
    """
    quiet = np.abs(omega) < threshold_dps
    # Rulare lungimi consecutive
    out = np.zeros_like(quiet, dtype=bool)
    i = 0
    n = len(quiet)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if j - i >= min_samples:
                out[i:j] = True
            i = j
        else:
            i += 1
    return out
