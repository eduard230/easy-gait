# DOSAR DE PROIECT — adevărul de bază (ground-truth)

> Fapte atomice extrase **direct din cod și din rezultatele reale** de doi agenți Opus 4.8 care au explorat proiectul. Acesta este reperul contra căruia au fost verificate afirmațiile din raport.

## Domeniu 1

Proiectul "easy-gait" este o platformă Python pentru analiza ciclului de mers din IMU și simularea controlului FSM al unei glezne protetice transtibiale, validată pe două dataseturi (Samala 2024 — IMU Noraxon 200 Hz + OMC C3D; Wassall NTNU 2025 — IMU Xsens 100 Hz cu etichete de teren).

Fluxul de date IMPLEMENTAT: (1) preprocesare — filtru Butterworth low-pass zero-phase (filtfilt) ord. 4, cutoff 15 Hz pe gyro/omega, magnitudine accelerație ||a||=norm; derivare numerică gradient pentru a obține omega din unghi (Samala dă unghiuri, nu gyro). (2) Detecție evenimente HS/TO — două metode: Trojaniello (offline, vârfuri mid-swing cu prag adaptiv 0.6×P95, ferestre HS [0,350ms] prag ω≤−20°/s, TO [−450,−100ms] prag ω≤−10°/s; scalare ×0.6 pentru protetic) și Maqbool R-GEDS (FSM real-time cu 3 stări STANCE/SWING/HS_PENDING, praguri ω_swing=50, ω_HS=−100 dps, a_HS=1.5g, relaxate la −60 dps/1.2g pentru protetic, refractar 0.25s). (3) Ground truth OMC — Zeni 2008 pe coordonata X relativă la centrul pelvisului, filtru 6 Hz, gap minim 0.4s. (4) Aliniere OMC↔IMU prin cross-correlation pe unghiul gleznei. (5) Segmentare cicluri HS_i→TO_i→HS_{i+1} cu rejecție outlieri 0.5–1.5×median stride. (6) Parametri — cadență (2×60×n/total), stride mean/std (ddof=1)/CV, stance%, Symmetry Index Robinson. (7) FSM 5 stări (Loading/Mid-Stance/Push-Off/Early-Swing/Late-Swing) cu SETPOINTS impedanță per activitate. (8) Traiectorie PCHIP cu waypoint la 30% din durata stării + smoothing 40ms.

REZULTATE reale (data/processed + tables): detecție evenimente are sensibilitate/F1 SLABE (Trojaniello HS sens 0.584/F1 0.377; Maqbool HS sens 0.633), MAE 60–80 ms — mult sub pragurile de acceptabilitate din docstring (≤25ms, sens≥99%). Traiectoria FSM corelează NEGATIV cu OMC (PCC mediu −0.244, RMSE 13.72°), pe când unghiul IMU direct e mult mai bun (PCC 0.652, RMSE 8.75°). Datele Wassall pe teren arată cadență mai mică pe scări (82.8) și mai mare pe iarbă (105.3).

**Fișiere cheie:**
- easy-gait/src/easy_gait/preprocessing.py — Butterworth filtfilt (cutoff 15Hz/ord4), derivata gradient, gyro_pitch_dps, detect_quiet_segments
- easy-gait/src/easy_gait/gait_events.py — Trojaniello (praguri/ferestre/scalare 0.6 protetic) și Maqbool R-GEDS (3 stări, praguri ω/accel, refractar)
- easy-gait/src/easy_gait/omc_events.py — Zeni 2008 (X relativ la pelvis, filtru 6Hz), align_omc_to_imu cross-correlation
- easy-gait/src/easy_gait/io_utils.py — compute_ankle_angle (-(shank-foot), ref 100, filtru 6Hz, clip ±35°), încărcare Samala/Wassall, constante fs
- easy-gait/src/easy_gait/segmentation.py — build_cycles, reject_outliers 0.5-1.5×median, stance/swing%
- easy-gait/src/easy_gait/parameters.py — cadență (×2), stride mean/std ddof=1, CV, Symmetry Index Robinson
- easy-gait/src/easy_gait/fsm.py — FSM 5 stări, SETPOINTS per activitate, praguri tranziție/timeout
- easy-gait/src/easy_gait/ankle_controller.py — generate_trajectory PCHIP waypoint 30%, smoothing 40ms
- easy-gait/src/easy_gait/validation.py — event_mae/F1, traj_rmse/nrmse/pcc, dtw_distance
- easy-gait/src/easy_gait/activity_compare.py — procesare Wassall PS (Gyr_Y rad2deg, Trojaniello prosthetic=True), agregare per teren
- easy-gait/src/easy_gait/prosthesis_viz.py — geometrie 2D proteză transtibială
- easy-gait/scripts/validate_events_all.py — pipeline validare HS/TO vs OMC (tol 150ms, prosthetic=True forțat)
- easy-gait/scripts/validate_fsm_all.py — pipeline validare traiectorie FSM/IMU vs OMC
- easy-gait/scripts/compute_wassall_summary.py — agregare Wassall per teren/walkaid
- easy-gait/notebooks/tables/tab03_events_validation_summary.csv — rezultate reale detecție evenimente
- easy-gait/notebooks/tables/tab04_fsm_validation_summary.csv — rezultate reale traiectorie (FSM PCC negativ vs IMU pozitiv)
- easy-gait/notebooks/tables/tab02_wassall_per_terrain.csv și data/processed/wassall_per_terrain.csv — parametri per teren
- easy-gait/notebooks/tables/tab01_population_summary.csv/.txt — sumar populație Samala (prosth vs intact)
- easy-gait/tests/ (test_gait_events/fsm/parameters/preprocessing) — confirmă comportamentul funcțiilor

