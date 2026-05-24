# Algoritmi implementați — referințe complete

Acest document conține citările complete ale tuturor algoritmilor și parametrilor folosiți în `easy-gait`. Fiecare valoare numerică (prag, fereastră, cutoff filtru, setpoint FSM) trebuie să fie justificabilă din sursele de mai jos.

---

## A. Detecție HS/TO din IMU shank

### A.1 Trojaniello-Salarian (offline, gold-standard)
- Aminian K., Najafi B., Büla C., Leyvraz P.-F., Robert P. (2002). *Spatio-temporal parameters of gait measured by an ambulatory system using miniature gyroscopes.* J Biomech 35(5):689-699. DOI: 10.1016/S0021-9290(02)00008-8
- Salarian A., Russmann H., Vingerhoets F.J.G., Burkhard P.R., Aminian K. (2004). *Gait assessment in Parkinson's disease: toward an ambulatory system for long-term monitoring.* IEEE TBME 51(8):1434-1443. PMID 15311830
- Trojaniello D., Cereatti A., Della Croce U. (2014). *Accuracy, sensitivity and robustness of five different methods for the estimation of gait temporal parameters using a single inertial sensor mounted on the lower trunk.* Gait & Posture 40(4):487-492.
- Trojaniello D. et al. (2014). *Estimation of step-by-step spatio-temporal parameters of normal and impaired gait using shank-mounted magneto-inertial sensors.* J NeuroEng Rehabil 11:152.

Parametri implementați:
- Filtru: Butterworth ord. 4, fc=15 Hz, zero-phase
- Prag minim peak mid-swing: `0.6 × percentile(ω, 95)`
- Fereastra HS: `[t_peak, t_peak + 350 ms]`
- Fereastra TO: `[t_peak − 450 ms, t_peak − 100 ms]`
- Praguri amplitudine: HS `ω < −20°/s`, TO `ω < −10°/s`
- Pentru picior protetic: scalare praguri la 0.6

### A.2 Maqbool R-GEDS (real-time, FSM-friendly)
- Maqbool H.F., Husman M.A.B., Awad M.I., Abouhossein A., Iqbal N., Dehghani-Sanij A.A. (2017). *A real-time gait event detection for lower limb prosthesis control and evaluation.* IEEE TNSRE 25(9):1500-1509. PMID 28269407

Parametri:
- Praguri intrare/ieșire swing: `ω_swing_in = +50°/s`, `ω_HS = −100°/s` (sănătos), `−60°/s` (protetic)
- Confirmare HS pe `|a| > 1.5 g` (sănătos) sau `1.2 g` (protetic)
- T_min_swing = 200 ms (refractary)

### A.3 Review-uri sistematice (pentru comparație în lucrare)
- Storm F.A., Buckley C.J., Mazzà C. (2016). *Gait event detection in laboratory and real life settings: accuracy of ankle and waist sensor based methods.* Gait & Posture 50:42-46. DOI: 10.1016/j.gaitpost.2016.08.012
- Pacini Panebianco G., Bisi M.C., Stagni R., Fantozzi S. (2018). *Analysis of the performance of 17 algorithms from a systematic review.* Gait & Posture 66:76-82. DOI: 10.1016/j.gaitpost.2018.08.025

---

## B. Filtrare semnal IMU

- Yu B., Gabriel D., Noble L., An K.N. (1999). *Estimate of the Optimum Cutoff Frequency for the Butterworth Low-Pass Digital Filter.* J Appl Biomech 15(3):318-329.
- Catalfamo P., Ghoussayni S., Ewins D. (2010). *Gait Event Detection on Level Ground and Incline Walking Using a Rate Gyroscope.* Sensors 10(6):5683-5702.

Recomandare: ordin 2 sau 4, cutoff 15 Hz pentru gait standard (fs=200 Hz), zero-phase via `scipy.signal.filtfilt`. Accelerația raw păstrată pentru detecția spike-urilor de impact.

---

## C. FSM gleznă protetică — design și setpoints

