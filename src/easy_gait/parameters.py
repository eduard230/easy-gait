"""Parametri temporali ai mersului calculați din evenimente HS/TO.

Indicatori clinici standard (Hollman 2011, Hausdorff 2007, Lord 2013):
- Cadence (pași/min)
- Stride duration (s) — medie, SD, CV
- Stance / Swing % per stride
- Single-support / Double-support % (necesită ambele picioare)
- Symmetry Index (între picior protetic și sănătos)
- Variabilitate stride-to-stride (deviație standard, CV)
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from easy_gait.segmentation import GaitCycle


@dataclass
class GaitParams:
    n_cycles: int
    cadence_steps_per_min: float
    stride_s_mean: float
    stride_s_std: float
    stride_cv: float                  # coefficient of variation = std/mean
    stance_pct_mean: float
    stance_pct_std: float
    swing_pct_mean: float
    swing_pct_std: float
    duration_total_s: float
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "n_cycles": self.n_cycles,
            "cadence [steps/min]": round(self.cadence_steps_per_min, 2),
            "stride mean [s]": round(self.stride_s_mean, 3),
            "stride std [s]": round(self.stride_s_std, 3),
            "stride CV [%]": round(100 * self.stride_cv, 2),
            "stance mean [%]": round(self.stance_pct_mean, 2),
            "stance std [%]": round(self.stance_pct_std, 2),
            "swing mean [%]": round(self.swing_pct_mean, 2),
            "swing std [%]": round(self.swing_pct_std, 2),
            "duration [s]": round(self.duration_total_s, 2),
        }


def compute_gait_params(cycles: list[GaitCycle]) -> GaitParams:
    """Calculează parametrii temporali agregati pe lista de cicluri."""
    if not cycles:
        return GaitParams(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, raw={})

    strides = np.array([c.stride_s for c in cycles])
    stance_pcts = np.array([c.stance_pct for c in cycles])
    swing_pcts = np.array([c.swing_pct for c in cycles])

    total_s = float(strides.sum())
    # cadence: 1 stride = 2 pași (un pas pe partea contralateral + unul ipsilateral),
    # dar fiindcă numărăm doar HS-uri pe un picior, fiecare HS = 1 pas pe partea aceea,
    # iar cadența clinică totală e dublul.
    n_steps_per_side = len(cycles)
    cadence_per_side = 60.0 * n_steps_per_side / total_s if total_s > 0 else 0.0
    cadence_total = 2.0 * cadence_per_side

    mean_s = float(strides.mean())
    std_s = float(strides.std(ddof=1)) if len(strides) > 1 else 0.0
    cv = std_s / mean_s if mean_s > 0 else 0.0

    return GaitParams(
        n_cycles=len(cycles),
        cadence_steps_per_min=cadence_total,
        stride_s_mean=mean_s,
        stride_s_std=std_s,
        stride_cv=cv,
        stance_pct_mean=float(stance_pcts.mean()),
        stance_pct_std=float(stance_pcts.std(ddof=1)) if len(stance_pcts) > 1 else 0.0,
        swing_pct_mean=float(swing_pcts.mean()),
        swing_pct_std=float(swing_pcts.std(ddof=1)) if len(swing_pcts) > 1 else 0.0,
        duration_total_s=total_s,
        raw={"strides": strides, "stance_pcts": stance_pcts, "swing_pcts": swing_pcts},
    )


def symmetry_index(prosthetic: float, intact: float) -> float:
    """Symmetry Index (Robinson 1987): SI = 2·(P − I)/(P + I) · 100.

    0 = simetrie perfectă. Pozitiv → valoarea protetică mai mare. Util pentru
    comparare cadență, durate stance, etc.
    """
    s = prosthetic + intact
    if s == 0:
        return 0.0
    return 100.0 * 2.0 * (prosthetic - intact) / s