**Fapte verificate:**

- butter_lowpass: cutoff implicit 15.0 Hz, ordin implicit 4, btype='low', zero-phase prin scipy.signal.filtfilt (ordin efectiv 2×order=8).  
  `easy-gait/src/easy_gait/preprocessing.py:16-46`
- butter_lowpass calculează wn = cutoff_hz / (0.5*fs); validează 0<wn<1 altfel ValueError.  
  `easy-gait/src/easy_gait/preprocessing.py:39-42`
- padlen = min(3 * max(len(a), len(b)), len(signal) - 1) — pad explicit pentru semnale scurte.  
  `easy-gait/src/easy_gait/preprocessing.py:45`
- derivative = np.gradient(signal, 1.0/fs) (derivată centrată).  
  `easy-gait/src/easy_gait/preprocessing.py:63-65`
- gyro_pitch_dps derivă omega (deg/s) din unghi prin derivative + butter_lowpass cutoff 15 Hz (Samala nu are gyro direct, doar unghiuri shank).  
  `easy-gait/src/easy_gait/preprocessing.py:68-76`
- normalize_to_g împarte la 9.80665 m/s².  
  `easy-gait/src/easy_gait/preprocessing.py:79-81`
- detect_quiet_segments: prag implicit 30.0 dps, min_samples implicit 25 (=125 ms @200Hz); returnează True unde |ω|<prag pe ≥min_samples consecutive.  
  `easy-gait/src/easy_gait/preprocessing.py:84-107`
- Trojaniello: parametri impliciti min_stride_s=0.5, hs_window_s=(0.0,0.35), to_window_s=(-0.45,-0.10), cutoff_hz=15.0, prosthetic=False.  
  `easy-gait/src/easy_gait/gait_events.py:52-61`
- Trojaniello prag vârfuri mid-swing: peak_height = 0.6 * P95 (percentila 95 a omega); dacă P95<=0 returnează gol.  
  `easy-gait/src/easy_gait/gait_events.py:90-93`
- Trojaniello praguri: scale = 0.6 if prosthetic else 1.0; hs_thr = -20.0*scale; to_thr = -10.0*scale (deci -12/-6 dps pentru protetic).  
  `easy-gait/src/easy_gait/gait_events.py:94-96`
- Trojaniello detecție vârfuri: find_peaks(omega, height=peak_height, distance=int(min_stride_s*fs)).  
  `easy-gait/src/easy_gait/gait_events.py:99-100`
- Trojaniello HS = argmin omega în fereastra [p+0, p+0.35*fs], acceptat doar dacă val<=hs_thr; TO = argmin în [p-0.45*fs, p-0.10*fs], acceptat dacă val<=to_thr.  
  `easy-gait/src/easy_gait/gait_events.py:110-127`
- Maqbool parametri impliciti: omega_swing_in_dps=50.0, omega_hs_dps=-100.0, accel_hs_g=1.5, t_min_swing_s=0.2, refractary_s=0.25, cutoff_hz=15.0.  
  `easy-gait/src/easy_gait/gait_events.py:141-153`
- Maqbool: dacă prosthetic=True, suprascrie omega_hs_dps=-60.0 și accel_hs_g=1.2.  
  `easy-gait/src/easy_gait/gait_events.py:180-182`
- Maqbool: omega filtrată cu butter (cutoff 15Hz), dar a_mag NEfiltrată (pentru spike-uri de impact); a_g = a_mag/9.80665.  
  `easy-gait/src/easy_gait/gait_events.py:176-178`
- Maqbool FSM 3 stări: STANCE→SWING (omega>50 dps ȘI i-t_last_hs>refract → emite TO); SWING→HS_PENDING (i-t_to>min_swing ȘI omega<-100); HS_PENDING→STANCE (a_g>1.5g → emite HS).  
  `easy-gait/src/easy_gait/gait_events.py:195-208`
- Maqbool fallback HS: dacă accel nu confirmă în i-t_to>int(0.6*fs) (=120 samples @200Hz, ~600ms), acceptă HS pe ω.  
  `easy-gait/src/easy_gait/gait_events.py:209-213`
- pair_hs_to formează triplete [HS_i, TO, HS_{i+1}] doar dacă TO strict între cei doi HS (ia primul TO candidat).  
  `easy-gait/src/easy_gait/gait_events.py:227-241`
- Zeni 2008 (OMC): HS = max local pe (heel-pelvis).x (find_peaks pe semnal filtrat), TO = min local pe (toe-pelvis).x (find_peaks pe -semnal).  
  `easy-gait/src/easy_gait/omc_events.py:120-123`
