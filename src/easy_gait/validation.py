"""Metrice de validare pentru evenimente și traiectorii.

- `event_mae`: MAE temporal între evenimente detectate și ground truth (ms).
- `event_f1`: F1-score la nivel de eveniment cu toleranță configurabilă.
- `traj_rmse`, `traj_nrmse`, `traj_pcc`: erori traiectorie unghi gleznă (deg).
- `dtw_distance`: distanță Dynamic Time Warping (opțional, robust la decalaje).

Standarde de acceptabilitate (Pacini Panebianco 2018, Markowitz 2011, Bartlett 2021):
- IC: |MAE| ≤ 25 ms, sens ≥ 99%
- TO: |MAE| ≤ 50 ms, sens ≥ 98%
- Traj ankle: RMSE < 5°, NRMSE < 15% pe level, PCC > 0.90
"""
from __future__ import annotations

import numpy as np


def event_mae(
    detected_idx: np.ndarray,
    truth_idx: np.ndarray,
    fs: float,
    tol_ms: float = 100.0,
) -> dict:
    """MAE temporal între evenimente detectate și ground truth.

    Algoritm: pentru fiecare eveniment truth, găsește cel mai apropiat detected
    în fereastra ±tol_ms. Calculează diferențele (ms) și agreghează.

    Returns:
        dict cu: mae_ms, bias_ms, n_truth, n_matched, sens (recall), ppv (precision), f1
    """
    if len(truth_idx) == 0:
        return {"mae_ms": np.nan, "bias_ms": np.nan, "n_truth": 0,
                "n_matched": 0, "sens": 0.0, "ppv": 0.0, "f1": 0.0}
    if len(detected_idx) == 0:
        return {"mae_ms": np.nan, "bias_ms": np.nan, "n_truth": int(len(truth_idx)),
                "n_matched": 0, "sens": 0.0, "ppv": 0.0, "f1": 0.0}

    truth_t = truth_idx / fs * 1000.0  # ms
    det_t = detected_idx / fs * 1000.0
    diffs = []
    matched_det = set()
    for t in truth_t:
        d = det_t - t
        idx_min = int(np.argmin(np.abs(d)))
        if abs(d[idx_min]) <= tol_ms and idx_min not in matched_det:
            diffs.append(d[idx_min])
            matched_det.add(idx_min)

    n_matched = len(diffs)
    mae = float(np.mean(np.abs(diffs))) if diffs else np.nan
    bias = float(np.mean(diffs)) if diffs else np.nan
    sens = n_matched / len(truth_t)
    ppv = n_matched / len(det_t) if len(det_t) else 0.0
    f1 = 2 * sens * ppv / (sens + ppv) if (sens + ppv) > 0 else 0.0
    return {
        "mae_ms": mae,
        "bias_ms": bias,
        "n_truth": int(len(truth_t)),
        "n_detected": int(len(det_t)),
        "n_matched": n_matched,
        "sens": sens,
        "ppv": ppv,
        "f1": f1,
    }


def restrict_to_window(detected_idx: np.ndarray, lo: int, hi: int,
                       margin: int = 0) -> np.ndarray:
    """Păstrează doar evenimentele detectate care cad în fereastra [lo-margin, hi+margin].

    Motivație: în datasetul Samala IMU acoperă ~14 s, dar OMC (ground truth) doar
    ~4.5 s. Detectorul IMU produce evenimente reale pe TOT trial-ul, însă cele din
    afara ferestrei OMC nu au pereche de referință și apar artificial ca
    fals-pozitive, prăbușind PPV/F1. Comparația corectă (măr-cu-măr) se face doar
    pe intervalul acoperit de OMC.
    """
    if len(detected_idx) == 0:
        return detected_idx
    d = np.asarray(detected_idx)
    return d[(d >= lo - margin) & (d <= hi + margin)]


