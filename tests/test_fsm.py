"""Unit tests pentru FSM gleznă protetică."""
import numpy as np

from easy_gait import fsm, ankle_controller
from easy_gait.fsm import AnkleState, SETPOINTS


def test_setpoints_have_all_states():
    for activity, sp in SETPOINTS.items():
        assert set(sp.keys()) == set(AnkleState)


def test_setpoints_sensible_ranges():
    """Toate setpoint-urile trebuie să fie în ROM realist (-45° → +20°)."""
    for activity, sp in SETPOINTS.items():
        for state, val in sp.items():
            assert -45 <= val <= 20, f"{activity}/{state} out of range: {val}"


def test_run_fsm_transitions_on_events():
    fs = 200
    n = 1000
    hs = np.array([100, 500, 900])
    to = np.array([350, 750])
    omega = np.zeros(n)
    trace = fsm.run_fsm(n, fs, hs, to, omega, ankle_angle_estimate_deg=None)
    # Trebuie să aibă cel puțin tranzițiile pe HS și TO
    states_changed = [t[1] for t in trace.transitions]
    assert AnkleState.S1_LOADING in states_changed
    assert AnkleState.S4_EARLY_SWING in states_changed


def test_setpoint_trajectory_within_setpoint_envelope():
    fs = 200
    n = 1000
    hs = np.array([100, 500, 900])
    to = np.array([350, 750])
    omega = np.zeros(n)
    trace = fsm.run_fsm(n, fs, hs, to, omega)
    traj = ankle_controller.generate_trajectory(trace, fs=fs)
    sp_vals = list(SETPOINTS["level"].values())
    assert min(sp_vals) - 5 <= traj.min()
    assert traj.max() <= max(sp_vals) + 5