- Zeni: filtru low-pass implicit 6.0 Hz ordin 4 pe poziții markeri, min_event_gap_s implicit 0.4 (distance = int(0.4*fs)).  
  `easy-gait/src/easy_gait/omc_events.py:75-81,84-92,118`
- Zeni: axa de mers aleasă automat = argmax(np.ptp(pelvis_center, axis=1)) (de obicei X); skip dacă n<int(fs*0.5).  
  `easy-gait/src/easy_gait/omc_events.py:104-110`
- detect_omc_events_from_c3d: toe_marker implicit 'MTH3'; centrul pelvisului = (PELVIS_L+PELVIS_R)/2, fallback PELVIS_SUP, apoi (ASIS_L+ASIS_R)/2.  
  `easy-gait/src/easy_gait/omc_events.py:128-160`
- OMC fs citit din C3D RATE; load_c3d_markers folosește ezc3d, markeri în mm (3×n_frames).  
  `easy-gait/src/easy_gait/omc_events.py:55-72`
- align_omc_to_imu: cross-correlation (scipy.signal.correlate mode='valid') pe semnale normalizate (z-score cu +1e-9); cere fs egale altfel ValueError; returnează argmax (offset OMC-în-IMU).  
  `easy-gait/src/easy_gait/omc_events.py:179-210`
- compute_ankle_angle: raw = -(shank_pitch - foot_pitch); convenție dorsi(+)/plantar(-); centrat pe reference_idx (implicit 100 = 0.5s static @200Hz).  
  `easy-gait/src/easy_gait/io_utils.py:378-389`
- compute_ankle_angle: filtru Butterworth ordin 4, smooth_cutoff_hz implicit 6.0 Hz, fs implicit 200.0; clipping la ±clip_deg implicit 35.0°.  
  `easy-gait/src/easy_gait/io_utils.py:346-350,391-397`
- compute_ankle_angle înlocuiește coloanele Noraxon 'Ankle Dorsiflexion LT/RT' considerate inconsistente (semn opus, valori non-fiziologice în swing).  
  `easy-gait/src/easy_gait/io_utils.py:196-206,357-358`
- reject_outliers: păstrează cicluri cu stride_s în [0.5*median, 1.5*median] (lo=0.5, hi=1.5 impliciti).  
  `easy-gait/src/easy_gait/segmentation.py:67-74`
- GaitCycle: stance = [hs_start,to], swing = [to,hs_end], stride = [hs_start,hs_end]; stance_pct = 100*stance_samples/max(stride_samples,1).  
  `easy-gait/src/easy_gait/segmentation.py:36-58`
- Cadență: cadence_per_side = 60*n_cycles/total_s; cadence_total = 2.0*cadence_per_side (un stride pe un picior = 1 pas; total dublu).  
  `easy-gait/src/easy_gait/parameters.py:62-64`
- Stride std folosește ddof=1 (std eșantion) doar dacă len>1, altfel 0; CV = std/mean.  
  `easy-gait/src/easy_gait/parameters.py:66-68,77,79`
- Symmetry Index (Robinson 1987): SI = 100*2*(prosthetic-intact)/(prosthetic+intact); 0 dacă sumă=0.  
  `easy-gait/src/easy_gait/parameters.py:85-94`
- FSM 5 stări IntEnum: S1_LOADING=1, S2_MIDSTANCE=2, S3_PUSHOFF=3, S4_EARLY_SWING=4, S5_LATE_SWING=5.  
  `easy-gait/src/easy_gait/fsm.py:28-33`
- SETPOINTS level (deg): S1=-8, S2=-15, S3=-25, S4=-5, S5=-3 (toate plantarflexie/negative, monoton descrescător în stance).  
  `easy-gait/src/easy_gait/fsm.py:52-60`
- SETPOINTS stair_ascent: S1=-3,S2=-8,S3=-18,S4=-3,S5=0; stair_descent: S1=-15,S2=-20,S3=-30,S4=-15,S5=-8.  
  `easy-gait/src/easy_gait/fsm.py:61-76`
- SETPOINTS slope_ascent: S1=-5,S2=-12,S3=-22,S4=-3,S5=-1; slope_descent: S1=-12,S2=-18,S3=-28,S4=-10,S5=-5.  
  `easy-gait/src/easy_gait/fsm.py:77-92`
- FSMConfig: foot_flat_omega_thr_dps=30.0, foot_flat_min_samples=10 (=50ms @200Hz), pushoff_dorsi_thr_deg=3.0 (relaxat de la 8°), pushoff_phase_fraction=0.45, max_dwell_factor=1.5, midswing_window_s=(0.15,0.35).  
  `easy-gait/src/easy_gait/fsm.py:96-108`
- FSM timeout: max_dwell = max(int(1.5*median_stride), int(0.3*fs)); median_stride = median(diff(hs_idx)) sau 1.0*fs dacă <2 HS.  
  `easy-gait/src/easy_gait/fsm.py:149-154`
