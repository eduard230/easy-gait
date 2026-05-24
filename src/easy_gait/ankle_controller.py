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
