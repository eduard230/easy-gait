"""easy-gait — Platformă software pentru analiza ciclului de mers IMU și control FSM al gleznei protetice."""

__version__ = "0.1.0"

from easy_gait import (
    io_utils,
    preprocessing,
    gait_events,
    segmentation,
    parameters,
    fsm,
    ankle_controller,
    validation,
    prosthesis_viz,
    gait_profile,
)

__all__ = [
    "io_utils",
    "preprocessing",
    "gait_events",
    "segmentation",
    "parameters",
    "fsm",
    "ankle_controller",
    "validation",
    "prosthesis_viz",
    "gait_profile",
]