- FSM S1→S2: foot-flat când |omega|<30 dps pe ≥10 samples consecutive, sau pe timeout (i-last_transition>max_dwell).  
  `easy-gait/src/easy_gait/fsm.py:179-189`
- FSM S2→S3: necesită min_dwell = int(0.20*median_stride); trigger pe unghi (ankle_angle>3.0°) SAU timeout (i-last>0.45*median_stride).  
  `easy-gait/src/easy_gait/fsm.py:191-203`
- FSM S3→S4: pe TO event (gestionat la i in to_set) sau timeout i-last>int(0.3*median_stride).  
  `easy-gait/src/easy_gait/fsm.py:175-177,205-208`
- FSM S4→S5: peak local ω în fereastra dt∈[0.15,0.35]s post-TO (ω[i-1]>ω[i] ȘI ω[i-1]>0) sau dt>0.35s.  
  `easy-gait/src/easy_gait/fsm.py:210-218`
- FSM: HS event forțează S1_LOADING și resetează ff_counter; TO event forțează S4_EARLY_SWING (prioritate peste logica de stare).  
  `easy-gait/src/easy_gait/fsm.py:173-177`
- Traiectorie PCHIP: waypoint_position implicit 0.30 (waypoint la 30% din durata stării), smooth_window_s implicit 0.04 (40ms moving-average).  
  `easy-gait/src/easy_gait/ankle_controller.py:26-32,73-79`
- generate_trajectory folosește scipy.interpolate.PchipInterpolator (extrapolate=True) — garantează monotonie fără overshoot; versiunea anterioară CubicHermiteSpline producea overshoot pană la 22°.  
  `easy-gait/src/easy_gait/ankle_controller.py:14-17,21,92-95`
- Smoothing final: win = max(int(0.04*fs),3), forțat impar, kernel uniform np.convolve mode='same'.  
  `easy-gait/src/easy_gait/ankle_controller.py:97-104`
- event_mae: pentru fiecare truth caută cel mai apropiat detected în ±tol_ms (greedy 1:1 cu matched_det set); întoarce mae_ms, bias_ms, sens(recall), ppv(precision), f1=2*sens*ppv/(sens+ppv).  
  `easy-gait/src/easy_gait/validation.py:18-65`
- traj_nrmse = RMSE / (max(truth)-min(truth)) — returnat ca fracție [0,∞), NU procent.  
  `easy-gait/src/easy_gait/validation.py:75-81`
- Constante fs: SAMALA_FS=200 Hz, WASSALL_FS=100 Hz.  
  `easy-gait/src/easy_gait/io_utils.py:20-21`
- Wassall: Gyr în rad/s convertit la deg/s (np.rad2deg) înainte de Trojaniello; Trojaniello apelat cu prosthetic=True pentru shank PS.  
  `easy-gait/src/easy_gait/activity_compare.py:81-83`
- detect_prosthetic_side: euristică pe ROM ankle (rom mai mic = protetic), 'left' dacă rom_lt<rom_rt.  
  `easy-gait/src/easy_gait/io_utils.py:225-233`
- Validare evenimente (rezultat real): Trojaniello n_trials=290, HS MAE 79.8 ms (median 77.5), HS sens 0.584, HS F1 0.377; TO MAE 60.7 ms, TO sens 0.613.  
  `easy-gait/notebooks/tables/tab03_events_validation_summary.csv→rând Trojaniello`
- Validare evenimente (rezultat real): Maqbool n_trials=290, HS MAE 60.2 ms (median 56.7), HS sens 0.633, HS F1 0.395; TO MAE 76.9 ms, TO sens 0.653.  
  `easy-gait/notebooks/tables/tab03_events_validation_summary.csv→rând Maqbool`
- Validare traiectorie FSM vs OMC (rezultat real): n=290, RMSE 13.72°±4.93, NRMSE 0.868, PCC mediu -0.244 (median -0.224), ROM_omc 22.9° vs ROM_pred 14.6°.  
  `easy-gait/notebooks/tables/tab04_fsm_validation_summary.csv→rând fsm`
- Validare traiectorie IMU vs OMC (rezultat real): n=290, RMSE 8.75°±5.49, NRMSE 0.529, PCC mediu 0.652 (median 0.65), ROM_pred 25.8° — net superioară FSM.  
  `easy-gait/notebooks/tables/tab04_fsm_validation_summary.csv→rând imu`
- Wassall per teren (cadență steps/min mean): flat 95.06 (n=69), grass 105.28 (n=39), gravel 87.51 (n=39), slope 92.81 (n=110), stair 82.76 (n=119), uneven 93.16 (n=92).  
  `easy-gait/notebooks/tables/tab02_wassall_per_terrain.csv→toate rândurile`
- Wassall stride_cv mean: cel mai mare pe stair (0.145/0.15) și uneven/grass; cel mai mic pe flat (0.051).  
  `easy-gait/data/processed/wassall_per_terrain.csv→stride_cv_mean`
- Populație Samala (tab01 txt): PROSTH n=30 laturi cadență 100.1±11.7, stride 1.215±0.142s, stance 51.7±9.8%, ROM ankle 17.0±16.4°; INTACT n=29 cadență 100.3±11.3, ROM ankle 38.6±11.9°.  
  `easy-gait/notebooks/tables/tab01_population_summary.txt`
