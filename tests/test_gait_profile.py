"""Teste pentru gait_profile (normalizare ciclu + validare pe formă de profil)."""
import numpy as np
import pytest

from easy_gait import gait_profile as gp


def test_normalize_cycle_length():
    sig = np.arange(50, dtype=float)
    out = gp.normalize_cycle(sig, 0, 50)
    assert out is not None
    assert len(out) == gp.N_POINTS
    # Capetele se păstrează
    assert out[0] == pytest.approx(0.0)
    assert out[-1] == pytest.approx(49.0)


def test_normalize_cycle_too_short():
    assert gp.normalize_cycle(np.arange(10.0), 0, 3) is None


def test_build_mean_profile_basic():
    # Trei cicluri identice → SD ≈ 0, n=3
    base = np.linspace(-10, 10, gp.N_POINTS)
    prof = gp.build_mean_profile([base.copy(), base.copy(), base.copy()])
    assert prof is not None
    assert prof.n_cycles == 3
    assert np.allclose(prof.mean, base)
    assert np.allclose(prof.sd, 0.0, atol=1e-9)


def test_build_mean_profile_needs_two():
    base = np.zeros(gp.N_POINTS)
    assert gp.build_mean_profile([base]) is None


def test_band_coverage_full_when_identical():
    base = np.sin(np.linspace(0, 2 * np.pi, gp.N_POINTS))
    # Bandă cu SD pozitiv (din cicluri ușor diferite)
    prof = gp.build_mean_profile([base, base + 0.5, base - 0.5])
    cov = gp.profile_band_coverage(prof.mean, prof, k=1.0)
    assert cov == pytest.approx(100.0)


def test_band_coverage_zero_when_far_outside():
    base = np.zeros(gp.N_POINTS)
    prof = gp.build_mean_profile([base + 0.1, base - 0.1, base])
    far = np.full(gp.N_POINTS, 100.0)
    assert gp.profile_band_coverage(far, prof, k=1.0) == pytest.approx(0.0)


def test_shape_metrics_pushoff_timing():
    # Profil cu minim (plantarflexie max) la 60% — push-off tipic
    x = np.linspace(0, 100, gp.N_POINTS)
    ref_mean = -np.exp(-((x - 60) ** 2) / 50)  # min la 60%
    prof = gp.build_mean_profile([ref_mean, ref_mean + 0.01, ref_mean - 0.01])
    sm = gp.profile_shape_metrics(ref_mean, prof)
    assert sm.pushoff_pct_ref == pytest.approx(60.0, abs=1.0)
    assert sm.pushoff_pct_cand == pytest.approx(60.0, abs=1.0)
    assert sm.pushoff_timing_err_pct == pytest.approx(0.0, abs=1.0)
    assert sm.shape_pcc == pytest.approx(1.0, abs=1e-6)


def test_cycles_from_events():
    sig = np.zeros(300)
    hs = np.array([0, 100, 200, 299])
    cycles = gp.cycles_from_events(sig, hs)
    assert len(cycles) == 3
    assert all(len(c) == gp.N_POINTS for c in cycles)