def event_mae_windowed(
    detected_idx: np.ndarray,
    truth_idx: np.ndarray,
    fs: float,
    tol_ms: float = 150.0,
    margin_ms: float = 200.0,
    debias: bool = False,
) -> dict:
    """`event_mae` evaluat DOAR pe fereastra acoperită de ground-truth (OMC).

    Restrânge evenimentele detectate la intervalul [min(truth), max(truth)] ± margin,
    apoi calculează metricile. Opțional aplică o corecție de bias median (debias):
    scade decalajul sistematic median detected−truth înainte de a raporta MAE, ceea
    ce reflectă practica de calibrare din literatură (offset constant între definiția
    evenimentului IMU și definiția Zeni-OMC).

    Returns: dict cu aceleași chei ca `event_mae`, plus:
        mae_debiased_ms, bias_ms, n_detected_in_window.
    """
    if len(truth_idx) == 0:
        base = event_mae(detected_idx, truth_idx, fs, tol_ms)
        base.update({"mae_debiased_ms": np.nan, "n_detected_in_window": 0})
        return base

    lo, hi = int(np.min(truth_idx)), int(np.max(truth_idx))
    margin = int(margin_ms / 1000.0 * fs)
    det_win = restrict_to_window(detected_idx, lo, hi, margin=margin)

    res = event_mae(det_win, truth_idx, fs, tol_ms)
    res["n_detected_in_window"] = int(len(det_win))

    # Corecție de bias: re-evaluează MAE după scăderea biasului median
    if debias and not np.isnan(res.get("bias_ms", np.nan)) and len(det_win) > 0:
        bias_samples = res["bias_ms"] / 1000.0 * fs
        det_corr = det_win - bias_samples
        res_corr = event_mae(det_corr.astype(float), truth_idx, fs, tol_ms)
        res["mae_debiased_ms"] = res_corr["mae_ms"]
    else:
        res["mae_debiased_ms"] = res.get("mae_ms", np.nan)
    return res


def traj_rmse(pred: np.ndarray, truth: np.ndarray) -> float:
    """RMSE între două traiectorii sincronizate (aceeași fs și lungime)."""
    n = min(len(pred), len(truth))
    e = pred[:n] - truth[:n]
    return float(np.sqrt(np.nanmean(e ** 2)))


def traj_nrmse(pred: np.ndarray, truth: np.ndarray) -> float:
    """NRMSE = RMSE / (max(truth) − min(truth)). Returnat în [0, ∞) (nu %)."""
    n = min(len(pred), len(truth))
    rng = float(np.nanmax(truth[:n]) - np.nanmin(truth[:n]))
    if rng == 0:
        return np.nan
    return traj_rmse(pred[:n], truth[:n]) / rng


def traj_pcc(pred: np.ndarray, truth: np.ndarray) -> float:
    """Pearson Correlation Coefficient."""
    n = min(len(pred), len(truth))
    p = pred[:n]
    t = truth[:n]
    mask = ~(np.isnan(p) | np.isnan(t))
    if mask.sum() < 2:
        return np.nan
    return float(np.corrcoef(p[mask], t[mask])[0, 1])


def dtw_distance(pred: np.ndarray, truth: np.ndarray, *, window: int | None = None) -> float:
    """Dynamic Time Warping distance, normalizată pe lungimea path-ului.

    Implementare simplă O(n²) cu opțiunea Sakoe-Chiba band (window). Pentru
    n > ~5000 e lent — pentru lucrare folosim pe cicluri individuale (50-200 samples).
    """
    n, m = len(pred), len(truth)
    if n == 0 or m == 0:
        return np.nan
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        j_lo = max(1, i - window) if window else 1
        j_hi = min(m + 1, i + window + 1) if window else m + 1
        for j in range(j_lo, j_hi):
            cost = abs(pred[i - 1] - truth[j - 1])
            D[i, j] = cost + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    return float(D[n, m] / (n + m))
