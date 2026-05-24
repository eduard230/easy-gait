"""Detecție Heel Strike (HS) și Toe Off (TO) din IMU shank.

Două variante complementare, ambele explicabile, deterministe:

(A) `detect_events_trojaniello` — gold-standard offline pe gyro tibial pitch.
    Bazat pe Aminian 2002, Salarian 2004, Trojaniello 2014.

(B) `detect_events_maqbool` — real-time, prietenos pentru FSM.
    Bazat pe Maqbool 2017 (referința directă pentru amputat lower-limb).

Convenție IMU shank pitch sagital:
- Vârf pozitiv (~+200..+400 deg/s) la mid-swing când tibia se mișcă înainte.
- Minim negativ la HS (~−100 deg/s) — tibia decelerează brusc la impact.
- Minim negativ la TO (~−30..−100 deg/s) înaintea peak-ului de swing.

Validare: comparație cu evenimente derivate din OMC (Samala) sau cu strides
marcate (Wassall — coloana Steps).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import find_peaks

from easy_gait.preprocessing import butter_lowpass


@dataclass
class GaitEvents:
    """Indici și timpi pentru evenimentele detectate într-un trial."""
    hs_idx: np.ndarray            # indici sample (HS = initial contact)
    to_idx: np.ndarray            # indici sample (TO = terminal contact)
    fs: float                     # frecvență eșantionare
    method: str                   # "trojaniello" | "maqbool"

    @property
    def hs_t(self) -> np.ndarray:
        """Timpii HS în secunde."""
        return self.hs_idx / self.fs

    @property
    def to_t(self) -> np.ndarray:
        """Timpii TO în secunde."""
        return self.to_idx / self.fs


# ──────────────────────────────────────────────────────────────────────────────
# (A) Trojaniello-Salarian
# ──────────────────────────────────────────────────────────────────────────────

def detect_events_trojaniello(
    shank_pitch_rate: np.ndarray,
    fs: float,
    *,
    prosthetic: bool = False,
    min_stride_s: float = 0.5,
    hs_window_s: tuple[float, float] = (0.0, 0.35),
    to_window_s: tuple[float, float] = (-0.45, -0.10),
    cutoff_hz: float = 15.0,
) -> GaitEvents:
    """Detecție HS/TO offline pe baza vitezei unghiulare a tibiei (pitch sagital).

    Procedură (Trojaniello 2014, Aminian 2002):
    1. Filtrare Butterworth low-pass, zero-phase, fc=15 Hz, ord. 4.
    2. Vârfuri mid-swing: peaks_MS pe semnal filtrat, prag adaptiv 0.6 × P95.
    3. Pentru fiecare peak P_i la t_i:
       - HS = minim local în fereastra [t_i, t_i + 350 ms], prag ω < -20°/s.
       - TO = minim local în fereastra [t_i − 450 ms, t_i − 100 ms], prag ω < -10°/s.
    4. Pentru picior protetic: relaxare praguri la 60% (Maqbool 2017).

    Args:
        shank_pitch_rate: viteza unghiulară shank pitch (deg/s). Pentru Samala,
            derivă din unghi pitch via `preprocessing.gyro_pitch_dps`.
            Pentru Wassall, e direct Gyr_Y convertit în deg/s.
        fs: frecvență eșantionare (Hz).
        prosthetic: dacă True, relaxează pragurile cu 0.6.
        min_stride_s: durata minimă între vârfuri mid-swing.
        hs_window_s: fereastra (relativ la peak MS) în care căutăm HS.
        to_window_s: fereastra (relativ la peak MS) în care căutăm TO.
        cutoff_hz: cutoff filtru.

    Returns:
        GaitEvents cu hs_idx și to_idx.
    """
    omega = butter_lowpass(shank_pitch_rate, fs=fs, cutoff_hz=cutoff_hz)
    n = len(omega)

    # 1) Praguri adaptive
    p95 = float(np.percentile(omega, 95))
    if p95 <= 0:
        return GaitEvents(np.array([], int), np.array([], int), fs, "trojaniello")
    peak_height = 0.6 * p95
    scale = 0.6 if prosthetic else 1.0
    hs_thr = -20.0 * scale
    to_thr = -10.0 * scale

    # 2) Detecție vârfuri mid-swing
    min_dist = int(min_stride_s * fs)
    peaks, _ = find_peaks(omega, height=peak_height, distance=min_dist)

    hs_idx: list[int] = []
    to_idx: list[int] = []

    hs_w_lo = int(hs_window_s[0] * fs)
    hs_w_hi = int(hs_window_s[1] * fs)
    to_w_lo = int(to_window_s[0] * fs)
    to_w_hi = int(to_window_s[1] * fs)

    for p in peaks:
        # 3a) HS: minim local în fereastra după peak
        lo, hi = max(0, p + hs_w_lo), min(n, p + hs_w_hi)
        if hi - lo > 2:
            local = omega[lo:hi]
            i = int(np.argmin(local))
            val = float(local[i])
            if val <= hs_thr:
                hs_idx.append(lo + i)

        # 3b) TO: minim local în fereastra dinainte de peak
        lo, hi = max(0, p + to_w_lo), max(1, p + to_w_hi)
        if hi - lo > 2:
            local = omega[lo:hi]
            i = int(np.argmin(local))
            val = float(local[i])
            if val <= to_thr:
                to_idx.append(lo + i)

    return GaitEvents(
        hs_idx=np.asarray(sorted(set(hs_idx)), dtype=int),
        to_idx=np.asarray(sorted(set(to_idx)), dtype=int),
        fs=fs,
        method="trojaniello",
    )


# ──────────────────────────────────────────────────────────────────────────────
# (B) Maqbool R-GEDS (real-time)
# ──────────────────────────────────────────────────────────────────────────────

def detect_events_maqbool(
    shank_pitch_rate: np.ndarray,
    shank_accel_mag: np.ndarray,
    fs: float,
    *,
    prosthetic: bool = False,
    omega_swing_in_dps: float = 50.0,
    omega_hs_dps: float = -100.0,
    accel_hs_g: float = 1.5,
    t_min_swing_s: float = 0.2,
    refractary_s: float = 0.25,
    cutoff_hz: float = 15.0,
) -> GaitEvents:
    """Detecție HS/TO real-time prin state machine (Maqbool 2017).

    Stări: STANCE → SWING → HS_PENDING → STANCE.

    Praguri adaptate pentru picior protetic (impact atenuat de elasticitatea
    piciorului SACH / carbon spring).

    Args:
        shank_pitch_rate: viteza unghiulară shank pitch (deg/s).
        shank_accel_mag: magnitudine accelerație shank (m/s²) — pentru confirmare HS.
        fs: frecvență eșantionare (Hz).
        prosthetic: dacă True, scalează ω_HS la -60 dps, a_HS la 1.2 g.
        omega_swing_in_dps: prag tranziție STANCE → SWING.
        omega_hs_dps: prag detecție candidat HS (semnal devenit foarte negativ).
        accel_hs_g: prag confirmare HS pe magnitudine accelerație.
        t_min_swing_s: timp minim petrecut în SWING (anti-bouncing).
        refractary_s: refractary post-HS până la următorul TO posibil.
        cutoff_hz: cutoff filtru.

    Returns:
        GaitEvents cu hs_idx și to_idx.
    """
    omega = butter_lowpass(shank_pitch_rate, fs=fs, cutoff_hz=cutoff_hz)
    a_mag = shank_accel_mag  # nefiltrată — vrem spike-uri de impact
    a_g = a_mag / 9.80665

    if prosthetic:
        omega_hs_dps = -60.0
        accel_hs_g = 1.2

    n = len(omega)
    min_swing = int(t_min_swing_s * fs)
    refract = int(refractary_s * fs)

    state = "STANCE"
    t_to = -refract
    t_last_hs = -refract

    hs_idx: list[int] = []
    to_idx: list[int] = []

    for i in range(n):
        if state == "STANCE":
            if omega[i] > omega_swing_in_dps and (i - t_last_hs) > refract:
                to_idx.append(i)
                t_to = i
                state = "SWING"
        elif state == "SWING":
            if (i - t_to) > min_swing and omega[i] < omega_hs_dps:
                state = "HS_PENDING"
        elif state == "HS_PENDING":
            if a_g[i] > accel_hs_g:
                hs_idx.append(i)
                t_last_hs = i
                state = "STANCE"
            # fallback: dacă |a| nu confirmă în 200 ms, acceptă pe ω
            elif (i - t_to) > int(0.6 * fs):
                hs_idx.append(i)
                t_last_hs = i
                state = "STANCE"

    return GaitEvents(
        hs_idx=np.asarray(hs_idx, dtype=int),
        to_idx=np.asarray(to_idx, dtype=int),
        fs=fs,
        method="maqbool",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Helpers comune
# ──────────────────────────────────────────────────────────────────────────────

def pair_hs_to(events: GaitEvents) -> list[tuple[int, int, int]]:
    """Împerechere [HS_i, TO_i, HS_{i+1}] pentru cicluri complete.

    Doar perechi unde TO se află strict între HS_i și HS_{i+1}.
    """
    hs = events.hs_idx
    to = events.to_idx
    cycles = []
    for i in range(len(hs) - 1):
        a, c = int(hs[i]), int(hs[i + 1])
        # TO între a și c
        candidates = [int(t) for t in to if a < t < c]
        if candidates:
            cycles.append((a, candidates[0], c))
    return cycles
