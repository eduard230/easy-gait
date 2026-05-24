"""Unit tests pentru modulul preprocessing."""
import numpy as np
import pytest

from easy_gait import preprocessing


def test_butter_lowpass_attenuates_high_freq():
    fs = 200
    t = np.arange(0, 2, 1 / fs)
    low = np.sin(2 * np.pi * 2 * t)        # 2 Hz — trecut
    high = np.sin(2 * np.pi * 60 * t)      # 60 Hz — atenuat
    signal = low + high
    filtered = preprocessing.butter_lowpass(signal, fs=fs, cutoff_hz=15.0, order=4)
    # Componenta 2 Hz trebuie să rămână aproape identic
    err = np.std(filtered - low)
    assert err < 0.15, f"low-freq passed through inacurat: err={err}"


def test_butter_lowpass_invalid_cutoff():
    sig = np.zeros(100)
    with pytest.raises(ValueError):
        preprocessing.butter_lowpass(sig, fs=200, cutoff_hz=200)


def test_derivative_constant_signal_is_zero():
    fs = 100
    sig = np.full(500, 3.14)
    d = preprocessing.derivative(sig, fs)
    assert np.allclose(d, 0.0)


def test_detect_quiet_segments():
    # 100 quiet, 50 active, 30 quiet (sub min), 80 quiet (peste min)
    omega = np.concatenate([
        np.full(100, 10.0),    # quiet ✓
        np.full(50, 100.0),    # active (>30 prag)
        np.full(30, 5.0),      # quiet dar sub 50 samples — DAR continuă în următorul
        np.full(80, 0.0),      # quiet — împreună cu cei 30 face 110 samples
    ])
    out = preprocessing.detect_quiet_segments(omega, threshold_dps=30.0, min_samples=50)
    # primele 100 = quiet
    assert out[:100].all()
    # următorii 50 = activ
    assert not out[100:150].any()
    # ultimii 110 (30+80) = quiet contiguu, suficient
    assert out[150:260].all()
