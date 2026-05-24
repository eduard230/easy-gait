"""Segmentare ciclu de mers în faze stance / swing.

Convenții (Perry & Burnfield 2010):
- Stance = [HS_i, TO_i]                    — piciorul în contact cu solul
- Swing  = [TO_i, HS_{i+1}]                — piciorul în aer
- Stride = [HS_i, HS_{i+1}]                — un ciclu complet

Rejecție outlieri stride-to-stride: durata stride în [0.5·median, 1.5·median],
recomandare standard din Trojaniello 2014, Pacini Panebianco 2018.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from easy_gait.gait_events import GaitEvents, pair_hs_to


@dataclass
class GaitCycle:
    """Un ciclu de mers complet: HS_i → TO_i → HS_{i+1}."""
    hs_start: int
    to: int
    hs_end: int
    fs: float

    @property
    def stride_samples(self) -> int:
        return self.hs_end - self.hs_start

    @property
    def stride_s(self) -> float:
        return self.stride_samples / self.fs

    @property
    def stance_samples(self) -> int:
        return self.to - self.hs_start

    @property
    def stance_s(self) -> float:
        return self.stance_samples / self.fs

    @property
    def swing_samples(self) -> int:
        return self.hs_end - self.to

    @property
    def swing_s(self) -> float:
        return self.swing_samples / self.fs

    @property
    def stance_pct(self) -> float:
        return 100.0 * self.stance_samples / max(self.stride_samples, 1)

    @property
    def swing_pct(self) -> float:
        return 100.0 - self.stance_pct


def build_cycles(events: GaitEvents) -> list[GaitCycle]:
    """Construiește lista de cicluri valide din evenimentele detectate."""
    triplets = pair_hs_to(events)
    return [GaitCycle(a, b, c, events.fs) for a, b, c in triplets]


def reject_outliers(cycles: list[GaitCycle], lo: float = 0.5, hi: float = 1.5) -> list[GaitCycle]:
    """Filtrează ciclurile a căror durată e sub `lo·median` sau peste `hi·median`."""
    if not cycles:
        return cycles
    durs = np.array([c.stride_s for c in cycles])
    med = float(np.median(durs))
    mask = (durs >= lo * med) & (durs <= hi * med)
    return [c for c, m in zip(cycles, mask) if m]


def label_phases(n_samples: int, cycles: list[GaitCycle]) -> np.ndarray:
    """Returnează un vector lung de n_samples cu eticheta fazei la fiecare sample.

    Valori: 0 = nedefinit (înainte de primul HS / după ultimul), 1 = stance, 2 = swing.
    Util pentru afișare timeline și pentru calcule pe sample (ex. unghi mediu per fază).
    """
    phases = np.zeros(n_samples, dtype=np.int8)
    for c in cycles:
        phases[c.hs_start:c.to] = 1
        phases[c.to:c.hs_end] = 2
    return phases
