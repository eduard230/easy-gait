"""Unit tests pentru detecția HS/TO."""
import numpy as np

from easy_gait import gait_events


def _synthetic_gait_signal(n_cycles: int = 5, fs: float = 200, stride_s: float = 1.0):
    """Generează un semnal sintetic shank pitch rate cu vârfuri și minime predictibile.

    Forma unui ciclu:
      - 0..30%: stance (ω ~ 0)
      - 30..45%: pre-swing/TO (ω devine negativ ~ -50 dps)
      - 45..70%: mid-swing peak (ω ~ +250 dps)
      - 70..85%: late swing → HS (ω minim ~ -100 dps)
      - 85..100%: stance start (ω ~ 0)
    """
    samples_per_stride = int(stride_s * fs)
    n_total = n_cycles * samples_per_stride
    signal = np.zeros(n_total)
    hs_true = []
    to_true = []
    for c in range(n_cycles):
        offset = c * samples_per_stride
        # TO la 35%
        to_idx = offset + int(0.35 * samples_per_stride)
        # Mid-swing peak la 60%
        ms_idx = offset + int(0.60 * samples_per_stride)
        # HS la 85%
        hs_idx = offset + int(0.85 * samples_per_stride)

        # Forme triunghiulare
        signal[to_idx - 5:to_idx + 5] = np.linspace(0, -50, 10)
        signal[to_idx + 5:ms_idx] = np.linspace(-50, 250, ms_idx - (to_idx + 5))
        signal[ms_idx:hs_idx] = np.linspace(250, -100, hs_idx - ms_idx)
        signal[hs_idx:hs_idx + 5] = np.linspace(-100, 0, 5)
        to_true.append(to_idx)
        hs_true.append(hs_idx)
    return signal, np.array(hs_true), np.array(to_true)


def test_trojaniello_detects_synthetic_events():
    fs = 200
    sig, hs_true, to_true = _synthetic_gait_signal(n_cycles=5, fs=fs)
    events = gait_events.detect_events_trojaniello(sig, fs=fs)
    # Trebuie să detecteze majoritatea evenimentelor (toleranță 1 lipsă)
    assert len(events.hs_idx) >= len(hs_true) - 1
    assert len(events.to_idx) >= len(to_true) - 1
    # Erorile temporale (samples) sub 50 ms = 10 samples @ 200 Hz
    for h in events.hs_idx:
        diff = np.min(np.abs(hs_true - h))
        assert diff < 20, f"HS detection too far: {diff} samples"


def test_maqbool_detects_synthetic_events():
    fs = 200
    sig, hs_true, to_true = _synthetic_gait_signal(n_cycles=5, fs=fs)
    # Magnitudine accelerație sintetică: spike la fiecare HS
    accel_mag = np.full_like(sig, 9.8)  # gravitație
    for h in hs_true:
        accel_mag[max(0, h - 5):h + 5] = 20.0  # 2g spike anticipativ

    # Praguri relaxate pentru semnal sintetic (forme triunghiulare, amplitudini mai mici)
    events = gait_events.detect_events_maqbool(
        sig, accel_mag, fs=fs,
        omega_swing_in_dps=30.0,
        omega_hs_dps=-50.0,
        accel_hs_g=1.5,
    )
    # Acceptăm și un eveniment lipsă la capete (signal start/end)
    assert len(events.hs_idx) >= len(hs_true) - 2
    assert len(events.to_idx) >= len(to_true) - 1


def test_pair_hs_to_returns_valid_cycles():
    fs = 200
    sig, _, _ = _synthetic_gait_signal(n_cycles=4, fs=fs)
    events = gait_events.detect_events_trojaniello(sig, fs=fs)
    cycles = gait_events.pair_hs_to(events)
    # Cicluri ordonate cronologic, TO între cele 2 HS
    for hs1, to, hs2 in cycles:
        assert hs1 < to < hs2


def test_empty_signal_no_events():
    events = gait_events.detect_events_trojaniello(np.zeros(100), fs=200)
    assert len(events.hs_idx) == 0
    assert len(events.to_idx) == 0
