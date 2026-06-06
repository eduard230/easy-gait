"""Generare traiectorie continuă a unghiului gleznei dintr-un FSMTrace.

Metoda standard pentru controllere prosthetic (BiOM, Vanderbilt, SpringActive):
**Interpolare PCHIP** (Piecewise Cubic Hermite Interpolating Polynomial). PCHIP
garantează MONOTONIA între waypoint-uri — adică nu produce overshoot dincolo de
valorile setpoint-urilor. Asta e critic biomecanic: nu vrem ca traj să meargă în
dorsiflexie când FSM e în Push-Off (plantarflexie comandată).

Referințe:
- Lawson, Varol, Goldfarb 2014 (Vanderbilt) — folosesc impedance control cu
  setpoint trecut la începutul stării, nu interpolat la mijloc.
- Au & Herr 2008 (BiOM) — lookup table normalizată pe % gait cycle.
- Bartlett 2019/2021 — recomandă PCHIP/monotonic cubic peste Catmull-Rom.

Versiunea anterioară folosea CubicHermiteSpline cu derivate centrate, care
PRODUCEA OVERSHOOT vizibil (până la 22° peste setpoint!) — vezi commits anteriori.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

from easy_gait.fsm import FSMTrace


def generate_trajectory(
    trace: FSMTrace,
    fs: float,
    *,
    smooth_window_s: float = 0.04,
    waypoint_position: float = 0.30,
) -> np.ndarray:
    """Convertește setpoint-urile discrete în traiectorie continuă a unghiului gleznei.

    Algoritm:
    1. Pentru fiecare segment de stare, plasează un waypoint la `waypoint_position`
       din durata segmentului (default 30%, nu 50% — ca să atingă setpoint-ul
       devreme, nu la sfârșitul stării). Asta face traj să fie aproape de setpoint
       majoritatea timpului petrecut în acea stare.
    2. PchipInterpolator între waypoints — garantează monotonia, FĂRĂ overshoot.
    3. Moving-average minim pentru a netezi micile coturi.

    Args:
        trace: FSMTrace returnat de `fsm.run_fsm`
        fs: frecvență eșantionare (Hz)
        smooth_window_s: fereastra moving-average finală (s). Default 40ms.
        waypoint_position: unde plasăm waypoint-ul în segmentul stării (0..1).
            0.30 = early in state (traj urcă rapid la setpoint și-l ține).
            0.50 = mid (clasic Catmull, dar produce overshoot dacă derivata e mare).

    Returns:
        Array 1D de aceeași lungime cu starea, unghi țintă în grade.
    """
    n = len(trace.state_per_sample)
    transitions = trace.transitions
    if not transitions:
        return trace.setpoint_per_sample.copy()

    # Construire segmente
    starts = [0] + [t[0] for t in transitions]
    ends = [t[0] for t in transitions] + [n]

    xs: list[float] = []
    ys: list[float] = []
    # Anchor la t=0 cu prima valoare
    xs.append(0.0)
    ys.append(float(trace.setpoint_per_sample[0]))

    for s, e in zip(starts, ends):
        if e - s < 1:
            continue
        sp_val = float(trace.setpoint_per_sample[s])
        # Waypoint plasat la waypoint_position din intervalul stării
        x = s + waypoint_position * (e - s)
        # Evită duplicate
        if xs and x <= xs[-1]:
            x = xs[-1] + 1.0
        xs.append(float(x))
        ys.append(sp_val)

    # Anchor la n
    if xs[-1] < n - 1:
        xs.append(float(n - 1))
        ys.append(float(trace.setpoint_per_sample[-1]))

    xs_arr = np.asarray(xs, dtype=float)
    ys_arr = np.asarray(ys, dtype=float)

    if len(xs_arr) < 2:
        return trace.setpoint_per_sample.copy()

    # PCHIP — monotonic between waypoints, no overshoot
    spline = PchipInterpolator(xs_arr, ys_arr, extrapolate=True)
    t_all = np.arange(n, dtype=float)
    traj = spline(t_all)

    # Smoothing minim
    win = max(int(smooth_window_s * fs), 3)
    if win % 2 == 0:
        win += 1
    if win < len(traj):
        kernel = np.ones(win) / win
        traj = np.convolve(traj, kernel, mode="same")
    return traj


# ──────────────────────────────────────────────────────────────────────────────
# Bucla de impedanță: din θ_eq comandat → θ observat (model fizic)
# ──────────────────────────────────────────────────────────────────────────────
#
# Setpoint-urile FSM sunt echilibre VIRTUALE de impedanță (θ_eq), nu unghiuri
# observate. Unghiul real al gleznei rezultă din relația de impedanță (Sup,
# Bohara & Goldfarb 2008; Hogan 1985):
#
#     τ = K · (θ_eq − θ_obs) + B · (−θ̇_obs)         (cuplul gleznei)
#
# La echilibru cvasi-static în stance (θ̇ ≈ 0) și sub momentul extern produs de
# GRF (M_ext), deflexia față de echilibru este M_ext / K, deci:
#
#     θ_obs ≈ θ_eq + M_ext / K
#
# unde M_ext (moment dorsiflexor extern, pozitiv = împinge glezna în dorsiflexie)
# este produs de forța de reacție verticală a solului (GRF) acționând pe brațul
# de pârghie posterior față de gleznă în timpul rocker-ului de stance. Asta
# explică de ce unghiul OBSERVAT crește în dorsiflexie pe stance (rocker), chiar
# dacă echilibrul COMANDAT (θ_eq) scade monoton spre plantarflexie pentru push-off.


# Profil GRF vertical normativ pentru un ciclu de mers (Winter 1991; Sanderson
# & Martin 1997): forma „M" cu două vârfuri (loading response ~1.1·BW la ~15%
# gait cycle, push-off ~1.1·BW la ~50%), zero în swing. Normalizat la greutatea
# corporală (BW). 101 puncte = 0..100% gait cycle.
_GRF_PCT = np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 62,
                     65, 70, 100], dtype=float)
_GRF_BW = np.array([0.0, 0.6, 1.0, 1.10, 1.02, 0.85, 0.78, 0.82, 0.95, 1.08,
                    1.12, 0.95, 0.45, 0.10, 0.0, 0.0, 0.0], dtype=float)


def grf_vertical_profile(n_points: int = 101) -> np.ndarray:
    """Profil GRF vertical normativ (×BW) pe 0-100% gait cycle (formă „M")."""
    x = np.linspace(0.0, 100.0, n_points)
    return np.interp(x, _GRF_PCT, _GRF_BW)


def grf_for_phase(phase_pct: np.ndarray) -> np.ndarray:
    """GRF vertical (×BW) evaluat la un vector de faze (% gait cycle, 0..100)."""
    return np.interp(np.clip(phase_pct, 0.0, 100.0), _GRF_PCT, _GRF_BW)


def observed_angle_from_impedance(
    theta_eq_deg: np.ndarray,
    phase_pct: np.ndarray,
    *,
    stiffness_nm_per_deg: float = 3.0,
    body_weight_n: float = 750.0,
    moment_arm_m: float = 0.06,
    grf_to_dorsi_sign: float = +1.0,
) -> np.ndarray:
    """Estimează unghiul OBSERVAT al gleznei din echilibrul de impedanță + GRF.

    θ_obs = θ_eq + (M_ext / K), unde M_ext = grf_to_dorsi_sign · GRF(phase) ·
    body_weight · moment_arm. Momentul dorsiflexor extern (rocker de stance)
    împinge glezna în dorsiflexie peste echilibrul comandat.

    Args:
        theta_eq_deg: echilibrul de impedanță comandat per sample (deg) — ieșirea
            FSM (`generate_trajectory`).
        phase_pct: faza ciclului de mers per sample (0..100%), pentru a evalua GRF.
        stiffness_nm_per_deg: rigiditatea impedanței K (N·m/deg). Valori tipice
            de gleznă în stance: 2-5 N·m/deg (Hansen 2004; Shamaei 2013).
        body_weight_n: greutatea corporală (N) — scalează GRF din ×BW în N.
        moment_arm_m: brațul de pârghie efectiv GRF→gleznă (m). ~0.05-0.08 m.
        grf_to_dorsi_sign: +1 dacă GRF produce moment dorsiflexor (rocker normal).

    Returns:
        θ_obs (deg), aceeași lungime cu theta_eq_deg.
    """
    grf_bw = grf_for_phase(phase_pct)                  # ×BW
    m_ext = grf_to_dorsi_sign * grf_bw * body_weight_n * moment_arm_m   # N·m
    deflection_deg = m_ext / max(stiffness_nm_per_deg, 1e-6)
    return theta_eq_deg + deflection_deg


def phase_from_states(state_per_sample: np.ndarray, hs_idx: np.ndarray,
                      n_samples: int) -> np.ndarray:
    """Estimează faza ciclului (0..100%) per sample, din indici HS consecutivi.

    Între HS_i și HS_{i+1}, faza crește liniar 0→100. În afara primului/ultimului
    HS, se extrapolează la marginea cea mai apropiată.
    """
    phase = np.zeros(n_samples, dtype=float)
    hs = [int(h) for h in hs_idx]
    if len(hs) < 2:
        return phase
    for i in range(len(hs) - 1):
        a, b = hs[i], hs[i + 1]
        if b <= a:
            continue
        phase[a:b] = np.linspace(0.0, 100.0, b - a, endpoint=False)
    phase[:hs[0]] = 0.0
    phase[hs[-1]:] = 0.0
    return phase
