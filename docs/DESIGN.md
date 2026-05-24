# easy-gait — Platformă software pentru analiza ciclului de mers și control adaptiv al gleznei utilizând date IMU

**Dizertație:** Raluca Andreea PĂUN
**Coordonator:** Conf. dr.ing. Mădălin-Corneliu FRUNZETE
**Facultate:** UPB — Inginerie Medicală, masterat TMIM
**Sesiune:** ianuarie 2026

---

## 1. Scop

Platformă software modulară în Python care:
1. importă și preprocesează semnale IMU de la purtători de proteze transtibiale,
2. detectează automat evenimentele biomecanice Heel Strike (HS) și Toe Off (TO),
3. segmentează ciclul de mers în stance / swing,
4. calculează parametri temporali (cadență, durată pas, % stance/swing, variabilitate),
5. compară parametrii între activități locomotorii (mers plan, scări, rampe, teren denivelat),
6. generează o traiectorie de referință pentru unghiul gleznei printr-un **Finite State Machine (FSM)** cu 5 stări — simulare software a controlului unei proteze active,
7. validează rezultatele contra unui sistem de referință (motion capture) și expune totul printr-un **dashboard Streamlit** interactiv.

Lucrarea **NU dezvoltă hardware** — toate datele provin din baze publice peer-reviewed. Extinde licența autoarei (proteză transtibială mecanică, iul 2024) cu partea software inteligentă de analiză și control.

---

## 2. Dataseturi (descărcate local în `data/raw/`)

### 2.1 Dataset principal — Samala et al. 2024
- **Citare:** Samala M., Rattanakoch J., Guerra G., et al. (2024). *A dataset of optical camera and IMU sensor derived kinematics of thirty transtibial prosthesis wearers.* Sci Data 11:922. DOI: 10.1038/s41597-024-03677-3
- **Conținut:** 30 purtători proteză transtibială unilaterală, mers la viteză confortabilă pe traseu drept (~10 m), 5 trial-uri walking per subiect.
- **IMU:** Noraxon MyoMotion, **200 Hz**, plasare pe Pelvis + Thigh L/R + Shank L/R + Foot L/R. **141 coloane** per CSV: orientare quaternion (x,y,z,w), accelerații în sistem senzor și segment (m/s²), course/pitch/roll (deg), unghiuri articulare derivate (Hip Flex/Abd/Rot, Knee Flex/Abd/Rot, Ankle Dorsi/Abd/Inv) — vezi `README_IMU.txt`.
- **Referință:** sistem OMC (motion capture), unghiurile articulare furnizate sincronizat în CSV multi-header pe 3 niveluri (`[OMC]SXX.csv`), citit cu `header=[0,1,2]`.
- **Format:** `[IMU]SXX_WalkingN.csv` (semnal raw) + `[OMC]SXX_WalkingN.c3d` (raw mocap) + `[OMC]SXX.csv` (unghiuri procesate pentru toate cele 5 trial-uri).
- **Utilizare:** dataset principal pentru validarea HS/TO și a traiectoriei FSM contra OMC.

### 2.2 Dataset complementar — Wassall NTNU 2025 (dataverse.no)
- **Citare:** Wassall M. (2025). *IMU dataset of lower limb prosthetic users traversing real-world terrain with and without a walking aid.* DataverseNO, DOI: 10.18710/U8RGDL
- **Conținut:** 20 purtători proteză membru inferior (11 transtibial, 8 transfemural, 1 bilateral) traversând **teren real**: flat (FL), grass (GR), stair ascent/descent (ST), slope up/down (SL), gravel (GV), uneven (UN). Cu (wi) și fără (wo) baston.
- **IMU:** Xsens Awinda, **100 Hz**, 4 senzori — Prosthetic Shank (PS), Thigh (TH), Trunk (TR), Other Shank (OS). 18 coloane per CSV: Acc_X/Y/Z (g+grav), FreeAcc_E/N/U (fără gravitație), Gyr_X/Y/Z (rad/s), Mag_X/Y/Z, VelInc_X/Y/Z, **Steps** (stride number — segmentat deja!), **Terrain** (label etichetat), **Turn** (binar).
- **Naming:** `<Terrain><WalkAid><Trial##><Sensor>.csv` ex. `STwi01PS.csv` = stair, with walking aid, trial 01, prosthetic shank.
- **Utilizare:** comparație inter-activități, robustețe în condiții ecologice. Strides deja segmentate și terenul etichetat — scutim de muncă de adnotare.