- Validare evenimente folosește toleranțe TOL_HS_MS=150.0 și TOL_TO_MS=150.0 ms (mai relaxate decât pragul 25/50ms din docstring validation.py).  
  `easy-gait/scripts/validate_events_all.py:35-36`
- Validare: ambii algoritmi rulați cu is_prosthetic=True forțat (lot mixt, prag relaxat 'pe sigur') pe toți subiecții Samala.  
  `easy-gait/scripts/validate_events_all.py:89-92,103-106`
- FSM validation pipeline: FSM rulat cu activity='level', events Trojaniello prosthetic=True; ankle_real centrat pe primul HS detectat (ref_idx=hs_idx[0]).  
  `easy-gait/scripts/validate_fsm_all.py:78-88`
- prosthesis_viz: geometrie L_TIBIA=0.40m, L_FOOT_FRONT=0.20, L_FOOT_BACK=0.06, FOOT_THICKNESS=0.04, PYLON_TILT_DEG=7.0; fără scaling/clip pe unghi.  
  `easy-gait/src/easy_gait/prosthesis_viz.py:26-53`

**Discrepanțe interne observate (cod vs. docstring / între module):**
- ⚠️ REZULTAT vs DOCSTRING: validation.py:8-11 declară praguri de acceptabilitate IC |MAE|≤25ms sens≥99%, TO≤50ms sens≥98%, Traj PCC>0.90 — dar rezultatele reale (tab03/tab04) sunt MULT sub: HS MAE 60-80ms, sens 0.58-0.63, FSM PCC mediu NEGATIV (-0.244).
- ⚠️ FSM PCC NEGATIV: ankle_controller/fsm produc o traiectorie care corelează negativ cu OMC (tab04 fsm PCC -0.244), pe când unghiul IMU direct (compute_ankle_angle) corelează pozitiv (PCC 0.652) — controlul FSM comandat NU urmărește forma fiziologică reală, contrar afirmației din ankle_controller.py:5-8 despre evitarea overshoot/comportament biomecanic corect.
- ⚠️ SETPOINTS FSM 'level' sunt TOATE plantarflexie (negative, -8 la -25°) și interpretate explicit ca echilibre de impedanță, NU unghiuri observate fiziologic (fsm.py:36-48) — deci ROM_pred (14.6°) e mult sub ROM_omc (22.9°), iar comparația directă RMSE/PCC vs unghi articular OMC e conceptual nepotrivită (admis în comentariu, dar produce metrice slabe).
- ⚠️ compute_ankle_angle docstring (io_utils.py:201-202,357-358) afirmă convenția validată HS≈0/push-off≈-18°/mid-swing≈+10°, dar reference_idx implicit=100 (0.5s static) NU coincide cu HS; pipeline-ul FSM îl recalibrează pe primul HS (validate_fsm_all.py:80-81) — două convenții de calibrare diferite în cod.
- ⚠️ Maqbool în validate_events_all.py:88,103-106 primește shank_pitch_rate = gyro_pitch_dps (omega derivat din unghi + filtrat), deci omega e re-filtrat încă o dată în interiorul detect_events_maqbool (gait_events.py:176) — dublă filtrare a omega.
- ⚠️ Docstring gait_events.py:14 descrie convenția shank pitch cu minim negativ la HS ~-100°/s, dar pragul Trojaniello hs_thr implicit e doar -20°/s (×0.6=-12 pentru protetic) — prag mult mai permisiv decât amplitudinea descrisă, contribuind la PPV/F1 scăzut (multe false-positive: n_imu_hs > n_omc_hs în events_validation.csv).

## Domeniu 2

Proiect "easy-gait": platformă de analiză a mersului și simulare de control de gleznă protetică pe DOUĂ seturi de date publice. Samala 2024 (Sci Data 11:922, DOI 10.1038/s41597-024-03677-3): 30 purtători de proteză TRANSTIBIALĂ, toate PASIVE (24 SACH, 3 Dynamic/ESR, 2 sPace, 1 Single axis), IMU Noraxon 200 Hz (141 coloane) + referință optică OMC (C3D + CSV unghiuri @200 Hz), 5 probe de mers pe plat per subiect. Wassall 2025 (dataverse.no DOI 10.18710/U8RGDL): 20 participanți (11 transtibial, 8 transfemural, 1 bilateral; 2F/18M; 64.6±11.8 ani), IMU Xsens Awinda 100 Hz, 4 senzori (PS, TH, TR, OS), teren variat (plat/scări/pante/iarbă/pietriș/denivelat) cu/fără baston. Flux: io_utils încarcă brut → preprocessing (Butterworth) → gait_events (Trojaniello offline + Maqbool real-time) → omc_events (Zeni 2008 ground-truth, aliniere cross-corr pe unghi gleznă) → parameters (cadență, stride, stance%, CV, Symmetry Index) → fsm (5 stări + SETPOINTS impedanță) → ankle_controller (PCHIP). Scripturile validate_events_all.py, validate_fsm_all.py, compute_wassall_summary.py produc data/processed/. Notebooks 01-04 produc 12 figuri PNG și 5 tabele CSV/TXT. Rezultate reale cheie: detecție evenimente Samala (290 trial-rows/algoritm) — Maqbool bate Trojaniello la HS (MAE 60.2 vs 79.8 ms, sens 0.633 vs 0.584), Trojaniello bate Maqbool la TO (MAE 60.7 vs 76.9 ms); PPV mic la ambii (~0.28-0.29). Validare FSM: unghiul derivat din IMU e mult mai aproape de OMC decât traiectoria FSM (RMSE 8.75° vs 13.72°, PCC +0.652 vs -0.244 negativ). Biomecanică prosth vs intact: ROM gleznă 17.0±16.4° vs 38.6±11.9° (proteze pasive → ROM mic). Dashboard Streamlit (6 pagini) și demo-web Flask recalculează metricile live, nu citesc CSV-urile de validare.

