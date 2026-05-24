"""Vizualizare animată 2D a protezei transtibiale (vedere sagitală — laterală).

## Modelul "tibie rigidă + talpa pivotează după date"

Configurație vizuală orientată exclusiv pe gleznă (singura componentă activă
într-o proteză transtibială cu gleznă acționată):

  - TIBIA (pylon) are LUNGIME FIXĂ (L_TIBIA) și UNGHI FIX OBLIC (PYLON_TILT_DEG)
  - GLEZNA se mișcă doar pe VERTICALĂ (ankle.x = constant)
  - GENUNCHIUL se mișcă doar pe VERTICALĂ (knee.x = constant), urcă/coboară
    împreună cu glezna pentru a păstra lungimea + unghiul tibiei constant
  - În stance (S1+S2+S3): talpa rotește cu unghiul EXACT din date (FSM/IMU,
    fără scaling). Cel mai jos punct al tălpii e pe sol. Glezna culisează
    vertical conform geometriei tălpii.
  - În swing (S4+S5): glezna se ridică la poziția neutră + clearance; talpa
    păstrează orientarea după unghiul din date.
  - Tranziția stance↔swing (TO, HS): poziția gleznei se interpolează lin pe
    o fereastră de ~80 ms pentru a evita salturi vizuale.

## Convenție unghi gleznă (FSM)

  - 0° = talpa perpendiculară pe tibie
  - + (dorsiflexie) = vârful în sus față de tibie
  - − (plantarflexie) = vârful în jos față de tibie

NU se aplică niciun scaling/clip pe unghi — folosim valorile exact așa cum
vin din `ankle_controller.generate_trajectory` (FSM) sau `compute_ankle_angle`
(IMU joint), conform selecției utilizatorului în UI.
"""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

# Geometrie standard în metri
L_TIBIA = 0.40
L_FOOT_FRONT = 0.20
L_FOOT_BACK = 0.06
FOOT_THICKNESS = 0.04

PYLON_TILT_DEG = 7.0
_TILT_RAD = np.deg2rad(PYLON_TILT_DEG)
_PYLON_DIR = np.array([np.sin(_TILT_RAD), np.cos(_TILT_RAD)])

GROUND_Y = 0.0

# Poziția neutră a gleznei (în S2 cu talpa orizontală pe sol).
# Glezna are întotdeauna ankle.x = ANKLE_X_NEUTRAL fix.
# Genunchiul are întotdeauna knee.x = ANKLE_X_NEUTRAL + L_TIBIA·sin(tilt) fix.
# Pe verticală, glezna și genunchiul urcă/coboară împreună, păstrând
# vectorul tibial = L_TIBIA·(sin_tilt, cos_tilt) constant.
ANKLE_X_NEUTRAL = 0.0
ANKLE_Y_NEUTRAL = GROUND_Y + FOOT_THICKNESS / 2
KNEE_X_FIX = ANKLE_X_NEUTRAL + L_TIBIA * _PYLON_DIR[0]


def _knee_from_ankle(ankle_xy: np.ndarray) -> np.ndarray:
    """Genunchiul = glezna + vector tibie fix (păstrează lungime + unghi)."""
    return ankle_xy + L_TIBIA * _PYLON_DIR

# Ridicare în swing față de neutru
SWING_LIFT = 0.06

_STANCE_STATES = {1, 2, 3}

FSM_COLORS = {1: "#1f77b4", 2: "#2ca02c", 3: "#d62728", 4: "#ff7f0e", 5: "#9467bd"}
FSM_NAMES = {
    1: "S1 Loading Response",
    2: "S2 Mid-Stance",
    3: "S3 Push-Off",
    4: "S4 Early Swing",
    5: "S5 Late Swing",
}


def _foot_axis_global_deg(ankle_angle_deg: float) -> float:
    """Unghiul axei lungi a tălpii (călcâi→vârf) în cadrul global.

    Convenție:
      - tibia înclinată cu PYLON_TILT_DEG înainte de verticală
      - ankle_angle_deg = unghi între talpă și perpendiculara la tibie
        (+ = dorsiflexie, − = plantarflexie)
      - axa tălpii în cadrul global = PYLON_TILT_DEG + ankle_angle_deg
        (la pylon=0, ankle=0 → talpa orizontală)
    """
    return PYLON_TILT_DEG + ankle_angle_deg