### C.1 Arhitectură FSM
- Au S., Berniker M., Herr H. (2008). *Powered ankle-foot prosthesis to assist level-ground and stair-descent gaits.* Neural Networks 21(4):654-666.
- Eilenberg M.F., Geyer H., Herr H. (2010). *Control of a powered ankle–foot prosthesis based on a neuromuscular model.* IEEE T-NSRE 18(2):164-173.
- Sup F., Bohara A., Goldfarb M. (2008). *Design and control of a powered transfemoral prosthesis.* Int. J. Robotics Research 27(2):263-273.
- Sup F., Varol H.A., Mitchell J., Withrow T.J., Goldfarb M. (2009). *Preliminary evaluations of a self-contained anthropomorphic transfemoral prosthesis.* IEEE/ASME T-Mech 14(6):667-676.
- Sup F., Varol H.A., Goldfarb M. (2012). *Control of stair ascent and descent with a powered transfemoral prosthesis.* IEEE T-NSRE 20(5):654-661.
- Bartlett H.L., King S.T., Goldfarb M., Lawson B.E. (2021). *A semi-powered ankle prosthesis and unified controller for level and sloped walking.* IEEE T-NSRE 29:320-329.
- Tucker M.R., et al. (2015). *Control strategies for active lower extremity prosthetics and orthotics: a review.* J. NeuroEng. Rehab. 12(1):1.

### C.2 Toleranță erori și tranziții fail-safe
- Varol H.A., Sup F., Goldfarb M. (2010). *Multiclass real-time intent recognition of a powered lower limb prosthesis.* IEEE T-BME 57(3):542-551.

### C.3 Date biomecanice de referință
- Winter D.A. (1991). *The Biomechanics and Motor Control of Human Gait.* University of Waterloo Press.
- Perry J., Burnfield J.M. (2010). *Gait Analysis: Normal and Pathological Function* (2nd ed.). SLACK.
- Protopapadaki A., et al. (2007). *Hip, knee, ankle kinematics and kinetics during stair ascent and descent in healthy young individuals.* Clinical Biomechanics 22(2):203-210.
- Riener R., Rabuffetti M., Frigo C. (2002). *Stair ascent and descent at different inclinations.* Gait & Posture 15(1):32-44.

---

## D. Generare traiectorie din setpoints FSM
- Spline cubic Hermite (Catmull-Rom) — Catmull E., Rom R. (1974). *A class of local interpolating splines.* Computer Aided Geometric Design.
- Alternativ: lookup table normalizat pe % gait cycle (Au 2008, BiOM commercial).

---

## E. Validare
- Markowitz J. et al. (2011). *Speed adaptation in a powered transtibial prosthesis controlled with a neuromuscular model.* Philos Trans R Soc B 366:1621-1631.
- Frossard L. et al. (2014). DOI metrici pentru cinematică gait.
- Dynamic Time Warping: Sakoe H., Chiba S. (1978). *Dynamic programming algorithm optimization for spoken word recognition.* IEEE TASSP 26:43-49.

---

## F. Dataseturi
- Samala M., Rattanakoch J., Guerra G., Tharawadeepimuk K., Nanbancha A., Niamsang W., Kerdsomnuek P., Suwanmana S., Limroongreungrat W. (2024). *A dataset of optical camera and IMU sensor derived kinematics of thirty transtibial prosthesis wearers.* Sci Data 11:922. DOI: 10.1038/s41597-024-03677-3
- Wassall M. (2025). *IMU dataset of lower limb prosthetic users traversing real-world terrain with and without a walking aid.* DataverseNO, DOI: 10.18710/U8RGDL
- Horsak B. et al. (2020). *GaitRec, a large-scale ground reaction force dataset of healthy and impaired gait.* Sci Data 7:143.

---

## G. Aplicații specifice amputat transtibial
- Maqbool 2017 (vezi A.2) — referința principală pentru detecție evenimente la amputat.
- Rattanasak A. et al. (2022). *Real-Time Gait Phase Detection Using Wearable Sensors for Transtibial Prosthesis Based on a kNN Algorithm.* Sensors 22:4242.
- Romijnders R. et al. (2022). *A Deep Learning Approach for Gait Event Detection from a Single Shank-Worn IMU.* Sensors 22:3859.