**Fișiere cheie:**
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/data/processed/events_validation.csv — validare HS/TO IMU vs OMC, 580 rânduri (29 subiecți × trials × laturi × 2 algoritmi)
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/data/processed/fsm_validation.csv — validare traiectorie FSM/IMU vs unghi gleznă OMC, 580 rânduri
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/data/processed/wassall_per_trial.csv — parametri per trial Wassall (506 rânduri, 16 participanți)
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/data/processed/wassall_per_terrain.csv — agregare mean±std per teren (8 categorii)
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/data/processed/wassall_per_terrain_walkaid.csv — agregare per (teren, baston)
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/tables/tab01_population_summary.csv și .txt — biomecanică prosth vs intact
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/tables/tab03_events_validation_summary.csv — sumar Trojaniello vs Maqbool
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/tables/tab04_fsm_validation_summary.csv — sumar FSM vs IMU
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/tables/tab05_fsm_validation_per_subject.csv — RMSE/PCC per subiect
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/src/easy_gait/samala_metadata.py — metadate 30 subiecți Samala (tip proteză, foot_type, latură)
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/src/easy_gait/io_utils.py — constante dataset (SAMALA_FS=200, WASSALL_FS=100, terenuri, senzori)
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/src/easy_gait/fsm.py — FSM 5 stări + SETPOINTS + FSMConfig
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/src/easy_gait/validation.py — formule MAE/F1/RMSE/NRMSE/PCC
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/src/easy_gait/parameters.py — formule cadență, CV, stance%, Symmetry Index
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/scripts/validate_events_all.py — pipeline validare evenimente (TOL=150ms)
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/scripts/validate_fsm_all.py — pipeline validare FSM/IMU vs OMC
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/scripts/compute_wassall_summary.py — pipeline agregare Wassall
- D:/OneDrive - Realworld Holding b.v/Documents/67/datasets/dataverse_README.txt — sursă oficială Wassall (20 participanți, terenuri, senzori, 100Hz)
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/data/raw/samala_2024/README_IMU.txt și README_OMC.txt — descriere semnale Samala @200Hz
- D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/dashboard/app.py și pages/4_Simulator_FSM.py — afirmații dashboard (ținte RMSE<5°, NRMSE<15%)
- D:/OneDrive - Realworld Holding b.v/Documents/67/demo-web/app/templates/ — varianta web Flask (6 pagini)

**Fapte verificate:**

- Samala: 200 Hz, verificat empiric pe S01 (2888 frame / 14.44 s); Wassall: 100 Hz declarat în README dataverse.no  
  `easy-gait/src/easy_gait/io_utils.py:20-21`
- Samala IMU Noraxon: 141 coloane @ 200 Hz (140 parametri + coloana frame)  
  `easy-gait/src/easy_gait/io_utils.py:77 ; data/raw/samala_2024/README_IMU.txt:16-18`
- Samala: 30 subiecți S01..S30, fiecare cu 5 probe Walking1..5 (IMU CSV) + OMC (CSV unghiuri + C3D Static/Walking1..5 + .cal)  
  `data/raw/samala_2024/S01/ listing`
- Toate cele 30 de proteze Samala sunt PASIVE, transtibiale; nicio gleznă acționată (BiOM/Empower/Proprio)  
  `easy-gait/src/easy_gait/samala_metadata.py:8-10`
- Distribuție tip foot Samala: 24/30 SACH, 3/30 Dynamic (ESR), 2/30 sPace (Endolite), 1/30 Single axis  
  `easy-gait/src/easy_gait/samala_metadata.py:13-19,44-73`
- Wassall: 20 participanți (11 transtibial, 8 transfemural, 1 bilateral TT-drept/TF-stâng), 2F/18M, 64.6±11.8 ani  
  `datasets/dataverse_README.txt:22`
- Wassall: 4 IMU per probă — PS (prosthetic shank), TH (prosthetic thigh), TR (trunk ~L4), OS (other shank); P7 fără trunk (other thigh)  
  `datasets/dataverse_README.txt ; easy-gait/src/easy_gait/io_utils.py:34-39`