def _build_foot_from_toe(toe_xy: np.ndarray, foot_axis_deg: float) -> dict:
    """Construiește talpa pivotând în jurul vârfului (pentru stance).

    Glezna se calculează DEDUCTIV: ankle = toe − L_FOOT_FRONT · long_axis
    + (FOOT_THICKNESS/2) · short_axis.
    """
    a = np.deg2rad(foot_axis_deg)
    long_axis = np.array([np.cos(a), np.sin(a)])
    short_axis = np.array([-np.sin(a), np.cos(a)])

    toe_mid = toe_xy.copy()
    heel_mid = toe_mid - (L_FOOT_FRONT + L_FOOT_BACK) * long_axis
    ankle = toe_mid - L_FOOT_FRONT * long_axis + (FOOT_THICKNESS / 2) * short_axis

    half_t = (FOOT_THICKNESS / 2) * short_axis
    heel_bot = heel_mid - half_t
    heel_top = heel_mid + half_t
    toe_bot = toe_mid - half_t
    toe_top = toe_mid + half_t

    foot_poly = np.array([heel_bot, toe_bot, toe_top, heel_top, heel_bot])
    return {
        "ankle": ankle, "toe": toe_mid, "heel": heel_mid,
        "foot_poly": foot_poly,
    }


def _build_foot_from_ankle(ankle_xy: np.ndarray, foot_axis_deg: float) -> dict:
    """Construiește talpa cu glezna la poziția dată (pentru swing)."""
    a = np.deg2rad(foot_axis_deg)
    long_axis = np.array([np.cos(a), np.sin(a)])
    short_axis = np.array([-np.sin(a), np.cos(a)])

    toe_mid = ankle_xy + L_FOOT_FRONT * long_axis
    heel_mid = ankle_xy - L_FOOT_BACK * long_axis

    half_t = (FOOT_THICKNESS / 2) * short_axis
    heel_bot = heel_mid - half_t
    heel_top = heel_mid + half_t
    toe_bot = toe_mid - half_t
    toe_top = toe_mid + half_t

    foot_poly = np.array([heel_bot, toe_bot, toe_top, heel_top, heel_bot])
    return {
        "ankle": ankle_xy.copy(), "toe": toe_mid, "heel": heel_mid,
        "foot_poly": foot_poly,
    }


def _stance_geometry(ankle_angle_deg: float) -> dict:
    """Geometria în stance: talpa rotește după unghiul exact, cu cel mai jos
    punct al tălpii pe sol (vârful când plantarflexie, călcâiul când dorsi).

    Glezna se calculează deductiv din poziția tălpii. Pylonul rămâne fix oblic
    (genunchiul nu se mișcă), dar glezna culisează vertical conform geometriei.
    """
    foot_axis = _foot_axis_global_deg(ankle_angle_deg)
    a = np.deg2rad(foot_axis)

    # Construim întâi talpa cu glezna pe linia pylonului (ankle_x = ANKLE_X_NEUTRAL)
    # și ankle_y candidat = ANKLE_Y_NEUTRAL. Apoi verificăm punctul cel mai jos
    # al poligonului și translatăm vertical ca acel punct să fie pe sol.
    candidate_ankle = np.array([ANKLE_X_NEUTRAL, ANKLE_Y_NEUTRAL])
    foot = _build_foot_from_ankle(candidate_ankle, foot_axis)
    # Translatăm pe verticală ca cel mai jos punct al poligonului să fie la y=0
    lowest_y = float(foot["foot_poly"][:, 1].min())
    dy = GROUND_Y - lowest_y
    if dy != 0.0:
        foot["ankle"] = foot["ankle"] + np.array([0.0, dy])
        foot["toe"] = foot["toe"] + np.array([0.0, dy])
        foot["heel"] = foot["heel"] + np.array([0.0, dy])
        foot["foot_poly"] = foot["foot_poly"] + np.array([0.0, dy])
    return foot