### 2.3 Dataset auxiliar (citat, opțional folosit)
- GaitRec (Horsak 2020, Sci Data) — 75 000 trial-uri GRF, pentru benchmark statistic dacă timpul permite.

---

## 3. Algoritmi aleși (justificați științific)

### 3.1 Preprocesare
- **Filtru:** Butterworth low-pass, **ordin 4, cutoff 15 Hz, zero-phase (`scipy.signal.filtfilt`)** pentru gyro și accel filtrate; accelerație raw păstrată pentru detecția spike-urilor de impact (Catalfamo 2010, Yu 1999, Pacini Panebianco 2018).
- **Magnitudine accelerație:** `|a| = sqrt(ax² + ay² + az²)` din canalele Accel Sensor X/Y/Z (sistem senzor, m/s²).
- **Resampling:** Samala 200 Hz nativ; Wassall 100 Hz nativ — păstrăm fs nativ, parametrii filtrului calculați din fs efectiv.

### 3.2 Detecție HS/TO
Implementăm **două variante complementare**, ambele explicabile, ambele citabile:

**(A) Trojaniello-Salarian (offline gold-standard)** — `detect_events_trojaniello()`:
- Vârf pozitiv mid-swing pe `ω_shank_y` (pitch sagital) → ancoră temporală.
- HS = minim local în fereastra `[t_peak, t_peak + 350 ms]`, prag adaptiv `ω < -20°/s`.
- TO = minim local în fereastra `[t_peak − 450 ms, t_peak − 100 ms]`, prag `ω < -10°/s`.
- Pentru piciorul protetic: relaxare praguri la 60%, ferestre identice (Trojaniello 2014, Maqbool 2017).
- **Citare:** Trojaniello D., Cereatti A., Della Croce U. (2014) Gait & Posture 40:487; Aminian K. (2002) J Biomech 35:689; Salarian A. (2004) IEEE TBME 51:1434.

**(B) Maqbool R-GEDS (real-time, prietenos pentru FSM)** — `detect_events_maqbool()`:
- State machine cu 4 stări Stance/Heel-Off/Swing/HS-Pending bazat pe `ω_shank_y` + `|a_shank|`.
- Praguri scalate pentru picior protetic: `ω_HS = -60°/s`, `a_HS = 1.2 g`.
- **Citare:** Maqbool H.F. et al. (2017) IEEE TNSRE 25:1500.

**Validare:** ambele variante comparate cu evenimente derivate din OMC (Samala) — metrice: MAE temporal, sensibilitate, F1@50ms. Țintă state-of-the-art: |MAE| < 25 ms IC, < 50 ms TO, sens > 99% (Pacini Panebianco 2018).

### 3.3 Segmentare stance/swing
- Stance: `[HS_i, TO_i]`. Swing: `[TO_i, HS_{i+1}]`.
- Calcul per stride; outlier rejection: durată pas în `[0.5·median, 1.5·median]` (Trojaniello 2014).

### 3.4 Parametri temporali
- **Cadence** [pași/min] = `60 · N_HS / T_total`
- **Stride duration** [s], mean ± std, CV (coefficient of variation)
- **Stance %** = `(t_TO − t_HS) / (t_HS_{i+1} − t_HS) · 100`
- **Swing %** = `100 − Stance %`
- **Simetrie** între piciorul protetic și cel sănătos (Samala, transtibial unilateral): Symmetry Index = `2·(P − I)/(P + I)·100`.
- **Variabilitate:** SD și CV stride-to-stride (regularitate).