- Wassall etichete teren: 1=flat, 2=grass, 4=stair_ascent, 5=stair_descent, 6=slope_ascent, 7=slope_descent, 8=gravel, 9=uneven; strides din peaks Gyroscope Y  
  `easy-gait/src/easy_gait/io_utils.py:23-32 ; datasets/dataverse_README.txt:26`
- Trojaniello (290 trial-rows): HS MAE mean 79.8 / median 77.5 ms, HS sens 0.584, HS F1 0.377; TO MAE mean 60.7 / median 58.3 ms, TO sens 0.613, TO F1 0.377  
  `easy-gait/notebooks/tables/tab03_events_validation_summary.csv:2`
- Maqbool (290 trial-rows): HS MAE mean 60.2 / median 56.7 ms, HS sens 0.633, HS F1 0.395; TO MAE mean 76.9 / median 75.8 ms, TO sens 0.653, TO F1 0.373  
  `easy-gait/notebooks/tables/tab03_events_validation_summary.csv:3`
- PPV mic la ambii (HS PPV Trojaniello 0.283, Maqbool 0.291) → multe falsuri pozitive; n_imu_hs mult > n_omc_hs  
  `data/processed/events_validation.csv (recalculat)`
- events_validation.csv: 580 rânduri; HS valid Trojaniello=237, Maqbool=250 (restul NaN), deși tab03 raportează n_trials=290; S04 absent complet (29/30 subiecți)  
  `data/processed/events_validation.csv (recalculat)`
- Toleranța de potrivire eveniment: ±150 ms HS și TO (Pacini Panebianco 2018)  
  `easy-gait/scripts/validate_events_all.py:35-36`
- FSM vs OMC (sursa fsm, n=290): RMSE 13.72±4.93° (median 13.6), NRMSE mean 0.868/median 0.582, PCC mean -0.244/median -0.224, ROM_pred 14.6° vs ROM_omc 22.9°  
  `easy-gait/notebooks/tables/tab04_fsm_validation_summary.csv:2`
- IMU vs OMC (sursa imu, n=290): RMSE 8.75±5.49° (median 7.46), NRMSE mean 0.529/median 0.358, PCC mean +0.652/median 0.650, ROM_pred 25.8° vs ROM_omc 22.9°  
  `easy-gait/notebooks/tables/tab04_fsm_validation_summary.csv:3`
- Per-subiect (tab05): toate PCC FSM ~0 sau negative (S01 -0.43, S19 -0.66); toate PCC IMU pozitive (0.27..0.95, S01 0.89, S03 0.95)  
  `easy-gait/notebooks/tables/tab05_fsm_validation_per_subject.csv:2-30`
- PROSTH (n=30 laturi): cadență 100.1±11.7 pași/min, stride 1.215±0.142 s, stance 51.7±9.8%, ROM gleznă 17.0±16.4°  
  `easy-gait/notebooks/tables/tab01_population_summary.txt:2-6`
- INTACT (n=29 laturi): cadență 100.3±11.3 pași/min, stride 1.212±0.137 s, stance 55.5±4.1%, ROM gleznă 38.6±11.9°  
  `easy-gait/notebooks/tables/tab01_population_summary.txt:8-12`
- tab01: 30 rânduri prosth dar 29 intact; S27 doar prosth dreapta cu stance anomal 2.3% și ROM 67°; S22 prosth=intact=70.0, S23 intact=70.0 (plafonate)  
  `easy-gait/notebooks/tables/tab01_population_summary.csv:44-47,54`
- Wassall cadență per teren (pași/min): flat 95.1, grass 105.3 (max), gravel 87.5, slope 92.8, stair 82.8, uneven 93.2, STEP_MULTI 87.3, CS 80.6  
  `easy-gait/data/processed/wassall_per_terrain.csv:2-9`
- Wassall stride_cv: max stair 0.145 și STEP_MULTI 0.14, min flat 0.051; slope 0.061, uneven 0.071, grass 0.083, gravel 0.088, CS 0.086  
  `easy-gait/data/processed/wassall_per_terrain.csv:2-9`
- Wassall stance%: CS 59.6, stair 59.5, gravel 55.5, STEP_MULTI 55.9, uneven 54.6, flat 54.7, slope 54.0, grass 52.1; stride_mean_s: flat 1.277, stair 1.514, grass 1.237  
  `easy-gait/data/processed/wassall_per_terrain.csv:2-9`
- Wassall n_trials per teren: stair 119, slope 110, uneven 92, flat 69, gravel 39, grass 39, STEP_MULTI 29, CS 9 (total 506 rânduri, 5746 cicluri, doar 16 participanți)  
  `data/processed/wassall_per_trial.csv (recalculat)`
- Efect baston global: cu baston cadență 88.2 (n=214)/stance 57.5%/stride 1.420 s, fără baston 93.3 (n=259)/stance 54.2%/stride 1.316 s; cv ~egal (0.086 vs 0.088)  
  `data/processed/wassall_per_trial.csv (recalculat) ; wassall_per_terrain_walkaid.csv`