def _swing_geometry(ankle_angle_deg: float) -> dict:
    """Geometria în swing: glezna ridicată cu SWING_LIFT, talpa rotește după unghi."""
    foot_axis = _foot_axis_global_deg(ankle_angle_deg)
    ankle = np.array([ANKLE_X_NEUTRAL, ANKLE_Y_NEUTRAL + SWING_LIFT])
    return _build_foot_from_ankle(ankle, foot_axis)


def compute_segments(
    ankle_angle_deg: float,
    fsm_state: int = 2,
    phase_frac: float = 0.5,  # neutilizat
) -> dict:
    """Coordonatele segmentelor protezei pentru un cadru.

    În stance: vârful pe sol, talpa rotește după unghiul EXACT din date.
    În swing: glezna ridicată, talpa rotește după unghiul EXACT din date.
    Tibia + genunchiul: fix oblic.
    """
    if int(fsm_state) in _STANCE_STATES:
        foot = _stance_geometry(ankle_angle_deg)
    else:
        foot = _swing_geometry(ankle_angle_deg)

    knee = _knee_from_ankle(foot["ankle"])
    return {
        "ankle": foot["ankle"],
        "knee": knee,
        "toe": foot["toe"],
        "heel": foot["heel"],
        "foot_poly": foot["foot_poly"],
        "ground_y": GROUND_Y,
        "tibia_tilt_deg": PYLON_TILT_DEG,
    }