### 3.5 FSM control gleznă — 5 stări
Bazat direct pe **Sup, Bohara & Goldfarb 2008** (Int J Robot Res 27(2):263-273), Tabel 5
ankle θ_eq pentru cele 4 stări Vanderbilt, interpolate la 5 stări. Pentru stair/slope
adaptat din Sup, Varol & Goldfarb 2012 (IEEE T-NSRE 20:654) și Bartlett, King, Goldfarb
& Lawson 2021 (IEEE T-NSRE 29:320).

**IMPORTANT — interpretarea setpoints-urilor:** valorile reprezintă **echilibre virtuale
de impedanță** (impedance equilibrium θ_eq), NU unghiuri observate fiziologic. În
controllerele reale (BiOM/Empower, Vanderbilt) stance este controlat prin impedanță
(stiffness K + θ_eq), iar curba observată a gleznei rezultă din interacțiunea
K·(θ−θ_eq) + GRF + inerția corpului — nu prin trajectory tracking de poziție.

Pentru simulare software pură (fără model dinamic), folosim θ_eq ca țintă pentru
PCHIP interpolation: traiectoria comandată = înlănțuirea netedă a echilibrelor.
Această alegere produce o curbă **monoton descrescătoare în stance** (-8° → -25°),
elimină „balansul" vizual și e apărabilă științific prin Sup 2008.

| Stare | Trigger intrare | Setpoint Level (°) | Stair Asc | Stair Desc | Slope Up | Slope Down |
|-------|-----------------|---------------------|-----------|------------|----------|-------------|
| S1 Loading Response | HS detectat | −8 | −3 | −15 | −5 | −12 |
| S2 Mid-Stance | foot-flat (\|ω_shank\|<30°/s timp 50ms) | −15 | −8 | −20 | −12 | −18 |
| S3 Push-Off | dorsi > +3° SAU 45% stride | −25 | −18 | −30 | −22 | −28 |
| S4 Early Swing | TO detectat | −5 | −3 | −15 | −3 | −10 |
| S5 Late Swing | shank pitch peak | −3 | 0 | −8 | −1 | −5 |

**Convenție:** dorsiflexie pozitivă (+), plantarflexie negativă (−), gleznă neutră 0°.
Echilibrele Sup 2008 ankle = {−8, −25, 0, −3}° pentru modurile Mode1, Mode2, Mode3, Mode4.

**Generare traiectorie continuă:** **PCHIP** (Piecewise Cubic Hermite Interpolating
Polynomial) între waypoints — garantează monotonia, fără overshoot. Versiunea inițială
folosea Catmull-Rom care PRODUCEA OVERSHOOT vizibil de până la 22° (depășire setpoint).

**Toleranță la erori:** timeout pe stare = `1.5 × durată_mediană`; dacă evenimentul
așteptat nu apare, tranziție forțată (Varol, Sup & Goldfarb 2010).

**Generare traiectorie continuă:** spline cubic Hermite (Catmull-Rom) între setpoints, durată per stare estimată din fereastra HS→TO→HS_next. Asta evită jerk-uri (vezi `ankle_controller.generate_trajectory()`).

**Toleranță la erori:** timeout pe stare = `1.5 × durată_mediană`; dacă evenimentul așteptat nu apare, tranziție forțată (Varol, Sup & Goldfarb 2010).

### 3.6 Validare FSM
- **RMSE [°]** vs. unghi gleznă OMC real (Samala) — țintă < 5°.
- **NRMSE = RMSE/ROM** — țintă < 15% pe level, < 25% pe stairs/ramp (Bartlett 2021).
- **Pearson PCC** — țintă > 0.90 (Markowitz 2011 BiOM).
- **DTW** opțional, pentru robustețe la decalaje temporale.

---

## 4. Arhitectura repository-ului

