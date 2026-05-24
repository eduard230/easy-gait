"""Unit tests pentru parametrii temporali."""
import numpy as np

from easy_gait import segmentation, parameters
from easy_gait.gait_events import GaitEvents


def _make_events(fs=200, n_cycles=10, stride_s=1.0, stance_frac=0.6):
    samples_per_stride = int(stride_s * fs)
    hs = np.array([i * samples_per_stride for i in range(n_cycles + 1)])
    to = np.array([h + int(stance_frac * samples_per_stride) for h in hs[:-1]])
    return GaitEvents(hs_idx=hs, to_idx=to, fs=fs, method="synthetic")


def test_compute_gait_params_synthetic():
    events = _make_events(n_cycles=10, stride_s=1.0, stance_frac=0.6)
    cycles = segmentation.build_cycles(events)
    assert len(cycles) == 10
    params = parameters.compute_gait_params(cycles)
    assert params.n_cycles == 10
    assert abs(params.stride_s_mean - 1.0) < 0.01
    # cadence = 60 * 10 / 10 * 2 = 120 (2 picioare)
    assert abs(params.cadence_steps_per_min - 120.0) < 0.1
    assert abs(params.stance_pct_mean - 60.0) < 0.5
    assert abs(params.swing_pct_mean - 40.0) < 0.5


def test_reject_outliers_removes_short_long():
    events = _make_events(n_cycles=5)  # toate stride=1s
    cycles = segmentation.build_cycles(events)
    # Adăugăm un outlier extrem de scurt (0.1s) și unul extrem de lung (3s)
    short = type(cycles[2])(hs_start=0, to=10, hs_end=20, fs=200)  # 0.1s
    long_ = type(cycles[2])(hs_start=0, to=300, hs_end=600, fs=200)  # 3s
    cycles_aug = cycles + [short, long_]
    filt = segmentation.reject_outliers(cycles_aug)
    # Cele 5 normale rămân, cele 2 outlier-i sunt scoase
    assert len(filt) == 5


def test_symmetry_index():
    assert parameters.symmetry_index(60, 60) == 0.0
    assert parameters.symmetry_index(70, 60) > 0
    assert parameters.symmetry_index(50, 60) < 0


def test_empty_params():
    p = parameters.compute_gait_params([])
    assert p.n_cycles == 0
    assert p.cadence_steps_per_min == 0
