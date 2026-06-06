"""Normalizare la 0-100% gait cycle și validare pe FORMĂ DE PROFIL.

Motivație (literatură): controllerele de impedanță FSM pentru gleznă protetică
(Sup, Bohara & Goldfarb 2008; Au & Herr 2008; Lawson & Goldfarb 2014) NU se
validează prin corelație Pearson / RMSE punct-cu-punct între setpoint-ul comandat
și unghiul articular observat — pentru că setpoint-ul este un *echilibru de
impedanță* (θ_eq), nu o traiectorie de urmărit. Metoda standard este compararea
**formei profilului** mediat pe ciclu (ankle angle vs % gait cycle) cu banda
±1 SD a articulației sănătoase / intacte.

Acest modul oferă:
- `normalize_cycle`        : reeșantionează un segment [HS_i, HS_{i+1}] la 0-100%.
- `build_mean_profile`     : profil mediu + SD dintr-o listă de cicluri normalizate.
- `profile_band_coverage`  : ce % din profilul candidat (FSM) cade în banda ±k·SD.
- `profile_shape_metrics`  : metrici de FORMĂ corecte (coverage, RMSE-pe-profil-mediu,
                             corelație de formă, potrivirea timingului push-off).

Referințe metodologie:
- Perry & Burnfield (2010), Gait Analysis: Normal and Pathological Function.
- Sup F., Bohara A., Goldfarb M. (2008). Int J Robot Res 27(2):263-273.
- Winter D.A. (1991), The Biomechanics and Motor Control of Human Gait.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


N_POINTS = 101  # 0..100 % gait cycle inclusiv


def normalize_cycle(signal: np.ndarray, start: int, end: int,
                    n_points: int = N_POINTS) -> np.ndarray | None:
    """Reeșantionează signal[start:end] la `n_points` puncte (0-100% gait cycle).

    Returns None dacă segmentul e prea scurt (<4 sample).
    """
    if end - start < 4 or end > len(signal):
        return None
    seg = signal[start:end].astype(float)
    x_old = np.linspace(0.0, 100.0, num=len(seg))
    x_new = np.linspace(0.0, 100.0, num=n_points)
    return np.interp(x_new, x_old, seg)


@dataclass
class MeanProfile:
    """Profil mediu pe ciclu + bandă de variabilitate."""
    pct: np.ndarray                  # 0..100 (% gait cycle)
    mean: np.ndarray                 # profil mediu (deg)
    sd: np.ndarray                   # deviație standard pe fiecare procent
    n_cycles: int                    # nr. cicluri agregate

    def band(self, k: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
        """Marginile benzii ±k·SD (lower, upper)."""
        return self.mean - k * self.sd, self.mean + k * self.sd


def build_mean_profile(cycles_norm: list[np.ndarray]) -> MeanProfile | None:
    """Construiește profilul mediu + SD dintr-o listă de cicluri deja normalizate."""
    valid = [c for c in cycles_norm if c is not None and len(c) == N_POINTS]
    if len(valid) < 2:
        return None
    arr = np.vstack(valid)
    return MeanProfile(
        pct=np.linspace(0.0, 100.0, N_POINTS),
        mean=arr.mean(axis=0),
        sd=arr.std(axis=0, ddof=1),
        n_cycles=len(valid),
    )


def cycles_from_events(signal: np.ndarray, hs_idx: np.ndarray) -> list[np.ndarray]:
    """Extrage și normalizează toate ciclurile [HS_i, HS_{i+1}] din semnal."""
    out = []
    for i in range(len(hs_idx) - 1):
        c = normalize_cycle(signal, int(hs_idx[i]), int(hs_idx[i + 1]))
        if c is not None:
            out.append(c)
    return out


def profile_band_coverage(candidate: np.ndarray, ref: MeanProfile,
                          k: float = 1.0) -> float:
    """Procentul (%) din profilul candidat care cade în banda ±k·SD a referinței.

    `candidate` trebuie să fie deja normalizat la N_POINTS.
    """
    if candidate is None or len(candidate) != N_POINTS:
        return float("nan")
    lo, hi = ref.band(k)
    inside = (candidate >= lo) & (candidate <= hi)
    return 100.0 * float(np.mean(inside))


@dataclass
class ShapeMetrics:
    coverage_1sd_pct: float          # % puncte FSM în banda ±1SD intact
    coverage_2sd_pct: float          # % în ±2SD
    profile_rmse_deg: float          # RMSE profil candidat vs profil mediu referință
    shape_pcc: float                 # corelație de formă profil-vs-profil mediu
    pushoff_pct_cand: float          # poziția (% cycle) a plantarflexiei max candidat
    pushoff_pct_ref: float           # idem referință
    pushoff_timing_err_pct: float    # |diferența| de timing push-off (% cycle)
    extra: dict = field(default_factory=dict)


def _argmin_plantar(profile: np.ndarray) -> float:
    """Poziția (% gait cycle) a celui mai plantar punct (min) din profil."""
    idx = int(np.argmin(profile))
    return 100.0 * idx / (len(profile) - 1)


def profile_shape_metrics(candidate: np.ndarray, ref: MeanProfile) -> ShapeMetrics:
    """Metrici de FORMĂ între un profil candidat (FSM) și profilul mediu de referință.

    Spre deosebire de corelația punct-cu-punct pe semnalul brut (nepotrivită pentru
    impedanță), aceasta compară:
    - acoperirea benzii fiziologice (cât din FSM e plauzibil biomecanic),
    - RMSE față de FORMA medie (nu față de un trial individual zgomotos),
    - corelația de formă a profilelor mediate,
    - potrivirea momentului push-off (plantarflexie maximă în stance).
    """
    cand = candidate
    if cand is None or len(cand) != N_POINTS:
        nan = float("nan")
        return ShapeMetrics(nan, nan, nan, nan, nan, nan, nan)
    e = cand - ref.mean
    rmse = float(np.sqrt(np.mean(e ** 2)))
    if np.std(cand) < 1e-9 or np.std(ref.mean) < 1e-9:
        pcc = float("nan")
    else:
        pcc = float(np.corrcoef(cand, ref.mean)[0, 1])
    po_c = _argmin_plantar(cand)
    po_r = _argmin_plantar(ref.mean)
    return ShapeMetrics(
        coverage_1sd_pct=profile_band_coverage(cand, ref, 1.0),
        coverage_2sd_pct=profile_band_coverage(cand, ref, 2.0),
        profile_rmse_deg=rmse,
        shape_pcc=pcc,
        pushoff_pct_cand=po_c,
        pushoff_pct_ref=po_r,
        pushoff_timing_err_pct=abs(po_c - po_r),
    )
