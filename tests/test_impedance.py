"""Teste pentru bucla de impedanță (θ_obs = θ_eq + M_GRF/K) din ankle_controller."""
import numpy as np
import pytest

from easy_gait import ankle_controller as ac


def test_grf_profile_shape():
    grf = ac.grf_vertical_profile()
    assert len(grf) == 101
    # Două vârfuri ~1.1 BW în stance, ~0 în swing
    assert grf.max() == pytest.approx(1.12, abs=0.05)
    assert grf[15] > 0.9          # loading response
    assert grf[50] > 0.9          # push-off
    assert grf[80] == pytest.approx(0.0, abs=0.01)  # swing


def test_impedance_swing_equals_equilibrium():
    # În swing GRF=0 → unghiul observat = echilibrul comandat
    theta_eq = np.full(101, -5.0)
    phase = np.full(101, 80.0)    # toți în swing
    theta_obs = ac.observed_angle_from_impedance(theta_eq, phase)
    assert np.allclose(theta_obs, -5.0, atol=1e-6)


def test_impedance_stance_adds_dorsiflexion():
    # În stance GRF>0 → unghiul observat e mai dorsiflex (mai mare) decât echilibrul
    theta_eq = np.full(101, -15.0)
    phase = np.full(101, 15.0)    # loading response, GRF mare
    theta_obs = ac.observed_angle_from_impedance(theta_eq, phase)
    assert np.all(theta_obs > -15.0)   # deplasare în dorsiflexie


def test_impedance_stiffness_inverse():
    # K mai mare → deflexie mai mică
    theta_eq = np.full(10, -15.0)
    phase = np.full(10, 50.0)
    soft = ac.observed_angle_from_impedance(theta_eq, phase, stiffness_nm_per_deg=1.0)
    stiff = ac.observed_angle_from_impedance(theta_eq, phase, stiffness_nm_per_deg=6.0)
    # deflexia (obs - eq) e mai mare la soft
    assert (soft - theta_eq).mean() > (stiff - theta_eq).mean()


def test_phase_from_states_linear():
    n = 300
    hs = np.array([0, 100, 200])
    phase = ac.phase_from_states(np.zeros(n), hs, n)
    # La mijlocul primului ciclu (50) faza ~50%
    assert phase[50] == pytest.approx(50.0, abs=2.0)
    assert phase[150] == pytest.approx(50.0, abs=2.0)
    assert 0.0 <= phase.min() and phase.max() < 100.0
