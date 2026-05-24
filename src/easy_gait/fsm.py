"""Finite State Machine pentru simularea controlului unghiular al gleznei protetice.

5 stări, bazat pe Au & Herr 2008, Sup 2008, Eilenberg 2010, Bartlett 2021:
    S1 Loading Response  ← HS detectat
    S2 Mid-Stance        ← foot-flat (|ω_shank| < 30°/s timp 50 ms)
    S3 Push-Off          ← dorsiflexie > +8°
    S4 Early Swing       ← TO detectat
    S5 Late Swing        ← shank pitch peak (mid-swing)

Convenție unghi gleznă: dorsiflexie pozitivă (+), plantarflexie negativă (−),
gleznă neutră = 0°.

Tabelul de setpoint-uri și pragurile de tranziție sunt parametrizate per activitate
(level, stair_ascent, stair_descent, slope_up, slope_down) — vezi `SETPOINTS`.

Toleranță la erori: dacă evenimentul așteptat nu apare în max_dwell·median_T,
tranziție forțată (Varol, Sup & Goldfarb 2010).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Callable

import numpy as np


class AnkleState(IntEnum):
    S1_LOADING = 1
    S2_MIDSTANCE = 2
    S3_PUSHOFF = 3
    S4_EARLY_SWING = 4
    S5_LATE_SWING = 5


# Setpoint-uri ankle (deg) per stare — interpretate ca **echilibre virtuale**
# de impedanță (impedance equilibrium θ_eq), nu ca unghiuri observate fiziologic.
#
# Valorile pentru level walking sunt ancorate direct în Sup, Bohara & Goldfarb 2008
# (Int J Robot Res 27(2):263-273), Tabel 5: ankle θ_eq = {Mode 1: -8°, Mode 2: -25°,
# Mode 3: 0°, Mode 4: -3°}. Pentru cele 5 stări FSM ale noastre, am interpolat
# Mode 1 (loading→mid-stance) într-o pereche S1/S2.
#
# Această convenție impedance-style PRODUCE o curbă monoton descrescătoare în stance
# (de la -8° la -25° push-off), eliminând "balansul" vizual care apărea când foloseam
# unghiuri observate fiziologic ca setpoints (ex. mid-stance +3° dorsi). În controllere
# reale (Au & Herr 2008 BiOM/Empower, Sup 2008 Vanderbilt), stance este controlat prin
# impedanță (stiffness K + echilibru), NU prin trajectory tracking de poziție.
#
# Pentru stair/slope, valorile sunt scalate proporțional din Sup, Varol & Goldfarb 2012
# (IEEE T-NSRE 20:654) și Bartlett, King, Goldfarb & Lawson 2021 (IEEE T-NSRE 29:320).
SETPOINTS: dict[str, dict[AnkleState, float]] = {
    "level": {
        # Sup 2008 Table 5 ankle θ_eq, interpolate la 5 stări
        AnkleState.S1_LOADING: -8.0,        # Sup Mode 1 start
        AnkleState.S2_MIDSTANCE: -15.0,     # interpolat Sup Mode 1 → Mode 2
        AnkleState.S3_PUSHOFF: -25.0,       # Sup Mode 2
        AnkleState.S4_EARLY_SWING: -5.0,    # interpolat Sup Mode 3 → Mode 4
        AnkleState.S5_LATE_SWING: -3.0,     # Sup Mode 4
    },
    "stair_ascent": {
        # Sup 2012 stair ascent: reducere amplitudine push-off, mai puțin plantar
        AnkleState.S1_LOADING: -3.0,
        AnkleState.S2_MIDSTANCE: -8.0,
        AnkleState.S3_PUSHOFF: -18.0,
        AnkleState.S4_EARLY_SWING: -3.0,
        AnkleState.S5_LATE_SWING: 0.0,
    },
    "stair_descent": {
        # Sup 2012 stair descent: dorsi-flexie controlată în loading + plantar puternic
        AnkleState.S1_LOADING: -15.0,
        AnkleState.S2_MIDSTANCE: -20.0,
        AnkleState.S3_PUSHOFF: -30.0,
        AnkleState.S4_EARLY_SWING: -15.0,
        AnkleState.S5_LATE_SWING: -8.0,
    },
    "slope_ascent": {
        # Bartlett 2021 sloped walking, panta urcată: similar level dar deplasat ușor
        AnkleState.S1_LOADING: -5.0,
        AnkleState.S2_MIDSTANCE: -12.0,
        AnkleState.S3_PUSHOFF: -22.0,
        AnkleState.S4_EARLY_SWING: -3.0,
        AnkleState.S5_LATE_SWING: -1.0,
    },
    "slope_descent": {
        # Bartlett 2021 sloped walking, panta coborâtă: plantar mai accentuat
        AnkleState.S1_LOADING: -12.0,
        AnkleState.S2_MIDSTANCE: -18.0,
        AnkleState.S3_PUSHOFF: -28.0,
        AnkleState.S4_EARLY_SWING: -10.0,
        AnkleState.S5_LATE_SWING: -5.0,
    },
}


@dataclass
class FSMConfig:
    activity: str = "level"
    foot_flat_omega_thr_dps: float = 30.0     # |ω_shank| sub care e foot-flat
    foot_flat_min_samples: int = 10           # nr. samples consecutiv (50 ms @ 200 Hz)
    pushoff_dorsi_thr_deg: float = 3.0        # prag dorsi pentru S2→S3; relaxat de la 8°
                                              # (literatura BiOM, subiecți healthy) la 3°
                                              # pentru a se declanșa și pe purtători cu ROM redus.
                                              # Dacă tot nu se atinge, FSM cade pe timeout.
    pushoff_phase_fraction: float = 0.45      # forțează S2→S3 la 45% din median stride
                                              # dacă pragul de unghi nu e atins (fallback)
    max_dwell_factor: float = 1.5             # timeout absolut = max_dwell * median_stride
    midswing_window_s: tuple[float, float] = (0.15, 0.35)  # de la TO

    def setpoints(self) -> dict[AnkleState, float]:
        return SETPOINTS[self.activity]


@dataclass
class FSMTrace:
    """Evoluția stărilor în timp + traiectoria țintă a unghiului gleznei."""
    state_per_sample: np.ndarray         # AnkleState int per sample
    setpoint_per_sample: np.ndarray      # setpoint discret per sample (deg)
    transitions: list[tuple[int, AnkleState]] = field(default_factory=list)  # (idx, new_state)


def run_fsm(
    n_samples: int,
    fs: float,
    hs_idx: np.ndarray,
    to_idx: np.ndarray,
    omega_shank_dps: np.ndarray,
    ankle_angle_estimate_deg: np.ndarray | None = None,
    config: FSMConfig | None = None,
) -> FSMTrace:
    """Rulează FSM cauzal pe semnal IMU și evenimente date.

    Args:
        n_samples: numărul total de samples
        fs: frecvență eșantionare (Hz)
        hs_idx, to_idx: indici evenimente HS și TO (din `gait_events`)
        omega_shank_dps: viteza unghiulară shank pitch (deg/s)
        ankle_angle_estimate_deg: opțional, unghi gleznă curent — folosit doar
            pentru trigger-ul S2 → S3 (push-off când dorsi > prag). Dacă None,
            tranziția S2→S3 e bazată exclusiv pe timeout.
        config: parametri FSM.

    Returns:
        FSMTrace cu starea per sample, setpoint per sample și lista tranzițiilor.
    """
    cfg = config or FSMConfig()
    sp = cfg.setpoints()

    # Estimare durată mediană stride pentru timeout
    if len(hs_idx) > 1:
        median_stride = int(np.median(np.diff(hs_idx)))
    else:
        median_stride = int(1.0 * fs)
    max_dwell = max(int(cfg.max_dwell_factor * median_stride), int(0.3 * fs))

    state_per = np.zeros(n_samples, dtype=np.int8)
    setp_per = np.full(n_samples, sp[AnkleState.S5_LATE_SWING], dtype=float)
    transitions: list[tuple[int, AnkleState]] = []

    state = AnkleState.S5_LATE_SWING
    last_transition = 0

    # Sortare evenimente pentru lookup rapid
    hs_set = set(int(i) for i in hs_idx)
    to_set = set(int(i) for i in to_idx)

    # Detector foot-flat: counter cumulativ
    ff_counter = 0

    for i in range(n_samples):
        new_state = state

        if i in hs_set:
            new_state = AnkleState.S1_LOADING
            ff_counter = 0
        elif i in to_set:
            new_state = AnkleState.S4_EARLY_SWING

        elif state == AnkleState.S1_LOADING:
            # Tranziție la S2 pe foot-flat sau pe timeout
            if abs(omega_shank_dps[i]) < cfg.foot_flat_omega_thr_dps:
                ff_counter += 1
                if ff_counter >= cfg.foot_flat_min_samples:
                    new_state = AnkleState.S2_MIDSTANCE
                    ff_counter = 0
            else:
                ff_counter = 0
            if (i - last_transition) > max_dwell:
                new_state = AnkleState.S2_MIDSTANCE

        elif state == AnkleState.S2_MIDSTANCE:
            # Cerință: S2 trebuie să dureze minimum 20% din median_stride înainte
            # ca să se poată trece la S3. Asta evită tranziții instantanee S1→S2→S3
            # care apar când foot-flat e detectat foarte rapid după HS.
            min_dwell = int(0.20 * median_stride)
            if (i - last_transition) > min_dwell:
                trigger_angle = (
                    ankle_angle_estimate_deg is not None
                    and ankle_angle_estimate_deg[i] > cfg.pushoff_dorsi_thr_deg
                )
                trigger_timeout = (i - last_transition) > int(cfg.pushoff_phase_fraction * median_stride)
                if trigger_angle or trigger_timeout:
                    new_state = AnkleState.S3_PUSHOFF

        elif state == AnkleState.S3_PUSHOFF:
            # S3 → S4 doar pe TO event (gestionat mai sus), sau timeout
            if (i - last_transition) > int(0.3 * median_stride):
                new_state = AnkleState.S4_EARLY_SWING

        elif state == AnkleState.S4_EARLY_SWING:
            # S4 → S5 pe peak ω (mid-swing) sau pe fereastră post-TO
            dt = (i - last_transition) / fs
            if cfg.midswing_window_s[0] <= dt <= cfg.midswing_window_s[1]:
                # peak local detectat dacă ω scade după ce a urcat
                if i > 1 and omega_shank_dps[i - 1] > omega_shank_dps[i] and omega_shank_dps[i - 1] > 0:
                    new_state = AnkleState.S5_LATE_SWING
            if dt > cfg.midswing_window_s[1]:
                new_state = AnkleState.S5_LATE_SWING

        elif state == AnkleState.S5_LATE_SWING:
            # Aștept HS — gestionat de hs_set; pe timeout, rămâne S5
            pass

        if new_state != state:
            transitions.append((i, AnkleState(new_state)))
            last_transition = i
            state = new_state

        state_per[i] = int(state)
        setp_per[i] = sp[state]

    return FSMTrace(state_per_sample=state_per, setpoint_per_sample=setp_per, transitions=transitions)