def build_animation_figure(
    times_s: np.ndarray,
    ankle_angles_deg: np.ndarray,
    fsm_states: np.ndarray,
    *,
    resample_hz: int = 60,
    height: int = 540,
    playback_speed: float = 1.0,
) -> go.Figure:
    """Construiește figura Plotly cu animație, slider și buton Play/Pause.

    Args:
        playback_speed: 1.0 = real-time, 0.5 = jumătate viteză, 2.0 = dublu.
            Afectează doar viteza de redare (cât timp stă un cadru pe ecran),
            nu și unghiurile sau geometria.
    """
    if len(times_s) < 2:
        times_s = np.asarray([0.0, 1.0])
        ankle_angles_deg = np.asarray([0.0, 0.0])
        fsm_states = np.asarray([5, 5])

    dt_target = 1.0 / resample_hz
    t_grid = np.arange(times_s[0], times_s[-1], dt_target)
    if len(t_grid) < 2:
        t_grid = times_s.copy()
    ang = np.interp(t_grid, times_s, ankle_angles_deg)
    idx = np.searchsorted(times_s, t_grid)
    idx = np.clip(idx, 0, len(fsm_states) - 1)
    sts = np.asarray(fsm_states)[idx]

    # Calculează geometriile pentru ambele moduri (stance & swing) pentru
    # fiecare cadru, apoi interpolează între ele pe o fereastră de tranziție
    # de 80 ms în jurul evenimentelor TO/HS. Asta gestionează decuplarea
    # fizică de la sol (varianta ii) fără a modifica unghiul tălpii.
    stance_geoms = [_stance_geometry(float(a)) for a in ang]
    swing_geoms = [_swing_geometry(float(a)) for a in ang]
    is_stance = np.isin(sts, list(_STANCE_STATES))

    # Pondere stance (1.0 = full stance, 0.0 = full swing), netezită cu MA
    # pentru a interpola pozițiile fizice (ankle.y) între cele 2 moduri.
    w_stance_raw = is_stance.astype(float)
    blend_win = max(int(0.08 * resample_hz), 3)
    if blend_win % 2 == 0:
        blend_win += 1
    if blend_win < len(w_stance_raw):
        kernel = np.ones(blend_win) / blend_win
        w_stance = np.convolve(w_stance_raw, kernel, mode="same")
    else:
        w_stance = w_stance_raw

    frames = []
    for i, (t, a, s) in enumerate(zip(t_grid, ang, sts)):
        w = w_stance[i]
        # Interpolare liniară între geometria stance și swing
        ankle_pos = w * stance_geoms[i]["ankle"] + (1 - w) * swing_geoms[i]["ankle"]
        toe_pos = w * stance_geoms[i]["toe"] + (1 - w) * swing_geoms[i]["toe"]
        heel_pos = w * stance_geoms[i]["heel"] + (1 - w) * swing_geoms[i]["heel"]
        foot_poly = (w * stance_geoms[i]["foot_poly"]
                     + (1 - w) * swing_geoms[i]["foot_poly"])
        # Genunchiul = glezna + vector tibie fix (rigid, lungime + unghi constante)
        knee = _knee_from_ankle(ankle_pos)

        color = FSM_COLORS.get(int(s), "#888")

        traces = [
            go.Scatter(
                x=[-0.50, 0.60], y=[GROUND_Y] * 2,
                mode="lines", line=dict(color="#888", width=2),
                showlegend=False, hoverinfo="skip",
            ),
            go.Scatter(
                x=[ankle_pos[0], knee[0]], y=[ankle_pos[1], knee[1]],
                mode="lines", line=dict(color="#444", width=18),
                name="Tibia", hoverinfo="skip",
            ),
            go.Scatter(
                x=foot_poly[:, 0], y=foot_poly[:, 1],
                mode="lines", fill="toself", fillcolor=color,
                line=dict(color=color, width=1),
                name=f"Talpa ({FSM_NAMES.get(int(s), '?')})",
                hovertemplate=f"t={t:.2f}s<br>θ={a:.1f}°<br>{FSM_NAMES.get(int(s),'?')}",
            ),
            go.Scatter(
                x=[ankle_pos[0]], y=[ankle_pos[1]],
                mode="markers",
                marker=dict(size=18, color="white", line=dict(width=3, color="black")),
                name="Gleznă", hoverinfo="skip",
            ),
            go.Scatter(
                x=[knee[0]], y=[knee[1]],
                mode="markers",
                marker=dict(size=22, color="#666", line=dict(width=2, color="black")),
                name="Genunchi", hoverinfo="skip",
            ),
        ]
        frames.append(go.Frame(
            name=f"{t:.3f}", data=traces,
            layout=go.Layout(
                title_text=f"t = {t:.2f} s    |    θ_gleznă = {a:+.1f}°    |    {FSM_NAMES.get(int(s),'?')}",
            ),
        ))

    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        xaxis=dict(
            range=[-0.50, 0.60], scaleanchor="y", scaleratio=1,
            showgrid=True, gridcolor="#eee", zeroline=False,
            title="x (m) — anterior →",
        ),
        yaxis=dict(
            range=[-0.05, 0.65],
            showgrid=True, gridcolor="#eee", zeroline=False,
            title="y (m) — vertical ↑",
        ),
        title=frames[0].layout.title.text,
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=False,
        updatemenus=[dict(
            type="buttons", direction="left",
            x=0.02, y=1.08, xanchor="left", yanchor="bottom",
            buttons=[
                dict(label="▶ Play", method="animate", args=[None, {
                    "frame": {
                        "duration": int(1000 / (resample_hz * max(playback_speed, 0.01))),
                        "redraw": True,
                    },
                    "fromcurrent": True, "transition": {"duration": 0},
                }]),
                dict(label="⏸ Pause", method="animate", args=[[None], {
                    "frame": {"duration": 0, "redraw": False},
                    "mode": "immediate", "transition": {"duration": 0},
                }]),
            ],
        )],
        sliders=[dict(
            active=0,
            currentvalue=dict(prefix="t = ", suffix=" s", visible=True),
            pad=dict(t=40),
            steps=[dict(
                method="animate", label=f.name,
                args=[[f.name], {
                    "mode": "immediate",
                    "frame": {"duration": 0, "redraw": True},
                    "transition": {"duration": 0},
                }],
            ) for f in frames],
        )],
    )
    return fig


def build_legend_figure() -> go.Figure:
    fig = go.Figure()
    for s_int, name in FSM_NAMES.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(size=15, color=FSM_COLORS[s_int]),
            name=name, showlegend=True,
        ))
    fig.update_layout(
        height=80, margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=0.5),
        template="plotly_white",
    )
    return fig