- Efect baston la stair: cu baston cadență 76.9 vs fără 87.1, stance 62.0% vs 57.6%  
  `easy-gait/data/processed/wassall_per_terrain_walkaid.csv:14-15`
- FSM 5 stări: S1 Loading (HS), S2 Mid-Stance (|ω_shank|<30°/s 50ms), S3 Push-Off, S4 Early Swing (TO), S5 Late Swing (shank pitch peak)  
  `easy-gait/src/easy_gait/fsm.py:3-8,28-33`
- SETPOINTS level (θ_eq impedanță deg): S1=-8, S2=-15, S3=-25, S4=-5, S5=-3 (Sup 2008 Table 5); convenție dorsiflexie + / plantarflexie -  
  `easy-gait/src/easy_gait/fsm.py:53-60`
- SETPOINTS: stair_ascent (-3/-8/-18/-3/0), stair_descent (-15/-20/-30/-15/-8), slope_ascent (-5/-12/-22/-3/-1), slope_descent (-12/-18/-28/-10/-5)  
  `easy-gait/src/easy_gait/fsm.py:61-92`
- FSMConfig: foot_flat_omega_thr=30°/s, foot_flat_min_samples=10 (50ms@200Hz), pushoff_dorsi_thr=3.0° (relaxat de la 8°), pushoff_phase_fraction=0.45, max_dwell_factor=1.5, midswing_window=(0.15,0.35)s  
  `easy-gait/src/easy_gait/fsm.py:99-108`
- Formule: cadență = 2×(60×n_steps_per_side/total_s); stride CV = std/mean; Symmetry Index Robinson 1987 = 2·(P−I)/(P+I)·100  
  `easy-gait/src/easy_gait/parameters.py:59-68,85-94`
- Formule validare: sens=n_matched/len(truth), ppv=n_matched/len(det), f1=2·sens·ppv/(sens+ppv); NRMSE=RMSE/(max-min) ca raport (NRMSE>1 posibil); PCC=np.corrcoef  
  `easy-gait/src/easy_gait/validation.py:46-55,75-92`
- Praguri detecție: Trojaniello peak_height=0.6×P95, prosthetic scalează ×0.6, cutoff=15Hz; Maqbool prosthetic ω_HS=-60 dps, a_HS=1.2 g; validarea folosește prosthetic=True pe tot lotul  
  `easy-gait/src/easy_gait/gait_events.py:93-94,165,180 ; scripts/validate_events_all.py:89`
- 12 figuri PNG (fig01 signal_overview, fig02 stride_overlay, fig03 cadence_per_terrain, fig04 stride/walkaid, fig05 stride_cv, fig06 mae_histograms, fig07 sens_per_subject, fig08 n_events_scatter, fig09 fsm_rmse_pcc, fig10 rom_scatter, fig11 overlay, fig12 prosthesis_phases) + 5 tabele (tab01-tab05)  
  `easy-gait/notebooks/figs/ și tables/ (listing)`
- Dashboard FSM afișează ținte RMSE<5° (Bartlett 2021) și NRMSE<15%, dar real FSM RMSE 13.72°/NRMSE 86.8% (mult peste); dashboard și demo-web recalculează live, nu citesc CSV-urile de validare  
  `easy-gait/dashboard/pages/4_Simulator_FSM.py:68-69 ; dashboard/app.py:34-37`
- demo-web (Flask) replică 7 template-uri: home, signals, events, parameters, fsm, activities, prosthesis  
  `demo-web/app/templates/ (listing)`

**Discrepanțe interne observate (cod vs. docstring / între module):**
- ⚠️ S04 absent complet din events_validation.csv și fsm_validation.csv (29/30 subiecți), deși scripturile iterează S01..S30 și tab03/tab04 raportează n_trials=290 fără a semnala lipsa.
- ⚠️ Wassall: README/dashboard (app.py:36) afirmă 20 participanți, dar wassall_per_trial.csv conține doar 16 (P3, P5, P12, P18, P20 absente); P7 apare ca P7_TF și P7_TT.
- ⚠️ FSM docstring (fsm.py:6) spune 'S3 Push-Off ← dorsiflexie > +8°', dar FSMConfig.pushoff_dorsi_thr_deg=3.0 (relaxat de la 8°). Pragul real în cod e 3°.
- ⚠️ tab02_wassall_per_terrain.csv are doar 6 terenuri (flat, grass, gravel, slope, stair, uneven), excluzând CS și STEP_MULTI care apar în wassall_per_terrain.csv (8 categorii).
- ⚠️ NRMSE FSM raportat în CSV ca raport (0.868), dar dashboard (4_Simulator_FSM.py:69) afișează ×100 ca 'NRMSE [%]'.
- ⚠️ SETPOINTS FSM folosesc convenție impedance-style (toate negative în stance, fsm.py:44-48), NU unghi fiziologic observat → produc PCC NEGATIV (-0.244) vs OMC; comentariul din cod recunoaște explicit acest lucru.
- ⚠️ compute_wassall_summary.py citește din data/raw/wassall_2025/, dar fișierele .zip Wassall trăiesc și în datasets/ (root); datele dezarhivate sunt în easy-gait/data/raw/wassall_2025/.