```
easy-gait/
├── README.md                       # cum se rulează
├── pyproject.toml                  # pachet instalabil cu `pip install -e .`
├── requirements.txt                # dependențe pinned
├── docs/
│   ├── DESIGN.md                   # acest document
│   ├── ALGORITHMS.md               # detalii algoritmi + citări complete
│   └── DATASET_NOTES.md            # convenții coloane, ID-uri sensori
├── data/
│   ├── raw/                        # Samala, dataverse.no (gitignore)
│   └── processed/                  # rezultate intermediare CSV/parquet
├── src/easy_gait/
│   ├── __init__.py
│   ├── io_utils.py                 # load_samala_imu, load_samala_omc, load_wassall
│   ├── preprocessing.py            # butter_lowpass, accel_magnitude, resample
│   ├── gait_events.py              # detect_events_trojaniello, detect_events_maqbool
│   ├── segmentation.py             # split_stance_swing, reject_outlier_strides
│   ├── parameters.py               # compute_gait_params, symmetry_index, variability
│   ├── fsm.py                      # AnkleFSM (5 stări, tranziții, setpoints)
│   ├── ankle_controller.py         # generate_trajectory (Hermite spline)
│   ├── validation.py               # event_mae, traj_rmse, dtw
│   └── activity_compare.py         # comparare inter-activități Wassall
├── dashboard/
│   ├── app.py                      # Streamlit, multi-page
│   └── pages/
│       ├── 1_📊_Signal_Explorer.py
│       ├── 2_👣_Gait_Events.py
│       ├── 3_📈_Parameters.py
│       ├── 4_🦿_FSM_Simulator.py
│       └── 5_🔬_Activity_Compare.py
├── notebooks/
│   ├── 01_explore_samala.ipynb     # replicare figuri MATLAB din CS3
│   ├── 02_explore_wassall.ipynb
│   ├── 03_validate_events.ipynb
│   └── 04_fsm_validation.ipynb
└── tests/
    ├── test_preprocessing.py
    ├── test_gait_events.py         # date sintetice + 1 trial real
    ├── test_fsm.py
    └── test_parameters.py
```

## 5. Stack tehnic

| Componentă | Bibliotecă | Versiune min. | Motivație |
|------------|-----------|---------------|-----------|
| Date tabulare | pandas | 2.0 | citire/transformare CSV |
| Calcul numeric | numpy | 1.24 | array ops |
| Procesare semnal | scipy | 1.11 | butter, filtfilt, find_peaks, dtw |
| Vizualizare interactivă | plotly | 5.18 | grafice dashboard |
| Dashboard | streamlit | 1.30 | UI rapidă |
| ML opțional | scikit-learn | 1.3 | doar dacă adăugăm clasificator activitate |
| Notebook | jupyter, ipykernel | — | explorări |
| Test | pytest | 7.4 | unit tests |
| Lint/format | ruff, black | — | calitate cod |

## 6. Plan livrare (etape)

1. ✅ Cercetare științifică (HS/TO, FSM) — făcută
2. ✅ Inspectare dataset Wassall — făcută
3. ⏳ Descărcare Samala S02-S30 — în curs
4. ⏳ Structură repository + docs — în curs
5. ⏭ Module core: `io_utils`, `preprocessing`, `gait_events` (Trojaniello + Maqbool)
6. ⏭ Module: `segmentation`, `parameters`, `fsm`, `ankle_controller`
7. ⏭ Validare vs. OMC pe Samala, raport metrice
8. ⏭ Notebook-uri replicare CS3 + analiză inter-activități Wassall
9. ⏭ Dashboard Streamlit (5 pagini)
10. ⏭ Suport scriere lucrare (capitole IV-VII)

---

## 7. Diferențe față de CS3 (corectări)

CS3 conține câteva inacurații tehnice de corectat în dizertația finală:
- **Frecvență Samala:** CS3 spune "~100 Hz" — corect este **200 Hz** (verificat citind un CSV S01: 2888 frame-uri / 14.44 s).
- **Nume coloane:** CS3 menționează generic "accelerometru, giroscop" — datasetul real are 141 coloane Noraxon structurate (orientări quaternion, acceleratii senzor vs. segment, course/pitch/roll, plus unghiuri articulare derivate).
- **Pașii deja segmentați la Wassall:** CS3 nu menționează că Wassall furnizează stride numbering și terrain labels gata făcute — economisim adnotare manuală.
- **Frecvență Wassall:** confirmat 100 Hz, Xsens Awinda.

---

## 8. Referințe bibliografice complete

(vezi `docs/ALGORITHMS.md` pentru lista completă cu DOI)
