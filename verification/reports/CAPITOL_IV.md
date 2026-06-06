# CAPITOLUL IV — Platformă, date, algoritmi, FSM, dashboard

> Verificare detaliată (Opus 4.8) a fiecărei afirmații contra codului și rezultatelor reale. Legendă verdicte: ✅ CONFIRMAT · 🟡 PARȚIAL/imprecis · ❌ CONTRAZIS · ⚪ NEVERIFICABIL.

## 📋 Sinteză capitol

**Scor de acuratețe: 78/100**

Capitolul IV este, în ansamblu, solid și bine ancorat în implementarea reală: arhitectura modulară Python (5 module), algoritmii de detecție Trojaniello și Maqbool (ferestre temporale, scalare 60% protetic, caracter offline vs real-time), toate formulele parametrilor temporali (cadență, stride mean/SD ddof=1, CV, stance%, swing%=100-stance%, Symmetry Index Robinson), arhitectura FSM cu 5 stări (inclusiv toate cele 25 de setpoint-uri din TABEL 4.1 și interpolarea PCHIP cu waypoint 0,30), demografia Samala (30 subiecți, 25M/5F, vârstă ~53, proteze pasive majoritar SACH, 200 Hz IMU+OMC) și cele 6 pagini Streamlit + animația 2D sunt CONFIRMATE exact contra codului. Pe această fundație corectă există însă un nucleu de erori factuale ușor de verificat de un evaluator și câteva omisiuni de onestitate științifică ce trebuie reparate înainte de predare. Cinci erori sunt CRITICE: (1) frecvența IMU Samala scrisă ~100 Hz când realitatea, confirmată din trei surse independente, este 200 Hz; (2) Wassall descris ca „16 utilizatori transtibiali” când datasetul are 20 utilizatori (11 TT/8 TF/1 bilateral) iar cei 16 procesați includ și transfemorali; (3) stance mediu ~49,6%/swing 50,4% inexistent în orice rezultat al proiectului (real ~51,7% protetic / ~55,5% intact); (4) duratele și etichetele per-subiect S14/S02/S10/S08 care nu corespund tab01 (S14 real ~1,13 s, nu 0,606 s); (5) cifrele și eticheta „MEDIANE” din Fig 4.3.4 (valori reale: grass 105,3 maxim … stair 82,8 minim, afișate ca medii). Trei erori medii: viteza unghiulară atribuită greșit IMU Samala (de fapt derivată numeric), mașina Maqbool descrisă cu 4 stări (are 3 nominale + condiție refractară), și L_TIBIA=0,33 m în loc de 0,40 m. Cea mai importantă lacună metodologică transversală este absența declarării rezultatului NEGATIV al validării FSM (PCC -0,244 vs IMU +0,652), alături de statusul real al GaitRec (considerat dar neprocesat) și de pragurile protetice forțate (prosthetic=True pe tot lotul, toleranță ±150 ms). Odată corectate aceste 8 puncte și adăugate lacunele de onestitate, capitolul devine robust la susținere.

### Top probleme confirmate

- 🔴 **[CRITIC]** AF-4.20: Frecvența de eșantionare IMU Samala este declarată ~100 Hz, dar codul (SAMALA_FS=200, verificat empiric pe S01: 2888 frame/14,44 s = 200 Hz), README-ul dataset-ului brut ('frequency of 200 Hz') și RATE-ul C3D confirmă 200 Hz. Cifra ~100 Hz provine din confuzie cu Wassall (Xsens Awinda 100 Hz). Eroare direct contrazice și AF-4.8 (care spune corect 200 Hz) — contradicție internă vizibilă unui evaluator.
  - 🔧 *Fix:* Înlocuiește textul cu: «Datele IMU din datasetul Samala sunt eșantionate la o frecvență de 200 Hz, suficientă pentru captarea fidelă a evenimentelor dinamice ale mersului (heel strike și toe off).» Corectează și AF-4.22: OMC = 200 Hz (identic cu IMU), NU un interval 100-200 Hz și NU 'mai mare' decât IMU.
- 🔴 **[CRITIC]** AF-4.25: Wassall NTNU 2025 descris ca '16 utilizatori de proteză transtibială' — dublă eroare confirmată din date (nu din documentație): (1) datasetul sursă are 20 utilizatori (11 transtibial, 8 transfemoral, 1 bilateral), cei 16 fiind doar numărul efectiv procesat (lipsesc P3,P5,P12,P18,P20); (2) cei 16 procesați NU sunt toți transtibiali — includ ~7 transfemorali (P4,P9,P10,P14,P16,P19,P7_TF); numărul real de transtibiali procesați este 9.
  - 🔧 *Fix:* Rescrie: «se utilizează un dataset complementar (Wassall NTNU 2025) care, în forma sa publică, conține date de la 20 de utilizatori de proteză de membru inferior (11 transtibial, 8 transfemoral, 1 bilateral). În analiza de față au fost procesate efectiv datele a 16 participanți (atât transtibiali cât și transfemorali), restul fiind excluși din cauza datelor lipsă sau incomplete.»
- 🔴 **[CRITIC]** AF-4.53: Valori medii stance ~49,6% / swing 50,4% prezentate ca 'echilibru aproape simetric' — această valoare NU apare ca medie/agregat în niciun script, tabel sau CSV al proiectului (apare doar punctual, la nivel de probă individuală). Valorile reale: Samala prosth 51,7% / intact 55,5%; Wassall global ~55,6%, minim agregat grass 52,1%. Un stance mediu <50% este și atipic fiziologic pentru mers.
  - 🔧 *Fix:* Înlocuiește cu valorile reale: «Durata medie a fazei de sprijin (stance) este de aproximativ 51,7% pentru membrul protetic și 55,5% pentru membrul intact în lotul Samala (swing ~48,3% respectiv ~44,5%). Pe setul Wassall, sprijinul mediu pe teren variat este de ~55,6% (52,1% pe iarbă până la 59,6% pe scări coborâte).» Elimină complet cifra 49,6/50,4.
- 🔴 **[CRITIC]** AF-4.54/AF-4.55: Durata medie pas per subiect între 0,606 s (S14) și 1,130 s (S02), SD între 0,013 s (S10) și 0,152 s (S08) — valorile și etichetele NU corespund tab01 Samala. Real: S14 ~1,13 s (nu 0,606), maximul real este S29 ~1,51 s (nu S02), minimul S10 ~0,92 s. tab01 nici nu exportă SD-ul stride per subiect, deci 0,013/0,152 (S10/S08) sunt neverificabile. Recalcul independent pe toate cele 5 trial-uri confirmă: nicio interpretare rezonabilă nu salvează cifrele.
  - 🔧 *Fix:* Rescrie: «Durata medie a stride-ului per subiect (lotul Samala, tab01) variază de la ~0,93 s (S10) până la ~1,51 s (S29). Valorile pentru S14 (~1,13 s) și S02 (~1,13-1,16 s) se situează în zona mediană, nu la extreme.» Elimină cifra 0,606 s și deviațiile standard per subiect (nesusținute de tabel) sau verifică-le la sursă.
- 🔴 **[CRITIC]** Fig 4.3.4 (cadență per teren): cifrele declarate (flat 107, uneven 101, slope 101, grass 102, gravel 88, stair 83) și eticheta 'MEDIANE' sunt eronate. Medii reale (tab02): grass 105,3 (maxim), flat 95,1, uneven 93,2, slope 92,8, gravel 87,5, stair 82,8 (minim). Doar stair și gravel sunt aproximativ corecte; flat/uneven/slope/grass nu se regăsesc nicăieri. Figura este boxplot cu marker de MEDIE (showmeans=True), nu mediană.
  - 🔧 *Fix:* Corectează legenda: «cadența medie per teren (pași/min): grass 105,3 (maxim), flat 95,1, uneven 93,2, slope 92,8, gravel 87,5, stair 82,8 (minim). Valorile reprezintă medii pe trial-uri (marcate cu romb în boxplot), nu mediane.»
- 🟠 **[MEDIU]** AF-4.70: Mașina de stări Maqbool descrisă cu 4 stări (STANCE, SWING, HS_PENDING, perioadă refractară). Codul (gait_events.py:188-208) are doar 3 stări nominale; perioada refractară este o condiție temporală (i-t_last_hs)>refract, NU o stare. Docstring-ul (:156) declară explicit lanțul cu 3 stări. Eroare de structură ușor de verificat de un evaluator.
  - 🔧 *Fix:* Rescrie: «Mașina de stări Maqbool are 3 stări nominale — STANCE, SWING și HS_PENDING — parcurse ciclic (STANCE→SWING→HS_PENDING→STANCE). Perioada refractară NU este o stare separată, ci o condiție temporală: după fiecare HS, următorul toe off este permis doar după refractary_s = 0,25 s.»
- 🟠 **[MEDIU]** AF-4.14: Semnalele IMU Samala descrise ca incluzând 'viteze unghiulare pe trei axe'. Samala (Noraxon) furnizează DOAR acceleratii pe 3 axe, orientare cuaternion și unghiuri de segment (deg); omega (viteza unghiulară a tibiei) este DERIVATĂ numeric (np.gradient) din unghiul de pitch, apoi filtrată. Giroscopul direct (Gyr_X/Y/Z) există doar la Wassall.
  - 🔧 *Fix:* Rescrie: «Semnalele IMU includ accelerații pe trei axe și orientarea de segment (cuaternion). Spre deosebire de Wassall, sistemul Noraxon din Samala nu furnizează viteze unghiulare măsurate direct (giroscop); viteza unghiulară a tibiei este obținută prin diferențiere numerică a unghiului de segment, urmată de filtrare Butterworth (cutoff 15 Hz).»
- 🟠 **[MEDIU]** AF-4.94: L_TIBIA declarat 0,33 m în descrierea animației proteză, dar codul real (prosthesis_viz.py:36) folosește 0,40 m. Chiar și PDF-ul de documentație (l.830) scrie 0,40 m. În plus, referința 'bench-test MTS-type (Hansen/Childress/Knox 2004)' apare doar în generatorul PDF, nu în cod — modelul real este geometric ad-hoc (tibie rigidă oblică +7°), nu un roll-over shape din literatură.
  - 🔧 *Fix:* Corectează: «Modelul vizual folosește o tibie (pilon) rigidă cu lungime fixă L_TIBIA = 0,40 m și înclinare oblică constantă de +7° (PYLON_TILT_DEG = 7,0). Talpa pivotează după unghiul exact din date (FSM sau IMU), fără scalare.» Retrage referința Hansen/Childress/Knox 2004 sau marcheaz-o ca analogie conceptuală, nu sursă a implementării.
- 🟠 **[MEDIU]** AF-4.2: Modulul de preprocesare enumeră trei pași inexistenți în cod: 'corectarea offsetului', 'eliminarea derivațiilor (drift)' și 'sincronizarea temporală a canalelor IMU'. Codul face doar filtrare Butterworth low-pass zero-phase (15 Hz, ordin 4) + magnitudine accelerație + derivare numerică pentru omega (opusul 'eliminării derivațiilor'). Risc de a fi contestat la susținere ca funcționalitate pretinsă inexistentă.
  - 🔧 *Fix:* Reformulează conform implementării reale: import CSV brute, filtru Butterworth low-pass ordin 4 fază nulă (filtfilt, 15 Hz), magnitudine accelerație ca normă euclidiană, derivare numerică centrată a omega pentru Samala, calibrare unghi gleznă pe index de referință, iar sincronizarea OMC↔IMU prin cross-correlation doar la validare (nu între canalele IMU).
- 🟠 **[MEDIU]** AF-4.5 / AF-4.90 / cap. 4.11 FSM: descrierea FSM 'validat contra unghiurilor gleznei' omite că validarea a EȘUAT (PCC mediu -0,244, RMSE 13,72°), unghiul derivat direct din IMU fiind net superior (PCC +0,652, RMSE 8,75°). Suplimentar, AF-4.90 conține o referință internă eronată la 'Capitolul IX' (lucrarea are doar capitolele I-V). Omisiunea rezultatului negativ este o problemă de onestitate științifică.
  - 🔧 *Fix:* Declară explicit limitarea (vezi recomandările de scris) și corectează 'Capitolul IX' → 'Capitolul V'. Clarifică faptul că setpoint-urile FSM sunt echilibre virtuale de impedanță (toate în plantarflexie), nu unghiuri fiziologice, deci comparația directă RMSE/PCC cu unghiul articular OMC este conceptual nepotrivită.
- 🟠 **[MEDIU]** GaitRec (AF-4.33..4.41) este prezentat ca dataset utilizat, dar ZERO cod/rezultate îl procesează — apare doar în documentație/text. Induce în eroare cititorul. La fel, subiectul Samala S04 lipsește din validare (29/30 procesați, deși se raportează n_trials=290), nemenționat.
  - 🔧 *Fix:* Declară GaitRec ca 'considerat dar neprocesat' (vezi recomandări). Adaugă mențiunea excluderii S04: rezultatele de validare provin de la 29 din cei 30 de participanți Samala (290 trial-uri totale).
- 🟠 **[MEDIU]** AF-4.63/64/65, AF-4.69, AF-4.70: pragurile algoritmice sunt prezentate ambiguu/imprecis. Textul citează amplitudinea fiziologică (~-100 °/s HS) ca prag, iar pragul nominal real Trojaniello hs_thr=-20 °/s nu apare deloc. În validare se forțează prosthetic=True pe tot lotul (praguri relaxate -12/-6 °/s Trojaniello, -60 °/s și 1,2g Maqbool), deci valorile 'standard' citate (-20/-10, 1,5g) nu sunt cele folosite la rezultate. Maqbool descris pentru 'proteze active' deși tot lotul Samala e pasiv.
  - 🔧 *Fix:* Distinge clar amplitudinea fiziologică de pragul algoritmic; menționează pragul nominal Trojaniello hs_thr=-20 °/s și modul protetic forțat în validare. Reformulează 'proteze active' → 'detector real-time orientat către controlul protezelor active, aplicat aici pe date de la proteze transtibiale PASIVE'.
- 🟢 **[MINOR]** AF-4.99 / AF-4.97 / AF-4.98 / AF-4.100 (dashboard): mai multe afirmații imprecise — pagina 3 NU afișează Symmetry Index Robinson (doar medii pe rol); pagina 1 NU are 'alegere coloane' (slider cutoff); pagina 2 marchează HS/TO peste viteza unghiulară (omega), nu peste 'shank pitch'; pagina 4 NU colorează curba per-stare și are 3 sub-grafice, nu 'plot dublu'.
  - 🔧 *Fix:* Aplică reformulările precise per pagină: pag.1 'frecvență de tăiere a filtrului' (nu coloane); pag.2 'suprapuse peste viteza unghiulară a gambei (omega)'; pag.3 'sumar comparativ protetic vs intact prin medii pe rol; SI Robinson este definit în parameters.py dar nu afișat aici'; pag.4 'trei sub-grafice sincronizate'.
- 🟢 **[MINOR]** AF-4.47 / AF-4.72: 'calibrare 0° la primul HS' prezentată ca implicită, dar default-ul funcției compute_ankle_angle este reference_idx=100 (0,5 s static); calibrarea pe primul HS apare doar în pipeline-ul FSM. Coexistă două convenții de calibrare în cod — sursă de inconsistență între figuri și metrici.
  - 🔧 *Fix:* Precizează că default-ul este reference_idx=100 (0,5 s static la 200 Hz), iar calibrarea pe primul HS se aplică doar în pipeline-ul de validare FSM (validate_fsm_all.py:80-81); recomandă uniformizarea.
- 🟢 **[MINOR]** AF-4.73: valoarea specifică '+25°' pentru valorile non-fiziologice în swing ale coloanelor Noraxon NU apare în cod (cod spune doar generic 'valori non-fiziologice în swing'). Cifra este inventată/neverificabilă. Valorile HS≈0/push-off≈-18/mid-swing≈+10 sunt afirmații de docstring, nu rezultate de validare.
  - 🔧 *Fix:* Elimină '+25°' sau înlocuiește cu formularea generică 'valori non-fiziologice în swing'. Marchează HS≈0/push-off≈-18°/mid-swing≈+10° ca proveniente din convenția docstring, confirmate calitativ de suprapunerea cu OMC (fig11).

### ✍️ Recomandări de scris (ce să adaugi)

- LIMITAREA-CHEIE A FSM (prioritate maximă, onestitate științifică) — adaugă la sub-secțiunea de control/rezultate FSM: «Trebuie subliniat că traiectoria comandată de FSM reprezintă echilibre virtuale de impedanță (theta_eq), nu o estimare a unghiului articular fiziologic. În consecință, comparația directă FSM vs. referința optică OMC produce metrici slabe: RMSE 13,72° (±4,93), NRMSE 0,868 și o corelație Pearson medie NEGATIVĂ de -0,244 (mediana -0,224), iar amplitudinea comandată (ROM 14,6°) este sub cea observată OMC (22,9°). Prin contrast, unghiul gleznei estimat direct din IMU (compute_ankle_angle) urmărește mult mai fidel referința OMC: RMSE 8,75°, NRMSE 0,529 și PCC mediu pozitiv +0,652. Aceasta confirmă că obiectivul FSM nu este reproducerea cinematicii observate, ci comanda de impedanță — comparația RMSE/PCC față de unghiul articular OMC fiind conceptual nepotrivită pentru evaluarea controlului.»
- STATUSUL GaitRec (prioritate ridicată) — adaugă la sub-secțiunea seturi de date: «Datasetul GaitRec (peste 75.000 de trial-uri bilaterale bazate pe forțe de reacțiune la sol, achiziționate cu platforme de forță la ~1000 Hz) a fost identificat ca potențial set complementar pentru validări statistice la scară largă, comparații ale parametrilor temporali și studii de simetrie. În implementarea curentă GaitRec NU este procesat: rezultatele lucrării se bazează exclusiv pe seturile Samala 2024 și Wassall 2025, integrarea GaitRec rămânând o direcție de dezvoltare ulterioară.»
- PRAGURI PROTETICE FORȚATE ÎN VALIDARE (prioritate ridicată) — adaugă la sub-secțiunea de detecție evenimente: «În studiul de validare ambii detectori au fost rulați cu modul protetic activat (prosthetic=True) pe întregul lot Samala, ca alegere conservatoare pentru un set mixt de proteze. În consecință, pragurile efective au fost relaxate: pentru Trojaniello hs_thr=-12°/s și to_thr=-6°/s (60% din valorile nominale -20/-10°/s), iar pentru Maqbool omega_HS=-60°/s și a_HS=1,2g (în loc de -100°/s și 1,5g). Această relaxare crește sensibilitatea pe semnalele atenuate ale protezelor pasive, dar contribuie la rata mare de fals-pozitive observată (PPV ~0,28-0,29).»
- TOLERANȚA DE POTRIVIRE ±150 ms (prioritate ridicată) — adaugă la pipeline-ul de validare: «Potrivirea dintre evenimentele detectate din IMU și cele de referință OMC s-a făcut cu o toleranță de ±150 ms atât pentru heel-strike, cât și pentru toe-off (prag raportat de Pacini Panebianco et al., 2018), mai permisivă decât pragul clinic strict de 25 ms (IC) / 50 ms (TO) folosit ca obiectiv de proiectare. Această alegere reflectă caracterul eterogen al lotului (proteze pasive cu impact atenuat) și a fost aplicată uniform ambilor algoritmi.»
- PERFORMANȚA REALĂ A DETECȚIEI FAȚĂ DE PRAGURILE DE ACCEPTABILITATE (prioritate ridicată) — adaugă la rezultatele detecției: «Detecția folosește două metode deterministe complementare: Trojaniello (offline) și Maqbool R-GEDS (real-time). Validarea pe 290 de probe Samala (toleranță ±150 ms) arată o performanță limitată pe purtătorii de proteză pasivă: la HS, Maqbool obține MAE 60,2 ms și sensibilitate 0,633, iar Trojaniello MAE 79,8 ms și sensibilitate 0,584; la TO, Trojaniello (MAE 60,7 ms) îl depășește pe Maqbool (76,9 ms). Precizia (PPV) este redusă la ambii (~0,28-0,29). Aceste valori sunt sub pragurile de acceptabilitate clinică (MAE≤25 ms, sens≥99%), reflectând dificultatea detecției pe semnale de gambă protetică cu amplitudine redusă.»
- DERIVAREA NUMERICĂ A OMEGA PENTRU SAMALA (prioritate medie) — adaugă la sub-secțiunea seturi de date / preprocesare: «Spre deosebire de datasetul Wassall (care conține giroscop direct, Gyr_X/Y/Z în rad/s), sistemul Noraxon din Samala furnizează pentru fiecare segment orientarea (cuaternion), accelerațiile pe trei axe și unghiurile de segment (course/pitch/roll, în grade), dar NU și viteza unghiulară măsurată direct. În consecință, viteza unghiulară a tibiei (deg/s), necesară algoritmilor de detecție, este obținută prin diferențiere numerică centrată (np.gradient) a unghiului de pitch, urmată de filtrare Butterworth low-pass (cutoff 15 Hz). Pentru Wassall, viteza unghiulară se preia direct din giroscop (Gyr_Y) și se convertește din rad/s în deg/s.»
- ALINIEREA OMC↔IMU PRIN CROSS-CORRELATION (prioritate medie) — adaugă: «Deoarece achiziția simultană nu garantează alinierea la nivel de eșantion între fluxurile IMU și OMC, alinierea temporală se realizează algoritmic prin corelație încrucișată (cross-correlation) aplicată pe unghiul gleznei normalizat; offset-ul rezultat este stocat per trial și folosit la suprapunerea evenimentelor.»
- CEI 4 SENZORI WASSALL (prioritate medie) — adaugă: «Pentru fiecare probă, datasetul Wassall conține înregistrări de la patru senzori IMU Xsens Awinda plasați pe tibia protetică (PS), coapsa protetică (TH), trunchi (TR, la nivel L4) și tibia contralaterală (OS). Analiza folosește cu precădere semnalul tibiei protetice (PS, giroscop axă Y) pentru detecția evenimentelor de mers.»
- ÎNLOCUIREA COLOANELOR NORAXON 'Ankle Dorsiflexion' (prioritate medie) — adaugă la 4.8: «Unghiul gleznei nu a fost preluat direct din coloanele 'Ankle Dorsiflexion LT/RT' furnizate de Noraxon, deoarece acestea s-au dovedit inconsistente (semn opus și valori non-fiziologice în faza de balans). În locul lor, unghiul a fost recalculat intern ca diferență a orientărilor segmentelor tibie-picior, urmând convenția dorsiflexie pozitivă / plantarflexie negativă (Perry & Burnfield).»
- VALIDAREA EMPIRICĂ A UNGHIULUI IMU (prioritate medie, întărește 4.8) — adaugă: «Validarea pe cele 290 de probe Samala (tab04) confirmă calitatea unghiului derivat din IMU prin compute_ankle_angle: corelație Pearson medie +0,652 (median 0,65) și RMSE 8,75° față de referința optică OMC — net superioară traiectoriei comandate de FSM (PCC -0,244, RMSE 13,72°). Acest rezultat susține empiric convenția dorsi+/plantar- și calibrarea adoptate.»
- EXCLUDEREA SUBIECTULUI S04 (prioritate medie) — adaugă: «Din motive de calitate a datelor brute, subiectul S04 a fost exclus din etapa de validare a evenimentelor și a traiectoriei; rezultatele raportate provin așadar de la 29 din cei 30 de participanți Samala (290 trial-uri totale).»
- DETALII FSM SUPLIMENTARE (prioritate scăzută-medie) — adaugă: (a) foot-flat ca număr fix de eșantioane: «Pragul de foot-flat este definit ca număr fix de eșantioane consecutive (foot_flat_min_samples = 10) sub care |omega_shank| < 30°/s; la 200 Hz (Samala) = 50 ms, la 100 Hz (Wassall) = 100 ms.» (b) setpoint-uri monoton descrescătoare: «Setpoint-urile pentru level walking formează o curbă monoton descrescătoare în sprijin (de la -8° în loading la -25° în push-off), toate în plantarflexie — consecință a interpretării impedance-style (Sup 2008): valorile sunt echilibre virtuale theta_eq, nu unghiuri cinematice observate.»
- DETALII PREPROCESARE/DETECȚIE SUPLIMENTARE (prioritate scăzută-medie) — adaugă: (a) dubla filtrare omega Samala (derivată+filtrată 15 Hz în gyro_pitch_dps, apoi re-filtrată 15 Hz în detect_events_*); (b) magnitudinea accelerației folosită NEFILTRATĂ în Maqbool, deliberat, pentru a conserva spike-ul de impact; (c) fallback HS Maqbool: dacă accelerația nu confirmă HS în ~600 ms de la TO, HS este acceptat pe baza criteriului de viteză unghiulară.
- FORMULE CONCRETE PARAMETRI (prioritate scăzută, întărește 4.4/4.10) — adaugă: «Cadența totală = 2 × (60 × n_cicluri / durată_totală) [pași/min]. Variabilitatea pasului = abaterea standard de eșantion (ddof=1) și CV = SD/medie. Indicele de simetrie (Robinson 1987): SI = 2 × (protetic − intact) / (protetic + intact) × 100, unde 0 = simetrie perfectă. Filtrul de 6 Hz pe unghiul gleznei urmează recomandarea Winter (1991); clippingul ±35° respinge artefactele peste ROM-ul fiziologic (Perry & Burnfield).»
- ELEMENTE DASHBOARD/VIZUALIZARE (prioritate scăzută) — adaugă: (a) tibie rigidă: «tibia este un segment rigid de lungime fixă (L_TIBIA = 0,40 m) și înclinare constantă (+7°); genunchiul și glezna se deplasează doar pe verticală, doar talpa pivotează după unghiul comandat sau măsurat.» (b) două surse de unghi: «Simulatorul de proteză permite alegerea sursei unghiului: traiectoria comandată FSM sau unghiul real estimat din IMU, permițând comparația vizuală directă, relevantă dat fiind PCC negativ al FSM.» (c) metrici live + ținte: «Dashboard-ul recalculează metricile în timp real din datele brute; pagina 4 afișează țintele din literatură (RMSE<5° Bartlett 2021, NRMSE<15%, PCC>0,90), care NU sunt atinse de FSM-ul real (RMSE ~13,7°, PCC -0,244), fapt vizibil în interfață.»

---

## 🔍 Verificare detaliată pe sub-secțiuni

### WU-IV-01a — 4.1 Platforma software — cele 5 module functionale

*Sub-secțiunea 4.1 (cele 5 module) este în mare parte solidă: AF-4.1, AF-4.3, AF-4.4 și AF-4.6 sunt CONFIRMATE integral pe baza codului - arhitectura modulară Python, detecția HS/TO cu validare OMC, extragerea parametrilor (cadență, stance/swing, SD, simetrie) și dashboard-ul Streamlit cu toate vizualizările declarate există efectiv. Două afirmații necesită corectură. AF-4.2 este PARȚIAL: enumeră trei pași de preprocesare care NU sunt implementați (corectarea offsetului, eliminarea derivațiilor/drift, sincronizarea canalelor IMU) - codul face doar filtrare Butterworth + magnitudine + derivare numerică; aceasta trebuie reformulată pentru a nu pretinde funcționalitate inexistentă (severitate medie - risc de a fi contestat la susținere). AF-4.5 este PARȚIAL: descrierea FSM e corectă structural, dar afirmația 'validat contra unghiurilor gleznei' omite că validarea a EȘUAT (PCC negativ -0.244); trebuie adăugată explicit limitarea. Urgent de reparat: (1) rescrierea AF-4.2 conform implementării reale; (2) declararea onestă a rezultatului negativ al FSM la AF-4.5. Restul afirmațiilor pot rămâne neschimbate.*

#### Verdicte pe afirmații

**✅ AF-4.1 — CONFIRMAT**  
Platforma modulara Python cu module: preprocesare IMU, detectie faze, extragere parametri, control FSM gleznă, vizualizare (dashboard).  
📎 *Dovadă:* `easy-gait/src/easy_gait/: preprocessing.py, gait_events.py, parameters.py, fsm.py, ankle_controller.py + easy-gait/dashboard/app.py & pages/1..6; toate fișierele .py (limbaj Python).`  
💬 Toate cele 5 module declarate există ca module Python separate: preprocessing.py (preprocesare), gait_events.py+segmentation.py (detectie faze), parameters.py (extragere parametri), fsm.py+ankle_controller.py (control FSM), dashboard/ Streamlit (vizualizare). Arhitectura este efectiv modulară și implementată în Python.

**🟡 AF-4.2 — PARTIAL 🟠**  
Modul preprocesare: importa CSV brute (accel+viteza unghiulara), filtrare zgomot, corectarea offsetului, eliminarea derivatiilor (drift), sincronizare temporala canale.  
📎 *Dovadă:* `preprocessing.py:16-46 (butter_lowpass filtfilt), :63-65 (np.gradient), :68-76 (gyro_pitch_dps), :79-81 (normalize_to_g); io_utils.py:82 (df=pd.read_csv(p)), :340-343 (accel_magnitude norm); CAUTARE 'offset|drift|detrend|sync' în src/ → NICIUN rezultat de corectie offset/drift/sincronizare canale.`  
💬 Confirmat: importul CSV brute (io_utils.load_samala_imu / load_wassall_trial) și filtrarea de zgomot (butter_lowpass low-pass zero-phase 15 Hz, ordin 4). PARȚIAL fals restul: (1) 'corectarea offsetului' NU există ca pas dedicat - singura centrare e reference_idx în compute_ankle_angle (io_utils.py:386-389), aplicată doar pe unghiul gleznei, nu pe semnalele IMU brute. (2) 'eliminarea derivatiilor/drift' NU este implementată - nu există detrend/high-pass/drift removal nicăieri (grep gol); de fapt codul FACE derivare numerică (np.gradient) pentru a OBȚINE omega din unghi, opusul 'eliminării derivațiilor'. (3) 'sincronizare temporala canale' NU există pentru canalele IMU - read_csv încarcă canale deja co-eșantionate; singura sincronizare e align_omc_to_imu (omc_events.py:179) care aliniază OMC la IMU pentru validare, nu canalele IMU între ele. Notă: textul Samala dă unghiuri shank, nu giroscop direct - omega se derivă (preprocessing.py:68-76), aspect care contrazice 'importa viteza unghiulara' pentru Samala.

**✅ AF-4.3 — CONFIRMAT**  
Modul detectie faze: HS/TO din IMU, delimiteaza stance/swing, metode deterministe (reguli/praguri pe accel+viteza unghiulara), validare prin comparatie cu motion capture.  
📎 *Dovadă:* `gait_events.py:52-134 (Trojaniello, praguri ω hs_thr=-20*scale, peak 0.6×P95), :141-220 (Maqbool FSM praguri ω_swing=50, ω_HS=-100/-60, a_HS=1.5/1.2g); segmentation.py:36-58 (stance/swing/stride); omc_events.py:120-123 (Zeni 2008 OMC ground truth); scripts/validate_events_all.py + tab03_events_validation_summary.csv.`  
💬 Toate sub-afirmatiile sunt corecte: detectia HS/TO din IMU (Trojaniello și Maqbool), delimitarea stance=[HS,TO]/swing=[TO,HS] (segmentation.GaitCycle), metode deterministe bazate pe reguli și praguri pe viteza unghiulară (ambele) și accelerație (Maqbool a_HS). Validarea prin motion capture există (Zeni 2008 pe C3D OMC ca ground truth, rezultate în tab03). Singura nuanță: Trojaniello folosește DOAR viteza unghiulară (nu accelerație), accelerația intervine doar la Maqbool - dar 'praguri pe accel ȘI viteza unghiulara' rămâne adevărat la nivel de modul.

**✅ AF-4.4 — CONFIRMAT**  
Modul extragere parametri: cadenta (pasi/min), durata stance/swing, durata pasului si variabilitatea (SD), indicatori de simetrie.  
📎 *Dovadă:* `parameters.py:62-64 (cadence_total=2×60×n/total_s), :66-67 (stride mean, std ddof=1), :68 (CV=std/mean), :85-94 (symmetry_index Robinson); segmentation.py:53-58 (stance_pct, swing_pct).`  
💬 Toate componentele declarate sunt implementate: cadența în pași/min (cadence_steps_per_min, formula 2×cadence_per_side), durata stance%/swing% (GaitCycle.stance_pct/swing_pct), durata pasului (stride_s_mean) și variabilitatea SD (stride_s_std cu ddof=1, plus CV). Indicatorul de simetrie există (symmetry_index, formula Robinson 1987 SI=2(P-I)/(P+I)×100). Afirmația este completă și exactă.

**🟡 AF-4.5 — PARTIAL 🟠**  
Modul FSM: masina de stari (loading, mid-stance, push-off, swing), tranzitii declansate de HS/TO, setpoint per stare interpolat in traiectorie continua, validat contra unghiurilor gleznei din dataset.  
📎 *Dovadă:* `fsm.py:28-33 (5 stări S1..S5), :173-177 (HS→S1, TO→S4), :52-93 (SETPOINTS per stare); ankle_controller.py:93 (PchipInterpolator → traiectorie continuă); validate_fsm_all.py + tab04 (PCC mediu -0.244, RMSE 13.72°); fsm.py:36-48 (setpoints = echilibre de impedanță, NU unghiuri fiziologice).`  
💬 Confirmat structural: FSM cu 5 stări (Loading, Mid-Stance, Push-Off, Early-Swing, Late-Swing), tranziții pe HS (forțează S1, fsm.py:173-174) și TO (forțează S4, fsm.py:176-177), setpoint per stare interpolat în traiectorie continuă prin PCHIP (ankle_controller.py:93), și validare contra unghiului gleznei din dataset (validate_fsm_all.py). PARȚIAL pentru că afirmația sugerează implicit o validare reușită: rezultatul real este NEGATIV - traiectoria FSM corelează NEGATIV cu OMC (PCC mediu -0.244, RMSE 13.72°), inferioară unghiului IMU direct (PCC +0.652). Setpoint-urile sunt echilibre de impedanță (toate plantarflexie -8..-25° la 'level'), NU unghiuri fiziologice observate, deci comparația directă cu unghiul articular e conceptual nepotrivită. Afirmația în sine nu e falsă ca descriere de implementare, dar omite că validarea a eșuat - de aici PARȚIAL, cu lacună de discutat la rezultate.

**✅ AF-4.6 — CONFIRMAT**  
Modul vizualizare/dashboard: grafice semnale brute/filtrate, marcare HS/TO, stance/swing, comparatii unghi referinta vs traiectorie control, tabele parametri per subiect si trial.  
📎 *Dovadă:* `dashboard/pages/1_Explorare_semnale.py:64-101 (brut+filtrat, accel, unghi gleznă); 2_Detectie_evenimente.py:59-104 (marcare HS/TO, timeline stance/balans, tabel cicluri); 4_Simulator_FSM.py:90-93 (unghi real vs comandat), :73-110 (faze, tabel setpoints); 3_Parametri_temporali.py:47-127 (tabele parametri per subiect/trial/lot).`  
💬 Toate cele 5 funcții de vizualizare declarate există: (1) grafice brut/filtrat (pag.1, butter_lowpass cu slider cutoff); (2) marcarea HS/TO (pag.2, markers roșii/albastre pe omega) și stance/swing (pag.2 timeline 'sprijin/balans'); (3) comparație unghi referință (verde 'unghi real măsurat') vs traiectorie control (portocaliu 'unghi comandat') la pag.4:90-93; (4) tabele parametri per subiect și per trial (pag.3 process_trial pe Walking1..5, mod 'Un subiect'/'Toți subiecții'). Dashboard implementat în Streamlit, 6 pagini. Confirmat integral.

#### ✏️ Corecturi de redactare propuse

**AF-4.2**  
- ❌ Original: *Modul preprocesare IMU: importa CSV brute (acceleratie + viteza unghiulara), filtrare zgomot, corectarea offsetului, eliminarea derivatiilor, sincronizare temporala canale.*
- ✅ Corectat: **Modul preprocesare IMU: importă fișierele CSV brute (accelerații pe trei axe și unghiuri/viteză unghiulară a gambei), aplică filtrare de zgomot prin filtru Butterworth low-pass de ordin 4 cu fază nulă (frecvență de tăiere implicită 15 Hz), calculează magnitudinea accelerației ca normă euclidiană și, pentru datele Samala care furnizează doar unghiuri, derivă numeric viteza unghiulară a gambei. Calibrarea unghiului de gleznă la 0° se realizează prin centrare pe un index de referință. Sincronizarea temporală între referința optică (OMC) și IMU, necesară la validare, se obține prin corelație încrucișată pe unghiul gleznei.**

**AF-4.5**  
- ❌ Original: *Modul control FSM: masina de stari finite (loading response, mid-stance, push-off, swing), tranzitii declansate de HS si TO, setpoint per stare interpolat in traiectorie continua, validat contra unghiurilor gleznei din dataset.*
- ✅ Corectat: **Modul control FSM: mașină de stări finite cu cinci stări (Loading Response, Mid-Stance, Push-Off, Early Swing, Late Swing), cu tranziții declanșate de evenimentele HS și TO; fiecare stare are un setpoint de echilibru (impedanță) interpolat printr-o curbă continuă (PCHIP) într-o traiectorie a unghiului comandat. Modulul a fost validat contra unghiului real al gleznei din dataset; validarea a evidențiat o limitare conceptuală: deoarece setpoint-urile reprezintă echilibre de impedanță (toate în plantarflexie), nu unghiuri fiziologice observate, traiectoria comandată corelează negativ cu referința (PCC mediu -0,244; RMSE 13,72°), în timp ce unghiul derivat direct din IMU se apropie net mai bine de referință (PCC +0,652; RMSE 8,75°).**

#### 📌 Lacune — ce ar trebui adăugat

- **[ridicata]** Textul afirmă în AF-4.2 'corectarea offsetului' și 'eliminarea derivațiilor (drift)' și 'sincronizare temporală canale', dar codul de preprocesare NU implementează niciun pas de offset-correction, drift-removal/detrend sau sincronizare de canale. Singura preprocesare reală este filtrul Butterworth low-pass zero-phase și calculul magnitudinii accelerației. În plus, pentru Samala omega NU este importată direct, ci derivată numeric din unghi.
  - 📎 `preprocessing.py:16-81 (butter_lowpass, gradient, normalize_to_g), io_utils.py:340-343 (accel_magnitude), :386-389 (centrare reference_idx), omc_events.py:179-210 (align_omc_to_imu cross-corr); grep 'offset|drift|detrend|sync' în src/ → 0 rezultate de corectie.`
  - ✍️ *Text propus:* Modulul de preprocesare importă fișierele CSV brute (accelerații pe trei axe și, după caz, viteza unghiulară a gambei) și aplică un filtru Butterworth low-pass de ordin 4 cu fază nulă (filtfilt, frecvență de tăiere implicită 15 Hz) pentru atenuarea zgomotului de înaltă frecvență. Magnitudinea accelerației se calculează ca normă euclidiană a celor trei axe. Pentru setul Samala, care furnizează doar unghiuri ale gambei (nu giroscop), viteza unghiulară se obține prin derivare numerică centrată (gradient) urmată de filtrare. Calibrarea unghiului de gleznă la 0° se face prin centrare pe un index de referință (segment static sau primul contact). Sincronizarea temporală între referința optică (OMC) și IMU, atunci când este necesară pentru validare, se realizează prin corelație încrucișată pe semnalul unghiului de gleznă.
- **[ridicata]** AF-4.5 prezintă modulul FSM ca 'validat contra unghiurilor gleznei' fără a menționa rezultatul real: validarea este NEGATIVĂ (PCC mediu -0.244). Aceasta este o limitare esențială ce trebuie declarată explicit pentru onestitate științifică.
  - 📎 `tab04_fsm_validation_summary.csv (fsm: PCC -0.244, RMSE 13.72; imu: PCC 0.652, RMSE 8.75); fsm.py:36-48 (comentariu: setpoints = echilibre de impedanță, nu unghiuri fiziologice).`
  - ✍️ *Text propus:* Modulul de control FSM a fost validat prin comparație cu unghiul real al gleznei reconstruit din IMU și cu referința OMC. Validarea a evidențiat o limitare importantă: traiectoria comandată de FSM corelează negativ cu unghiul fiziologic de referință (PCC mediu -0,244; RMSE 13,72°±4,93°), în timp ce unghiul derivat direct din IMU se apropie mult mai bine de referință (PCC +0,652; RMSE 8,75°). Explicația este de natură conceptuală: setpoint-urile FSM sunt echilibre virtuale de impedanță (toate în plantarflexie, de la -8° la -25° pentru mers pe plat, conform Sup 2008), nu unghiuri articulare observate fiziologic; prin urmare, compararea directă a unei comenzi de impedanță cu un unghi articular măsurat este intrinsec nepotrivită și produce metrice slabe.
- **[medie]** AF-4.3 descrie metodele de detecție ca 'deterministe' dar nu menționează că ambele algoritmi au sensibilitate și F1 slabe pe lotul de proteze (HS sens 0.58-0.63, F1 0.38-0.40, MAE 60-80 ms), mult sub pragurile de acceptabilitate din docstring (sens≥99%, MAE≤25ms). Aceasta e o limitare reală a modulului.
  - 📎 `tab03_events_validation_summary.csv (Trojaniello HS MAE 79.8/sens 0.584/F1 0.377; Maqbool HS MAE 60.2/sens 0.633); validation.py:8-11 (praguri docstring); validate_events_all.py:35-36 (TOL 150 ms).`
  - ✍️ *Text propus:* Detecția evenimentelor folosește două metode deterministe complementare: Trojaniello (offline, pe vârfuri mid-swing cu prag adaptiv) și Maqbool R-GEDS (mașină de stări în timp real). Validarea pe 290 de probe Samala, cu toleranță de potrivire de ±150 ms, arată o performanță limitată pe purtătorii de proteză pasivă: la HS, Maqbool obține MAE 60,2 ms și sensibilitate 0,633, iar Trojaniello MAE 79,8 ms și sensibilitate 0,584; la TO, Trojaniello (MAE 60,7 ms) îl depășește pe Maqbool (76,9 ms). Precizia (PPV) este redusă la ambii (~0,28-0,29), generând multe false pozitive. Aceste valori sunt sub pragurile de acceptabilitate clinică (MAE≤25 ms, sens≥99%), reflectând dificultatea detecției pe semnale de gambă protetică cu amplitudine redusă.
- **[scazuta]** AF-4.4 nu menționează formula concretă a cadenței și a indicatorului de simetrie, deși acestea sunt parametrizate exact în cod și relevante metodologic.
  - 📎 `parameters.py:62-64 (cadence_total=2*cadence_per_side), :66-68 (std ddof=1, CV), :85-94 (symmetry_index Robinson).`
  - ✍️ *Text propus:* Cadența totală se calculează ca dublul cadenței pe un picior: cadență = 2 × (60 × n_cicluri / durată_totală), exprimată în pași/min. Variabilitatea pasului este cuantificată prin abaterea standard de eșantion (ddof=1) și coeficientul de variație CV = SD/medie. Indicatorul de simetrie urmează formula Robinson (1987): SI = 2 × (protetic − intact) / (protetic + intact) × 100, unde 0 reprezintă simetrie perfectă.

---

### WU-IV-01b — 4.2 Seturile de date (Samala 2024, Wassall NTNU 2025, GaitRec)

*Sub-sectiunea 4.2 are un nucleu corect (Samala: 30 subiecti, 25M/5F, varsta ~53, proteze pasive SACH, 200 Hz IMU si OMC — toate confirmate empiric), dar contine TREI erori factuale critice care trebuie reparate inainte de predare: (1) AF-4.20 afirma IMU Samala la ~100 Hz, dar codul, README-ul si datele brute confirma 200 Hz (provine probabil din confuzie cu Wassall); (2) AF-4.25 afirma '16 utilizatori transtibiali' Wassall, dar datasetul sursa are 20 utilizatori (11 transtibial/8 transfemoral/1 bilateral), iar cei 16 efectiv procesati includ si transfemorali — dubla eroare; (3) AF-4.14 atribuie Samala 'viteze unghiulare pe trei axe' desi Samala furnizeaza doar unghiuri, omega fiind derivat numeric (Wassall e cel cu giroscop real). Contradictia interna 200 Hz (AF-4.8) vs ~100 Hz (AF-4.20/4.22) se rezolva clar in favoarea 200 Hz. GaitRec (AF-4.33..4.41) este complet neutilizat in cod/rezultate — apare doar in documentatie/text; trebuie declarat explicit ca dataset considerat dar neprocesat, altfel induce in eroare. Recomand corectarea celor 6 afirmatii din lista de redactare si adaugarea lacunelor (excludere S04, derivarea omega, aliniere cross-correlation, 4 senzori Wassall, status GaitRec)."*

#### Verdicte pe afirmații

**✅ AF-4.7 — CONFIRMAT**  
Lucrarea utilizeaza exclusiv baze de date publice.  
📎 *Dovadă:* `easy-gait/src/easy_gait/io_utils.py:4-5 (Samala 2024, Sci Data 11:922, DOI 10.1038/s41597-024-03677-3; Wassall NTNU 2025, DOI 10.18710/U8RGDL); datasets/dataverse_README.txt:8 (DOI public Wassall). Ambele seturi de date au DOI public.`  
💬 Atat Samala 2024 cat si Wassall 2025 sunt publicate cu DOI public. GaitRec este de asemenea un dataset public (desi nefolosit efectiv in cod). Nu exista date proprietare/private in proiect.

**✅ AF-4.8 — CONFIRMAT**  
Samala: 30 participanti transtibiali unilaterali (25M/5F), varsta medie 53, proteze pasive majoritar SACH, mers viteza confortabila pe traseu drept, IMU Noraxon 200 Hz, OMC 200 Hz ground truth.  
📎 *Dovadă:* `samala_metadata.py:43-74 → 30 subiecti, gen Counter({M:25, F:5}), varsta medie 53.3 ani (min 24, max 75), foot_type Counter({SACH:25, Dynamic:2, sPace:2, Single axis:1}), toate 'passive'; io_utils.py:20 SAMALA_FS=200; C3D POINT RATE=200.0 (verificat empiric pe S01_Walking1.c3d); data/raw/samala_2024/README_IMU.txt 'frequency of 200 Hz'.`  
💬 Toate cifrele se confirma: 30 participanti, 25M/5F, varsta medie 53 ani, proteze pasive majoritar SACH (25/30), IMU Noraxon @200 Hz, OMC @200 Hz. Observatie minora: dosarul de echipa mentiona 24 SACH, dar metadatele reale arata 25 SACH (S30 e Dynamic, S20 Single axis, S13/S23 sPace) - textul spune doar 'majoritatea SACH', deci ramane corect.

**✅ AF-4.9 — CONFIRMAT**  
Achizitia Samala a fost realizata simultan (IMU + OMC).  
📎 *Dovadă:* `io_utils.py:4 ('IMU Noraxon 200 Hz + OMC referinta'); omc_events.py:179-210 align_omc_to_imu (cross-correlation pe unghiul gleznei presupune achizitie simultana sincronizabila); fiecare subiect S01..S30 are atat [IMU]Sxx_WalkingN.csv cat si [OMC]Sxx.csv/C3D.`  
💬 Codul de aliniere OMC↔IMU si structura fisierelor (IMU + OMC per acelasi trial) confirma achizitia simultana.

**✅ AF-4.10 — CONFIRMAT**  
Senzori IMU montati pe segmentele membrelor inferioare.  
📎 *Dovadă:* `io_utils.py:149-222 (coloane Shank/Foot/Thigh/Pelvis LT/RT); data/raw/samala_2024/S01/[IMU]S01_Walking1.csv header contine Pelvis/Thigh/Shank/Foot accel & orientare per segment.`  
💬 IMU Noraxon MyoMotion are senzori pe pelvis, coapsa, tibie si picior (LT/RT) - segmentele membrelor inferioare.

**✅ AF-4.11 — CONFIRMAT**  
Sistem optic OMC utilizat ca referinta biomecanica.  
📎 *Dovadă:* `omc_events.py:84-160 (Zeni 2008 pe markeri C3D produce ground-truth HS/TO); scripts/validate_events_all.py foloseste OMC ca truth pentru validarea evenimentelor.`  
💬 OMC (C3D markeri + CSV unghiuri) este folosit explicit ca ground-truth pentru validarea evenimentelor si traiectoriei.

**✅ AF-4.12-AF-4.13 — CONFIRMAT**  
Semnalele IMU includ acceleratii pe trei axe.  
📎 *Dovadă:* `io_utils.py:163-222 (Shank/Foot/Pelvis Accel Sensor X/Y/Z m/s^2); header CSV S01 contine 42 coloane 'Accel'; README_IMU.txt 'lower limb segment access/acceleration in x, y, z (m/s^2)'.`  
💬 Acceleratiile pe 3 axe (X/Y/Z) sunt prezente direct in CSV-ul Samala pentru fiecare segment.

**❌ AF-4.14 — CONTRAZIS 🟠** 🔁²  
Semnalele IMU includ viteze unghiulare pe trei axe.  
📎 *Dovadă:* `Header CSV S01 NU contine coloane gyro/angular-velocity/rad-s/deg-s - doar orientare quaternion (x/y/z/w), acceleratii (m/s^2) si UNGHIURI de segment (course/pitch/roll in deg). preprocessing.py:68-76 gyro_pitch_dps comentariu explicit: 'datasetul Samala unde Noraxon furnizeaza doar unghiuri shank (pitch in deg), nu giroscop direct'. Viteza unghiulara e DERIVATA numeric (np.gradient) din unghi, nu masurata.`  
💬 Samala NU furnizeaza viteze unghiulare (giroscop) pe trei axe. Furnizeaza unghiuri de segment in grade; omega (deg/s) este obtinuta prin diferentiere numerica + filtrare in cod. Afirmatia ca IMU 'include viteze unghiulare pe trei axe' este eronata pentru Samala (e adevarata DOAR pentru Wassall, care are Gyr_X/Y/Z in rad/s).  ⟶ [CONFIRMAT și de al 2-lea verificator: Constatarea rezista. Context probat: AF-4.14 se afla sub sectiunea 'Dataset principal: ... Samala et al. (2024)' (capitol_4...md:34) si in blocul 'Achizitia datelor' (AF-4.9..AF-4.18); AF-4.8:36 numeste explicit IMU Noraxon 200 Hz al Samala. Wassall apare abia la AF-4.25:57, deci 'Semnalele IMU includ: ... viteze unghiulare pe trei axe' se refera la Samala. Dovada independenta: header-ul real S01 (easy-gait/data/raw/samala_2024/S01/[IMU]S01_Walking1.csv) are 141 coloane; scanare programatica dupa gyro/gyr/angular/velocity/rad-s/deg-s/rate/omega = 0 potriviri; singurele unitati prezente sunt 'deg' (orientari/unghiuri segment) si 'm/s^2' (acceleratii) — nicio coloana de viteza unghiulara. Codul confirma: preprocessing.py:68-76 gyro_pitch_dps deriva omega prin np.gradient din unghi, cu comentariu 'datasetul Samala unde Noraxon furnizeaza doar unghiuri shank (pitch in deg), nu giroscop direct'. Prin contrast, Wassall (datasets/P1.zip → FLwi02TR.csv) chiar contine Gyr_X/Gyr_Y/Gyr_Z (io_utils.py:334, rad/s). Asadar AF-4.13 (acceleratii pe trei axe) e corecta, dar AF-4.14 (viteze unghiulare pe trei axe) e falsa pentru datasetul Samala la care se refera.]

**✅ AF-4.15 — CONFIRMAT**  
Datele IMU sunt furnizate in format CSV, intrare principala.  
📎 *Dovadă:* `io_utils.py:58-91 load_samala_imu citeste [IMU]Sxx_WalkingN.csv via pd.read_csv; fisierele raw sunt .csv.`  
💬 Datele IMU Samala sunt CSV si reprezinta intrarea principala a pipeline-ului.

**✅ AF-4.16 — CONFIRMAT**  
IMU folosit pentru detectia HS/TO.  
📎 *Dovadă:* `gait_events.py:52-241 (Trojaniello + Maqbool produc HS/TO din omega IMU); validate_events_all.py ruleaza ambii detectori pe IMU.`  
💬 Detectia HS/TO se face pe semnalul IMU (omega shank). Confirmat.

**✅ AF-4.17 — CONFIRMAT**  
IMU folosit pentru delimitarea stance/swing.  
📎 *Dovadă:* `segmentation.py:36-58 GaitCycle: stance=[hs_start,to], swing=[to,hs_end], derivate din evenimentele IMU.`  
💬 Fazele stance/swing se construiesc din HS/TO detectate pe IMU. Confirmat.

**✅ AF-4.18 — CONFIRMAT**  
IMU folosit pentru extragerea parametrilor temporali.  
📎 *Dovadă:* `parameters.py:59-94 (cadenta, stride, stance%, CV, Symmetry Index din ciclurile IMU).`  
💬 Parametrii temporali (cadenta, stride, stance%) sunt calculati din ciclurile derivate IMU. Confirmat.

**✅ AF-4.19 — CONFIRMAT**  
OMC folosit pentru traiectorii/unghiuri articulare, puse la dispozitie ca CSV.  
📎 *Dovadă:* `io_utils.py:94-133 load_samala_omc citeste [OMC]Sxx.csv (multi-header 3 niveluri: Walking1..5 × LANKLE_ANGLE/LHIP/LKNEE/RANKLE... × X/Y/Z); data/raw/samala_2024/S01/[OMC]S01.csv confirmat empiric.`  
💬 OMC furnizeaza unghiuri articulare (ankle/hip/knee X/Y/Z) ca CSV; markerii (traiectorii) sunt in C3D. Confirmat.

**❌ AF-4.20 — CONTRAZIS 🔴** 🔁²  
Datele IMU (Samala) sunt esantionate la ~100 Hz.  
📎 *Dovadă:* `io_utils.py:20 SAMALA_FS=200; README_IMU.txt 'frequency of 200 Hz'; verificat empiric: coloana 'time' din [IMU]S01_Walking1.csv are pas 0.005 s = 200 Hz. NU ~100 Hz.`  
💬 IMU Samala este la 200 Hz, nu ~100 Hz. Aceasta contrazice direct si AF-4.8 (care spune corect 200 Hz). Cifra '~100 Hz' provine probabil dintr-o confuzie cu Wassall (care e 100 Hz). Pentru Samala, fs IMU real = 200 Hz.  ⟶ [CONFIRMAT și de al 2-lea verificator: Am incercat sa refut constatarea, dar toate sursele independente confirma 200 Hz: (1) io_utils.py:20 SAMALA_FS=200 cu comentariu 'verificat empiric pe S01 (2888 frame / 14.44 s)'; docstring io_utils.py:4 'IMU Noraxon 200 Hz'. (2) README_IMU.txt:18 (datasetul brut, de la furnizorii datelor): 'measurement frames ... captured at a frequency of 200 Hz'. (3) Recalcul empiric independent al CSV-ului brut [IMU]S01_Walking1.csv: n=2888 frame, median dt=0.005 s => fs=200.000 Hz, durata=14.435 s. Cifra ~100 Hz corespunde de fapt Wassall (io_utils.py:21 WASSALL_FS=100, Xsens Awinda) - exact confuzia identificata de coleg. Niciun fisier de cod/date nu sustine 100 Hz pentru Samala.]

**🟡 AF-4.21 — PARTIAL 🟢**  
Frecventa suficienta pentru captarea evenimentelor dinamice.  
📎 *Dovadă:* `io_utils.py:20 (200 Hz). Afirmatia de oportunitate e plauzibila, dar este atasata cifrei eronate ~100 Hz din AF-4.20.`  
💬 Afirmatia generala (frecventa suficienta pentru evenimente dinamice) e adevarata la 200 Hz, dar contextul (~100 Hz) e gresit. Continuarea frazei AF-4.20.

**🟡 AF-4.22 — PARTIAL 🟠**  
OMC achizitionat la frecventa mai mare (100-200 Hz).  
📎 *Dovadă:* `C3D POINT RATE=200.0 (S01_Walking1.c3d, verificat empiric); omc_events.py:64 citeste RATE din C3D. OMC real = 200 Hz fix, nu un interval.`  
💬 OMC e la 200 Hz exact (nu un interval 100-200 Hz). Mai grav, AF-4.22 spune ca OMC e 'mai mare' decat IMU, dar conform cifrei eronate IMU=~100 Hz din AF-4.20 — in realitate AMBELE sunt 200 Hz, deci OMC NU e mai mare decat IMU la Samala. Valoarea 200 Hz e in interval, dar premisa comparativa e gresita.

**✅ AF-4.23 — CONFIRMAT**  
OMC asigura o referinta precisa a miscarii articulare.  
📎 *Dovadă:* `omc_events.py:84-160 (Zeni 2008 ground-truth), scripts/validate_events_all.py foloseste OMC ca truth.`  
💬 OMC e folosit ca referinta de validare. Continuarea AF-4.22; afirmatia in sine e corecta.

**🟡 AF-4.24 — PARTIAL 🟢**  
Unghiurile articulare OMC sunt sincronizate temporal cu IMU.  
📎 *Dovadă:* `omc_events.py:179-210 align_omc_to_imu: NU presupune sincronizare nativa, ci ALINIAZA prin cross-correlation (argmax) pe unghiul gleznei. events_validation.csv contine coloana 'align_offset_s' (offset nenul) → semnalele NU erau sincronizate la nivel de frame si necesita aliniere algoritmica.`  
💬 Afirmatia ca OMC si IMU sunt 'sincronizate temporal' e doar partial adevarata: in cod e nevoie de o aliniere explicita prin cross-correlation (offset nenul stocat per trial), deci sincronizarea nu e garantata nativ — e recuperata algoritmic.

**❌ AF-4.25 — CONTRAZIS 🔴** 🔁²  
Wassall NTNU 2025: 16 utilizatori de proteza transtibiala.  
📎 *Dovadă:* `datasets/dataverse_README.txt:21 'twenty lower limb prosthetic users ... 11 transtibial, 8 transfemoral, 1 bilateral'; data/processed/wassall_per_trial.csv → 16 participanti unici procesati (P1,P2,P4,P6,P7_TF,P7_TT,P8,P9,P10,P11,P13,P14,P15,P16,P17,P19). Dintre cei 16 procesati, aprox jumatate sunt TRANSFEMORALI (P4,P9,P10,P14,P16,P19,P7_TF) — NU toti transtibiali.`  
💬 Dubla eroare: (1) datasetul sursa are 20 utilizatori, nu 16 (16 e numarul efectiv procesat in pipeline, restul 4 - P3,P5,P12,P18,P20 - lipsesc din date); (2) cei 16 NU sunt toti transtibiali — includ utilizatori transfemorali. Afirmatia 'use of data from 16 transtibial prosthesis users' e factual gresita pe ambele planuri.  ⟶ [CONFIRMAT și de al 2-lea verificator: Am incercat sa refut, dar ambele erori se confirma din date independente, NU din documentatie. PRONG 1 (numarul 20 vs 16): datasets/dataverse_README.txt (si copia din easy-gait/data/raw/wassall_2025/dataverse_README.txt) linia 21 descrie 'twenty lower limb prosthetic users (11 transtibial, 8 transfemoral, 1 bilateral)', iar tabelul de participanti listeaza explicit P1..P20. Folderul brut easy-gait/data/raw/wassall_2025/ contine doar 16 foldere de participant (P1,P2,P4,P6,P7_TF,P7_TT,P8,P9,P10,P11,P13,P14,P15,P16,P17,P19) — lipsesc fizic P3,P5,P12,P18,P20. CSV-ul wassall_per_trial.csv confirma exact aceleasi 16 ID-uri unice procesate. Docstring-ul codului in io_utils.py:304 spune chiar 'Listeaza participantii (P1..P20, plus P7_TT/P7_TF)' — deci datasetul are 20, raportul foloseste 16 = numarul procesat, nu marimea datasetului. PRONG 2 (toti transtibiali): mapand cele 16 ID-uri procesate la coloana 'Type of prosthetic' din README, rezulta 9 transtibiali si 7 TRANSFEMORALI: P4=Right Transfemoral, P9=Left Transfemoral, P10=Left Transfemoral, P14=Right Transfemoral, P16=Left Transfemoral, P19=Right Transfemoral, plus P7_TF (piciorul stang transfemoral al participantului bilateral P7). Asadar numarul 16 nici nu egaleaza numarul de transtibiali (care e 9), iar grupul nu e omogen transtibial. Nicio interpretare rezonabila nu salveaza afirmatia: nici '16'=marimea datasetului (e 20), nici '16'=numarul de transtibiali (e 9), iar README-ul este sursa proprie a acestui dataset, nu un fisier .md/.pdf explicativ. Verdictul CONTRAZIS al colegului este corect.]

**✅ AF-4.26 — CONFIRMAT**  
Wassall: exclusiv IMU purtabili, teren real, fara OMC.  
📎 *Dovadă:* `dataverse_README.txt:21 'four body worn IMUs ... real-world terrain'; io_utils.py:5 'Xsens Awinda 100 Hz + terrain labels' (fara OMC); compute_wassall_summary.py proceseaza doar IMU.`  
💬 Wassall foloseste 4 IMU purtabile Xsens pe teren real, fara sistem optic de referinta. Confirmat.

**✅ AF-4.27-AF-4.30 — CONFIRMAT**  
Activitati Wassall: plan, scari, pante, suprafete instabile (iarba, denivelat).  
📎 *Dovadă:* `io_utils.py:23-32 WASSALL_TERRAIN_LABELS {1:flat,2:grass,4:stair_ascent,5:stair_descent,6:slope_ascent,7:slope_descent,8:gravel,9:uneven}; data/processed/wassall_per_terrain.csv contine flat/grass/gravel/slope/stair/uneven.`  
💬 Toate categoriile de teren mentionate (plan, scari, pante, iarba, denivelat) exista in etichetele si rezultatele reale. Observatie: exista si 'gravel' (pietris) si 'CS'/'STEP_MULTI' nementionate in text, dar lista din text e un subset corect.

**✅ AF-4.31 — CONFIRMAT**  
Mers cu si fara dispozitive de sprijin (baston).  
📎 *Dovadă:* `data/processed/wassall_per_terrain_walkaid.csv (separare cu/fara baston); dataverse_README.txt:21 'with and without a walking aid'; activity_compare.py:92 walkaid_code.`  
💬 Distinctia cu/fara baston exista in date si in rezultate (efect baston pe cadenta/stance). Confirmat.

**✅ AF-4.32 — CONFIRMAT**  
Semnalele IMU Wassall esantionate la ~100 Hz, reutilizeaza aceiasi algoritmi.  
📎 *Dovadă:* `io_utils.py:21 WASSALL_FS=100; dataverse_README.txt 'recorded at 100Hz, using Xsens Awinda'; activity_compare.py:83 reutilizeaza detect_events_trojaniello (acelasi algoritm ca Samala, cu prosthetic=True).`  
💬 Wassall e la 100 Hz si pipeline-ul reutilizeaza Trojaniello/segmentare/parametri. Aici cifra ~100 Hz este corecta (spre deosebire de AF-4.20 unde a fost aplicata gresit la Samala).

**⚪ AF-4.33 — NEVERIFICABIL 🟠**  
GaitRec: peste 75.000 trial-uri bilaterale GRF.  
📎 *Dovadă:* `grep '(?i)gaitrec' pe tot proiectul: apare DOAR in docs (DESIGN.md, ALGORITHMS.md) si in scaffolding-ul de verificare (build_workunits.py). ZERO referinte in src/, scripts/, notebooks/, data/. Nu exista director data/raw/gaitrec; data/raw/ contine doar samala_2024 si wassall_2025.`  
💬 GaitRec NU este folosit in cod sau rezultate — niciun fisier nu il proceseaza, nu exista date GaitRec in proiect. Cifra de 75.000 trial-uri nu poate fi verificata din proiect (provine din literatura). GaitRec e doar mentionat conceptual, nu utilizat.

**⚪ AF-4.34-AF-4.37 — NEVERIFICABIL 🟢**  
GaitRec: platforme de forta, tipare patologice, ~1000 Hz.  
📎 *Dovadă:* `Nicio implementare GaitRec in proiect (vezi AF-4.33). Caracteristicile (platforme forta, ~1000 Hz, GRF) nu pot fi confirmate din cod/date.`  
💬 Aceste afirmatii descriu datasetul GaitRec din literatura, dar nu exista nicio dovada in cod/rezultate ca a fost achizitionat sau procesat. Neverificabil din sursa de adevar a proiectului.

**⚪ AF-4.38-AF-4.41 — NEVERIFICABIL 🟠**  
GaitRec util pentru validari statistice, comparatii parametri, simetrie.  
📎 *Dovadă:* `Niciun script/notebook/tabel nu foloseste GaitRec. Validarile statistice reale (tab03/tab04) sunt pe Samala; parametrii temporali agregati pe teren sunt pe Wassall (tab02). GaitRec nu apare in niciun rezultat.`  
💬 Utilitatile declarate ale GaitRec (validari, comparatii, simetrie) sunt prezentate la timpul viitor/potential, dar nu sunt materializate in cod. Recomandare: fie se sterge sectiunea GaitRec, fie se reformuleaza explicit ca dataset 'considerat dar neutilizat'.

#### Figuri / tabele

| Referință | Există | Sursă | Observații |
| --- | --- | --- | --- |
| Figura 4.3.5 (cadenta per teren) — corespunde fig03 | da | `easy-gait/notebooks/figs/fig03_cadence_per_terrain.png; easy-gait/data/processed/wassall_per_terrain.csv` | Exista easy-gait/notebooks/figs/fig03_cadence_per_terrain.png. Legenda din text afirma cadenta minima pe scari (stair) si pietris (gravel) si maxima pe flat/grass. Confirmat partial de date: stair=82.8 (minim real), gravel=87.5, dar maximul real e grass=105.3 (nu flat=95.1). Afirmatia 'flat are cadenta superioara' e mai slaba decat realitatea — grass are cea mai mare cadenta. Stair fiind minim e corect. |
| tab01 population_summary (Samala demografie/parametri) | da | `easy-gait/notebooks/tables/tab01_population_summary.csv` | easy-gait/notebooks/tables/tab01_population_summary.{csv,txt} exista. Sustine AF-4.8 (30 subiecti, demografie). Atentie: tab01 are 30 randuri prosth dar 29 intact (S27 anomalie). |
| tab02 wassall_per_terrain | da | `easy-gait/notebooks/tables/tab02_wassall_per_terrain.csv` | Exista, dar contine doar 6 terenuri (flat/grass/gravel/slope/stair/uneven), excluzand CS si STEP_MULTI prezente in data/processed/wassall_per_terrain.csv (8 categorii). Relevant pentru AF-4.27..4.30. |

#### ✏️ Corecturi de redactare propuse

**AF-4.14**  
- ❌ Original: *Semnalele IMU includ: ... viteze unghiulare pe trei axe.*
- ✅ Corectat: **Semnalele IMU includ: acceleratii pe trei axe si orientarea de segment (cuaternion). Spre deosebire de Wassall, sistemul Noraxon din Samala nu furnizeaza viteze unghiulare masurate direct (giroscop); viteza unghiulara a tibiei este obtinuta prin diferentiere numerica a unghiului de segment, urmata de filtrare Butterworth (cutoff 15 Hz).**

**AF-4.20**  
- ❌ Original: *Datele IMU sunt esantionate la o frecventa de aproximativ 100 Hz, suficienta pentru captarea evenimentelor dinamice ale mersului.*
- ✅ Corectat: **Datele IMU din datasetul Samala sunt esantionate la o frecventa de 200 Hz, suficienta pentru captarea fidela a evenimentelor dinamice ale mersului (heel strike si toe off).**

**AF-4.22**  
- ❌ Original: *Datele de motion capture au fost achizitionate la o frecventa mai mare (100-200 Hz) pentru a asigura o referinta precisa a miscarii articulare.*
- ✅ Corectat: **Datele de motion capture (OMC) au fost achizitionate la 200 Hz, identica cu frecventa IMU, asigurand o referinta precisa, sincronizabila la nivel de esantion, a miscarii articulare.**

**AF-4.24**  
- ❌ Original: *Unghiurile articulare furnizate in dataset sunt sincronizate temporal cu semnalele IMU.*
- ✅ Corectat: **Unghiurile articulare furnizate de OMC sunt aliniate temporal cu semnalele IMU printr-o procedura de corelatie incrucisata (cross-correlation) pe unghiul gleznei, offset-ul rezultat fiind aplicat per trial inainte de comparatia evenimentelor.**

**AF-4.25**  
- ❌ Original: *se va utiliza un dataset complementar care include date de la 16 utilizatori de proteza transtibiala.*
- ✅ Corectat: **se utilizeaza un dataset complementar (Wassall NTNU 2025) care, in forma sa publica, contine date de la 20 de utilizatori de proteza de membru inferior (11 transtibial, 8 transfemoral, 1 bilateral). In analiza de fata au fost procesate efectiv datele a 16 participanti (atat transtibiali cat si transfemorali), restul fiind exclusi din cauza datelor lipsa sau incomplete.**

**AF-4.33-AF-4.41**  
- ❌ Original: *Datasetul GaitRec ... este util pentru: validari statistice la scara larga; comparatii intre parametri temporali ai mersului; studii asupra regularitatii si simetriei mersului.*
- ✅ Corectat: **Datasetul GaitRec (peste 75.000 de trial-uri bilaterale bazate pe forte de reactiune la sol, achizitionate cu platforme de forta la ~1000 Hz) a fost identificat ca potential set complementar pentru validari statistice la scara larga, comparatii ale parametrilor temporali si studii de simetrie. In implementarea curenta GaitRec NU este procesat: rezultatele lucrarii se bazeaza exclusiv pe seturile Samala 2024 si Wassall 2025, integrarea GaitRec ramanand o directie de dezvoltare ulterioara.**

#### 📌 Lacune — ce ar trebui adăugat

- **[medie]** Textul NU mentioneaza ca subiectul S04 lipseste complet din rezultatele de validare (29/30 subiecti procesati), desi scripturile itereaza S01..S30 si tabelele raporteaza n_trials=290.
  - ✍️ *Text propus:* Din motive de calitate a datelor brute, subiectul S04 a fost exclus din etapa de validare a evenimentelor si a traiectoriei; rezultatele raportate in Capitolul de validare provin asadar de la 29 din cei 30 de participanti Samala (290 trial-uri totale).
- **[ridicata]** Textul afirma (AF-4.14) ca IMU Samala include viteze unghiulare pe trei axe, dar nu precizeaza ca Samala furnizeaza DOAR unghiuri de segment si ca viteza unghiulara este obtinuta prin diferentiere numerica in cod. Aceasta este o caracteristica metodologica importanta.
  - ✍️ *Text propus:* Spre deosebire de datasetul Wassall (care contine giroscop direct, Gyr_X/Y/Z in rad/s), sistemul Noraxon din datasetul Samala furnizeaza pentru fiecare segment orientarea (cuaternion), acceleratiile pe trei axe si unghiurile de segment (course/pitch/roll, in grade), dar NU si viteza unghiulara masurata direct. In consecinta, viteza unghiulara a tibiei (deg/s), necesara algoritmilor de detectie a evenimentelor, este obtinuta prin diferentiere numerica centrata a unghiului de pitch, urmata de filtrare Butterworth low-pass (cutoff 15 Hz).
- **[medie]** Nu se mentioneaza ca sincronizarea OMC↔IMU se realizeaza algoritmic prin cross-correlation (offset nenul per trial), nu nativ.
  - ✍️ *Text propus:* Deoarece achizitia simultana nu garanteaza alinierea la nivel de esantion intre fluxurile IMU si OMC, alinierea temporala se realizeaza algoritmic prin corelatie incrucisata (cross-correlation) aplicata pe unghiul gleznei normalizat; offset-ul rezultat este stocat per trial si folosit la suprapunerea evenimentelor.
- **[medie]** Numarul de IMU si plasarea lor in Wassall (4 senzori: PS prosthetic shank, TH prosthetic thigh, TR trunk, OS other shank) nu este mentionat; textul spune doar 'senzori IMU purtabili'.
  - ✍️ *Text propus:* Pentru fiecare proba, datasetul Wassall contine inregistrari de la patru senzori IMU Xsens Awinda plasati pe tibia protetica (PS), coapsa protetica (TH), trunchi (TR, la nivel L4) si tibia contralaterala (OS). Analiza de fata foloseste cu precadere semnalul tibiei protetice (PS, giroscop axa Y) pentru detectia evenimentelor de mers.
- **[scazuta]** Lista de terenuri din text omite 'gravel' (pietris) ca activitate distincta, desi apare in rezultate (n=39, cadenta 87.5).
  - ✍️ *Text propus:* Suprafetele analizate includ: teren plan, iarba, pietris, scari (urcare/coborare), pante (urcare/coborare) si teren denivelat/instabil, fiecare cu o eticheta numerica de teren in fisierele sursa.
- **[ridicata]** GaitRec este prezentat ca dataset utilizat, dar nu exista niciun cod/rezultat care sa il proceseze. Aceasta limitare trebuie declarata explicit pentru a evita inducerea in eroare a cititorului.
  - ✍️ *Text propus:* Datasetul GaitRec a fost analizat ca potential set complementar pentru validari statistice la scara larga, insa in implementarea curenta el NU este procesat efectiv: pipeline-ul si rezultatele prezentate in aceasta lucrare se bazeaza exclusiv pe seturile Samala 2024 si Wassall NTNU 2025. Integrarea GaitRec ramane o directie de dezvoltare ulterioara.

---

### WU-IV-02 — 4.3 Prelucrarea/analiza datelor + figuri exploratorii + fluxul de date

*Sub-secțiunea descriptiv-metodologică (AF-4.42, 4.44, 4.45, 4.49, 4.58, 4.59) este SOLIDĂ și se confirmă linie cu linie în cod: filtrul Butterworth (15/6 Hz, ordin 4, zero-phase), algoritmii Trojaniello și Maqbool, formula de magnitudine accel, segmentarea/parametrii, fluxul de date și pipeline-ul de validare Zeni + cross-correlation sunt descrise corect. AF-4.47 e parțial (calibrarea '0° la primul HS' e valabilă doar pentru pipeline-ul FSM, nu implicit). PROBLEMELE CRITICE sunt în cifrele numerice exploratorii: (1) stance ~49.6% / swing 50.4% (AF-4.53) nu apare nicăieri în proiect — valoarea reală minimă de stance e 52.1%, iar mediile sunt 51.7%/55.5%; (2) duratele per-subiect și etichetele S14/S02/S10/S08 (AF-4.54/4.55) NU corespund tabelului Samala — 0.606 s pentru S14 este fals (real ~1.13 s); (3) valorile cadenței din Fig 4.3.4 (flat 107, uneven/slope 101, grass 102) NU corespund nici mediilor, nici medianelor reale, iar eticheta 'MEDIANE' e greșită (figura afișează media). De asemenea, Fig 4.4.1 (flowchart) nu este generat de cod și trebuie verificat manual, iar Fig 4.3.5 'distribuție cadență' nu are corespondent direct (fig05 este stride CV). URGENT de reparat: AF-4.53, AF-4.54/4.55 și cifrele/eticheta din Fig 4.3.4 înainte de predare — sunt afirmații numerice direct contrazise de rezultatele proiectului.*

#### Verdicte pe afirmații

**✅ AF-4.42 — CONFIRMAT**  
Butterworth ordin 4 zero-phase (filtfilt); cutoff 15 Hz detecție evenimente, 6 Hz cinematică articulară.  
📎 *Dovadă:* `preprocessing.py:16-46 (butter_lowpass: cutoff_hz=15.0, order=4, btype='low', scipy.signal.filtfilt); io_utils.py:346-350,391-397 (compute_ankle_angle: smooth_cutoff_hz=6.0, butter ordin 4); omc_events.py:75-81 (Zeni low-pass 6.0 Hz ordin 4)`  
💬 Toate cele patru cifre se confirmă în cod: filtru Butterworth ordin 4, zero-phase prin filtfilt; cutoff implicit 15 Hz pe omega/gyro pentru detecția evenimentelor (gait_events.py:60,86,176) și cutoff 6 Hz atât pentru unghiul gleznei (io_utils.py) cât și pentru filtrarea markerilor OMC (omc_events.py). De notat ca observație suplimentară: filtfilt dublează ordinul efectiv (2×4=8), menționat explicit în docstring (preprocessing.py:32).

**✅ AF-4.44 — CONFIRMAT**  
Trojaniello offline: viteza unghiulară tibie sagital, vârf pozitiv mid-swing ca ancoră, minime locale pentru HS/TO; praguri scalate la 60% pentru proteze.  
📎 *Dovadă:* `gait_events.py:90-100 (peak_height=0.6*P95, find_peaks pe omega filtrat); gait_events.py:110-127 (HS=argmin în [p,p+0.35fs], TO=argmin în [p-0.45fs,p-0.10fs]); gait_events.py:94-96 (scale=0.6 if prosthetic; hs_thr=-20*scale, to_thr=-10*scale)`  
💬 Implementarea corespunde descrierii: omega shank pitch sagital, vârf pozitiv mid-swing (find_peaks pe omega cu prag adaptiv 0.6×P95) ca ancoră, apoi minime locale (argmin) în ferestrele pentru HS și TO. Pentru picior protetic pragurile sunt scalate ×0.6 (rezultând -12/-6 dps). Corect.

**✅ AF-4.45 — CONFIRMAT**  
Maqbool R-GEDS real-time eșantion cu eșantion: STANCE/SWING/HS_PENDING + refractar; praguri viteză unghiulară + magnitudine accel |a|=sqrt(ax2+ay2+az2), spike HS ~1.5g.  
📎 *Dovadă:* `gait_events.py:188-213 (FSM 3 stări STANCE→SWING→HS_PENDING, refractary_s=0.25, buclă for i in range(n)); gait_events.py:177-178,205 (a_g=a_mag/9.80665, prag a_g>accel_hs_g=1.5g); io_utils.py:340-343 (accel_magnitude = np.linalg.norm = sqrt(sum ai^2)); io_utils.py:163-171 (3 coloane accel X/Y/Z)`  
💬 Toate elementele se confirmă: state machine real-time eșantion cu eșantion cu 3 stări (STANCE/SWING/HS_PENDING) și refractar 0.25s; praguri pe viteza unghiulară (omega_swing=50, omega_hs=-100 dps) și pe magnitudinea accelerației; |a| = norma vectorială pe 3 axe (sqrt(ax²+ay²+az²)); spike HS la 1.5g (accel_hs_g=1.5 implicit; pentru protetic relaxat la 1.2g — detaliu nemenționat în text dar nu contrazice).

**🟡 AF-4.47 — PARTIAL 🟢**  
Unghi gleznă intern = shank pitch - foot pitch (Perry & Burnfield); calibrat 0° la primul HS, filtrat 6 Hz, clipping ±35°.  
📎 *Dovadă:* `io_utils.py:385 (raw = -(shank_pitch - foot_pitch)); io_utils.py:393-397 (butter ordin 4, smooth_cutoff_hz=6.0, clip la ±clip_deg=35.0); io_utils.py:369,387 (reference_idx implicit=100 = 0.5s static, NU primul HS); validate_fsm_all.py:80-81 (în pipeline-ul FSM ref_idx=hs_idx[0])`  
💬 Filtrul 6 Hz (CONFIRMAT) și clipping-ul ±35° (CONFIRMAT) sunt corecte. Formula este de fapt raw = -(shank_pitch - foot_pitch) (cu semn negativ pentru convenția dorsi+/plantar-), echivalentă conceptual cu 'shank - foot' dar cu semn opus — minoră. PROBLEMA reală: calibrarea '0° la primul HS' NU este comportamentul implicit. Funcția compute_ankle_angle folosește reference_idx=100 (0.5s static) implicit (io_utils.py:369,387). Doar pipeline-ul de validare FSM (validate_fsm_all.py:80-81) recalibrează pe primul HS; în notebooks (01_explore_samala.py:47,82,141) se folosește reference_idx=100. Există deci două convenții de calibrare în cod, iar afirmația 'calibrat 0° la primul HS' este valabilă doar pentru pipeline-ul FSM, nu universal.

**✅ AF-4.49 — CONFIRMAT**  
Stride = interval între 2 HS consecutive; rejecție outlieri față de mediană; parametri cadență, durata pas (medie+SD), CV, stance%, simetrie Robinson.  
📎 *Dovadă:* `segmentation.py:23-34 (stride = [hs_start,hs_end], stride_samples = hs_end-hs_start); segmentation.py:67-74 (reject_outliers: păstrează stride în [0.5*median, 1.5*median]); parameters.py:62-68 (cadence_total=2*60*n/total, stride mean, std ddof=1, CV=std/mean); parameters.py:85-94 (symmetry_index Robinson 1987)`  
💬 Toate elementele se confirmă: stride între 2 HS consecutive, rejecție outlieri relativ la mediană (0.5–1.5×), cadență, stride mean/SD (ddof=1), CV, stance% (segmentation.py:53-54) și Symmetry Index Robinson 1987. Corect.

**❌ AF-4.53 — CONTRAZIS 🔴** 🔁²  
Valori medii stance ~49.6%, swing 50.4% (echilibru aproape simetric).  
📎 *Dovadă:* `tab01_population_summary.txt:5,11 (Samala PROSTH stance 51.7±9.8%, INTACT 55.5±4.1%); data/processed/wassall_per_terrain.csv (stance per teren 52.1–59.6%); wassall_per_trial.csv recalculat: stance mediu global 55.57%, median 56.47%, minim pe orice teren = grass 52.13%`  
💬 Nicăieri în rezultatele proiectului nu apare un stance de ~49.6% sau swing de 50.4%. Cea mai mică valoare de stance găsită în întreg proiectul este 52.1% (grass, Wassall). Samala: prosth 51.7%, intact 55.5%. Wassall global: 55.57% (mean) / 56.47% (median). Un stance de 49.6% (sub 50%) este fiziologic neobișnuit pentru mers și NU este produs de niciun script/tabel din proiect. Cifra pare preluată dintr-o sursă externă sau fabricată; nu poate fi confirmată din date. Work-unit-ul însuși ridică acest semnal de alarmă.  ⟶ [CONFIRMAT și de al 2-lea verificator: Am verificat independent fiecare agregare. Niciun MEDIU din proiect nu dă ~49.6% stance / 50.4% swing: tab01_population_summary.txt:5,11 (Samala prosth 51.7%, intact 55.5%); recalcul tab01 csv: Samala all-sides mean 53.56%, prosth 51.65% (raw, include outlierul S27=2.3%), intact 55.53%; wassall_per_trial.csv (n=506) global mean stance 55.66% / median 56.59%; tab02_wassall_per_terrain.csv: per-teren 52.13% (grass) … 59.48% (stair) — minimul agregat = grass 52.13%; wassall_per_terrain_walkaid.csv: cel mai apropiat de 50/50 este grass without_aid 50.26%/49.74% (dar swing<50%, direcția OPUSĂ afirmației); per-participant cel mai mic mediu este P7_TF 49.98% și P4 50.19% — tot nu 49.6/50.4. Singurul loc unde apar exact 49.6/50.4 este la NIVEL DE PROBĂ INDIVIDUALĂ (wassall_per_trial.csv:3 P1 FLwi02PS = 49.6/50.4; plus liniile 18,43,257,338,361,432), niciodată ca „valoare medie”. parameters.py:79 + DESIGN.md:79 confirmă swing%=100−stance%, deci 49.6→50.4 este consistent doar ca valoare punctuală, nu ca medie populațională. Concluzie: afirmația prezintă 49.6/50.4 drept „valori medii / echilibru aproape simetric”, dar acesta este un sub-50% swing-dominant care NU este produs de niciun script/tabel/CSV ca medie/agregat (un stance mediu <50% e și atipic fiziologic). Singura imprecizie minoră a colegului — „nicăieri nu apare 49.6%” — este irelevantă pentru fond: cifra apare doar punctual, nu ca rezultat mediu. Eroarea e reală.]

**❌ AF-4.54/AF-4.55 — CONTRAZIS 🔴** 🔁²  
Durata medie pas per subiect între 0.606s (S14) și 1.130s (S02); SD între 0.013s (S10) și 0.152s (S08).  
📎 *Dovadă:* `tab01_population_summary.csv:28-29 (S14 stride_mean_s 1.127 left / 1.134 right); tab01:4-5 (S02 stride 1.133 left / 1.155 right); tab01 NU conține coloană stride_std_s per subiect (doar n_cycles, cadence, stride_mean_s, stance_pct, ankle_rom_deg)`  
💬 Valorile per-subiect din text NU corespund tabelului Samala tab01. Pentru S14, tab01 dă stride 1.127–1.134 s, NU 0.606 s. Pentru S02, tab01 dă 1.133–1.155 s, iar textul îl numește maximul cu 1.130 s — apropiat ca valoare dar atribuit greșit ca 'maxim' când de fapt mai mulți subiecți au stride mai mare (ex. S29 1.499–1.513 s, S16 1.411–1.448 s). Etichetele subiecților (S14 ca minim, S02 ca maxim) sunt incorecte pentru Samala. Valoarea 0.606 s nu apare în tab01 (minimul real Samala este S10 0.925 s). SD per-subiect (0.013s/0.152s, S10/S08) NU poate fi verificat: tab01 nu exportă stride_std per subiect. Posibil ca textul să se refere la alt subset (Wassall per-participant: min P19 0.690 s, max P6 1.524 s — tot nu se potrivește cu S14/S02). Indiferent de sursă, etichetarea subiecților și valorile nu se regăsesc în rezultatele Samala.  ⟶ [CONFIRMAT și de al 2-lea verificator: Am incercat sa refut prin TOATE interpretarile rezonabile, recalculand din cod/date brute - toate esueaza. (1) tab01_population_summary.csv:28-29 confirma S14=1.127(left)/1.134(right) si :4-5 S02=1.133/1.155; tab01 NU are coloana stride_std (doar n_cycles,cadence,stride_mean_s,stance_pct,ankle_rom_deg) si foloseste doar trial 1 (notebooks/01_explore_samala.py:135 load_samala_imu(...,1)). (2) Recalcul propriu pe TOATE cele 5 trial-uri/subiect (preprocessing+gait_events.detect_events_trojaniello+segmentation+parameters): MIN stride=S10 0.915 s, MAX=S29 1.520 s; S14=1.120 s, S02=1.131 s (NU e maxim - sub S29 1.52, S16/S01/S05/S22/S12/S30 toate >1.29); SD per-subiect MIN=S21 0.037 s, MAX=S26 0.122 s - deci nici 0.013/S10 nici 0.152/S08. (3) Ipoteza 'pas=stride/2': S14 -> 0.560 s (NU 0.606), minimul ar fi S10 0.458 - tot nu se mapeaza la S14=0.606. (4) Ipoteza Wassall per-participant (wassall_per_trial.csv agregat): MIN=P19 0.690 s, MAX=P6 1.524 s, etichete Pxx nu Sxx; 0.606/1.130 nu apar. Valoarea 0.606 s nu apare ca medie de subiect in NICIO sursa; contextul textului (FIGURA 33/34, stride per teren 1.51/1.28) este clar Samala. Etichetele S14=min, S02=max si atribuirile SD S10/S08 sunt toate incorecte.]

**✅ AF-4.58 — CONFIRMAT**  
Flux: (1) CSV brute via io_utils; (2) preprocesare Butterworth + magnitudine; (3) Trojaniello/Maqbool HS/TO; (4) cicluri + rejecție outlieri; (5) parametri temporali; (6) FSM generează traiectoria PCHIP.  
📎 *Dovadă:* `01_explore_samala.py:37,45-48,84,146 (load_samala_imu → gyro_pitch_dps/accel_magnitude → detect_events_trojaniello → build_cycles+reject_outliers → compute_gait_params); validate_fsm_all.py:82-88 (fsm.run_fsm → ankle_controller.generate_trajectory); ankle_controller.py:21,26-32 (PchipInterpolator, waypoint 0.30)`  
💬 Fluxul descris corespunde exact lanțului implementat: io_utils încarcă CSV brut → preprocessing (Butterworth + accel_magnitude) → gait_events (Trojaniello/Maqbool) → segmentation (build_cycles + reject_outliers) → parameters → fsm + ankle_controller (PCHIP). Corect.

**✅ AF-4.59 — CONFIRMAT**  
Pipeline validare: C3D markeri OMC prin Zeni 2008, aliniere cross-corelație pe unghiul gleznei; metrici MAE/RMSE/NRMSE/PCC exportate CSV.  
📎 *Dovadă:* `omc_events.py:120-123,128-167 (detect_omc_events_from_c3d → detect_events_zeni pe markeri C3D); validate_events_all.py:51,60,77-81 (OMC Zeni, ankle_imu, align_omc_to_imu pe unghiul gleznei); omc_events.py:179-210 (cross-correlation); validation.py:18-92 (event_mae, traj_rmse/nrmse/pcc); validate_events_all.py:173 + validate_fsm_all.py:156 (export CSV)`  
💬 Pipeline-ul de validare folosește markeri OMC din C3D prin metoda Zeni 2008 (find_peaks pe poziția heel/toe relativ la centrul pelvisului), aliniere prin cross-correlation pe unghiul gleznei (align_omc_to_imu, scipy.signal.correlate), și exportă MAE/RMSE/NRMSE/PCC în CSV. Toate confirmate. Observație: NRMSE este exportat ca raport [0,∞), nu procent (validation.py:75-81).

#### Figuri / tabele

| Referință | Există | Sursă | Observații |
| --- | --- | --- | --- |
| Fig 4.3.1 explorare semnale | da | `easy-gait/notebooks/figs/fig01_signal_overview_S01_W1.png` | Fișierul există (fig01). Conține pitch shank + |accel| + unghi gleznă pentru S01 W1, conform 01_explore_samala.py:35-73. Corespunde descrierii 'explorare semnale'. |
| Fig 4.3.2 suprapunere pași intact (rocker) | da | `easy-gait/notebooks/figs/fig02_stride_overlay_S01_W1_right.png (și _left.png)` | Fișierul există (fig02). Generat de fig_2_stride_cycles (01_explore_samala.py:76-126): suprapunere cicluri normalizate 0–100% pe S01 W1 right (intact). Corespunde descrierii. |
| Fig 4.3.3 stride per teren (stair 1.51 vs flat 1.28) | da | `easy-gait/notebooks/figs/fig04_stride_per_terrain.png; tab02_wassall_per_terrain.csv` | Fișierul există (fig04_stride_per_terrain). Valorile din text (stair 1.51, flat 1.28) corespund MEDIILOR din tab02 (stair 1.51, flat 1.28). Figura este boxplot cu marker de medie (showmeans=True). Valorile sunt MEDII, nu mediane — în acest caz textul folosește corect media. Coincide. |
| Fig 4.3.4 cadență per teren (flat 107, uneven 101, slope 101, grass 102, gravel 88, stair 83 — declarate MEDIANE) | partial | `easy-gait/notebooks/figs/fig03_cadence_per_terrain.png; tab02_wassall_per_terrain.csv; data/processed/wassall_per_trial.csv` | DISCREPANȚĂ MAJORĂ. Fișierul figurii există (fig03_cadence_per_terrain), dar valorile numerice din text NU corespund nici mediilor, nici medianelor reale. Text: flat 107 / uneven 101 / slope 101 / grass 102 / gravel 88 / stair 83. MEDII reale (tab02): 95.06 / 93.16 / 92.81 / 105.28 / 87.51 / 82.76. MEDIANE reale (recalculat din wassall_per_trial.csv): flat 92.02, uneven 90.96, slope 91.27, grass 92.38, gravel 82.47, stair 81.36. Doar stair (~83) și gravel (~88) sunt aproximativ corecte ca medie; flat 107, uneven 101, slope 101, grass 102 nu se regăsesc nicăieri. Figura este boxplot care afișează MEDIA ca marker (showmeans=True), nu mediana. Eticheta 'MEDIANE' din text este eronată, iar cifrele trebuie corectate. |
| Fig 4.3.5 distribuție cadență | neclar | `easy-gait/notebooks/figs/fig05_stride_cv_per_terrain.png (NU cadență)` | NU există o figură dedicată 'distribuție cadență'. fig05 este 'stride CV per teren' (variabilitate stride), nu distribuția cadenței. Distribuția cadenței ca atare poate fi citită din boxplot-ul fig03 (care arată distribuția per teren). Maparea Fig 4.3.5 → fig05 este incorectă conceptual; trebuie clarificat ce figură se intenționează. |
| Fig 4.4.1 flowchart | nu | `(niciun fișier de flowchart în notebooks/figs/)` | NU există un fișier de flowchart generat în notebooks/figs/. Cele 15 PNG-uri sunt fig01–fig12 (semnale, overlay, cadență, stride, CV, MAE, sensibilitate, scatter evenimente, FSM RMSE/PCC, ROM, overlay, faze proteză). Flowchart-ul fluxului de date, dacă apare în lucrare, este probabil desenat manual (Visio/draw.io) și NU provine din pipeline-ul de cod — trebuie verificat de autor că diagrama corespunde fluxului real descris în AF-4.58. |

#### ✏️ Corecturi de redactare propuse

**AF-4.47**  
- ❌ Original: *Calibrat 0 grade la primul HS, filtrat 6 Hz, clipping +/-35 grade.*
- ✅ Corectat: **Unghiul gleznei este calculat intern din diferența orientărilor segmentelor tibie–picior (convenție dorsiflexie pozitivă / plantarflexie negativă, Perry & Burnfield), filtrat Butterworth la 6 Hz și limitat (clipping) la ±35°. Referința de zero grade este, implicit, un interval static de 0,5 s la începutul probei; în pipeline-ul de simulare a controlului FSM, referința este recalibrată la primul heel-strike detectat pentru a alinia faza cu fiziologia (ankle ≈ 0° la contactul inițial).**

**AF-4.53**  
- ❌ Original: *Valori medii stance ~49.6%, swing 50.4% (echilibru aproape simetric).*
- ✅ Corectat: **Durata medie a fazei de sprijin (stance) este de aproximativ 51,7% pentru membrul protetic și 55,5% pentru membrul intact în lotul Samala (corespunzător unui swing de ~48,3% respectiv ~44,5%). Pe setul Wassall, sprijinul mediu pe teren variat este de ~55,6% (52,1% pe iarbă până la 59,6% pe scări coborâte). Valoarea de 49,6% stance / 50,4% swing nu se regăsește în rezultatele proiectului și trebuie eliminată sau corectată.**

**AF-4.54/AF-4.55**  
- ❌ Original: *Durata medie pas per subiect intre 0.606s (S14) si 1.130s (S02), SD intre 0.013s (S10) si 0.152s (S08).*
- ✅ Corectat: **Durata medie a stride-ului per subiect (lotul Samala, tab01) variază de la aproximativ 0,93 s (S10) până la ~1,51 s (S29). Valorile pentru S14 (~1,13 s) și S02 (~1,13–1,16 s) se situează în zona mediană a distribuției, nu la extreme. Cifrele 0,606 s (S14) și deviațiile standard per subiect (0,013–0,152 s) nu sunt susținute de tabelul de rezultate Samala (care nu exportă SD-ul stride per subiect) și trebuie verificate la sursă sau eliminate.**

**Fig 4.3.4**  
- ❌ Original: *cadenta per teren (flat 107, uneven 101, slope 101, grass 102, gravel 88, stair 83 — MEDIANE)*
- ✅ Corectat: **cadența medie per teren (pași/min): grass 105,3 (maxim), flat 95,1, uneven 93,2, slope 92,8, gravel 87,5, stair 82,8 (minim). Valorile reprezintă medii pe trial-uri (marcate cu romb în boxplot), nu mediane; medianele corespunzătoare sunt mai mici și apropiate (flat 92,0; grass 92,4; slope 91,3; uneven 91,0; gravel 82,5; stair 81,4).**

#### 📌 Lacune — ce ar trebui adăugat

- **[ridicata]** Textul nu menționează că validarea folosește o toleranță relaxată de ±150 ms pentru potrivirea evenimentelor (Pacini Panebianco 2018), mult peste pragul de acceptabilitate din docstring (25 ms IC / 50 ms TO). Fără acest detaliu, rezultatele de sensibilitate/MAE par mai bune decât ar fi cu pragul strict.
  - ✍️ *Text propus:* Potrivirea dintre evenimentele detectate din IMU și cele de referință OMC s-a făcut cu o toleranță de ±150 ms atât pentru heel-strike, cât și pentru toe-off (prag acceptabil raportat de Pacini Panebianco et al., 2018), mai permisivă decât pragul clinic strict de 25 ms (IC) / 50 ms (TO) folosit ca obiectiv de proiectare. Această alegere reflectă caracterul eterogen al lotului (proteze pasive cu impact atenuat) și a fost aplicată uniform ambilor algoritmi.
- **[medie]** Textul nu spune că ambii algoritmi de detecție au fost rulați cu parametrul prosthetic=True forțat pe TOT lotul Samala (inclusiv membrul intact), pentru a evita pierderea de evenimente pe partea protetică.
  - ✍️ *Text propus:* În etapa de validare, ambii detectori (Trojaniello și Maqbool) au fost rulați cu pragurile relaxate pentru picior protetic (prosthetic=True) aplicate uniform tuturor subiecților și ambelor membre. Decizia, conservatoare, asigură captarea evenimentelor pe partea cu impact atenuat, dar contribuie la rata mai mare de fals-pozitive (PPV scăzut) raportată în capitolul de rezultate.
- **[medie]** Nu se precizează că unghiul gleznei calculat intern (compute_ankle_angle) înlocuiește coloanele 'Ankle Dorsiflexion LT/RT' ale sistemului Noraxon, considerate inconsistente (semn opus, valori non-fiziologice în swing). Aceasta este o decizie metodologică importantă.
  - ✍️ *Text propus:* Unghiul gleznei nu a fost preluat direct din coloanele 'Ankle Dorsiflexion LT/RT' furnizate de sistemul Noraxon, deoarece acestea s-au dovedit inconsistente (semn opus și valori non-fiziologice în faza de balans). În locul lor, unghiul a fost recalculat intern ca diferență a orientărilor segmentelor tibie–picior, urmând convenția dorsiflexie pozitivă / plantarflexie negativă (Perry & Burnfield).
- **[medie]** Pentru Samala, viteza unghiulară a tibiei NU provine dintr-un giroscop, ci este derivată numeric (gradient) din unghiul de pitch furnizat de Noraxon, apoi filtrată (15 Hz). Acest detaliu este esențial pentru reproducerea fluxului și nu apare în text.
  - ✍️ *Text propus:* În cazul setului Samala, sistemul Noraxon furnizează direct unghiul de pitch al tibiei (nu viteza unghiulară); de aceea viteza unghiulară sagitală a fost obținută prin derivare numerică centrată (np.gradient) a unghiului, urmată de filtrare Butterworth la 15 Hz. Pentru setul Wassall, viteza unghiulară este preluată direct din giroscop (Gyr_Y) și convertită din rad/s în deg/s.
- **[medie]** Limitarea reală a rezultatelor (sensibilitate 0.58–0.63, MAE 60–80 ms, PPV ~0.28–0.29) nu este pusă față în față cu pragurile de acceptabilitate din cod, iar lipsa subiectului S04 (29/30 prezenți, deși se raportează n_trials=290) nu este semnalată.
  - ✍️ *Text propus:* Trebuie menționat că performanța reală a detecției (sensibilitate HS 0.58–0.63, MAE 60–80 ms, precizie/PPV ~0.28–0.29) se situează sub pragurile de proiectare (MAE ≤25 ms, sensibilitate ≥99%), reflectând dificultatea detecției pe proteze pasive. De asemenea, subiectul S04 lipsește din fișierele de validare (29 din 30 de subiecți), chiar dacă raportarea agregată indică 290 de trial-uri.

---

### WU-IV-03 — 4.5 Preprocesare + 4.6 Trojaniello + 4.7 Maqbool

*Sub-sectiunea este in mare parte corecta pe partea de structura algoritmica si ferestre temporale, dar contine doua erori care trebuie reparate inainte de predare. (1) CONTRAZIS critic de structura: AF-4.70 afirma ca masina Maqbool are 4 stari, dar codul (gait_events.py:188-208) are doar 3 stari nominale (STANCE, SWING, HS_PENDING) — refractarul e o conditie temporala, nu o stare; aceasta e o eroare factuala usor de verificat de un evaluator. (2) PARTIAL/imprecis recurent: cifrele de prag sunt prezentate ambiguu — textul citeaza amplitudinea fiziologica (~-100 grade/s HS) ca si cum ar fi pragul algoritmic, cand pragurile reale sunt -20/-10 grade/s (Trojaniello) si -100/-60 grade/s + 1.5/1.2g (Maqbool), iar in validare se foloseste FORTAT modul protetic (praguri relaxate la 60% / -60 dps / 1.2g) pe tot lotul. Acelasi lot e descris imprecis ca 'proteze active' cand toate cele 30 sunt pasive. Restul (filtru Butterworth ordin 4 zero-phase, cutoff 15/6 Hz, padlen, magnitudine accel ca norma vectoriala, caracterul offline Trojaniello vs real-time Maqbool, scalarea 60% pentru protetic, ferestrele 350/[-450,-100]ms) este CONFIRMAT exact in cod. Tabelul tab03 si figurile fig06-08 exista si sustin cifrele de rezultat. Recomandare: corecteaza numarul de stari, distinge clar pragul algoritmic de amplitudinea fiziologica, si adauga lacunele despre prosthetic=True fortat, dubla filtrare a omega si fallback-ul HS pe acceleratie."
*

#### Verdicte pe afirmații

**🟡 AF-4.61 — PARTIAL 🟢**  
Butterworth ordin 4 zero-phase, cutoff 15 Hz pentru detectie evenimente si 6 Hz pentru cinematica (Winter 1991, Catalfamo 2010); altfel HS detectat cu 15-25 ms intarziere.  
📎 *Dovadă:* `preprocessing.py:19-20 (cutoff_hz=15.0, order=4), :43 butter(order, wn, btype='low'), :46 filtfilt (zero-phase). io_utils.py:348 smooth_cutoff_hz=6.0 pentru compute_ankle_angle (cinematica). Citare Catalfamo 2010: preprocessing.py:4-5 + :31. Winter 1991 NU apare in preprocessing.py ci doar in io_utils.py:361.`  
💬 Parametrii numerici (ordin 4, 15 Hz detectie, 6 Hz cinematica) si zero-phase via filtfilt sunt CONFIRMATI in cod. Atributiile bibliografice sunt in mare corecte (Catalfamo 2010 e citat explicit pentru cutoff 15 Hz; Winter 1991 e citat pentru cutoff 6 Hz, dar in io_utils.py nu in preprocessing.py). Afirmatia 'altfel HS detectat cu 15-25 ms intarziere' este o justificare conceptuala despre defazarea filtrului uni-directional vs zero-phase: nu poate fi verificata numeric din cod/rezultate (NEVERIFICABIL pe acea cifra) si e formulata ambiguu (filtfilt este zero-phase prin constructie, deci intarzierea de 15-25 ms ar aparea doar daca s-ar folosi un filtru intr-o singura directie, ceea ce codul NU face).

**✅ AF-4.62 — CONFIRMAT**  
butter si filtfilt din scipy.signal, padlen ajustat pentru semnale scurte.  
📎 *Dovadă:* `preprocessing.py:13 'from scipy.signal import butter, filtfilt'; :43 b,a=butter(...); :45 padlen=min(3*max(len(a),len(b)), len(signal)-1); :46 return filtfilt(b,a,signal,padlen=padlen).`  
💬 Importul din scipy.signal si calculul explicit al padlen pentru semnale scurte sunt exact ca in afirmatie.

**🟡 AF-4.63/64/65 — PARTIAL 🟠**  
Maqbool: |a|=sqrt(ax^2+ay^2+az^2) din acceleratiile shank (m/s^2); spike HS peste ~1.5g (14.7 m/s^2).  
📎 *Dovadă:* `io_utils.py:340-343 accel_magnitude = np.linalg.norm(arr, axis=1) (= sqrt(sum patrate)); coloane in m/s^2: io_utils.py:165-167 'Shank Accel Sensor X/Y/Z LT (m/s^2)'. gait_events.py:177-178 a_mag NEfiltrata, a_g=a_mag/9.80665; :149 accel_hs_g=1.5 (default), confirmare HS la a_g>accel_hs_g (:205). 1.5g=1.5*9.80665=14.71 m/s^2. DAR :180-182: daca prosthetic=True -> accel_hs_g=1.2 g.`  
💬 Formula magnitudinii (norm vectoriala), unitatea m/s^2 a acceleratiilor shank si conversia in g (impartire la 9.80665) sunt CONFIRMATE; 1.5g=14.7 m/s^2 este corect. ATENTIE insa: pragul 1.5g se aplica DOAR pentru non-protetic. In pipeline-ul real de validare toti subiectii ruleaza cu is_prosthetic=True (validate_events_all.py:89), deci pragul efectiv folosit pentru rezultatele raportate este 1.2g (=11.77 m/s^2), nu 1.5g. Capitolul ar trebui sa precizeze acest lucru pentru a fi exact.

**✅ AF-4.66 — CONFIRMAT**  
Trojaniello et al. (2014), standard offline.  
📎 *Dovadă:* `gait_events.py:5-6 docstring '(A) detect_events_trojaniello — gold-standard offline pe gyro tibial pitch. Bazat pe Aminian 2002, Salarian 2004, Trojaniello 2014.'; :52 def detect_events_trojaniello.`  
💬 Metoda este implementata ca varianta offline si referinta Trojaniello 2014 este declarata explicit. Caracterul offline e confirmat si de faptul ca foloseste percentila globala P95 (gait_events.py:90) si find_peaks pe intregul semnal (necesita vizualizare globala).

**🟡 AF-4.67 — PARTIAL 🟠**  
Varf pozitiv mid-swing ancora; minim dupa peak (~-100 grade/s) = HS; minim inainte peak (~-30..-100 grade/s) = TO; ferestre HS [tpeak, tpeak+350ms], TO [tpeak-450ms, tpeak-100ms].  
📎 *Dovadă:* `Ferestre: gait_events.py:58-59 hs_window_s=(0.0,0.35), to_window_s=(-0.45,-0.10) -> HS [tpeak, tpeak+350ms], TO [tpeak-450ms, tpeak-100ms] CONFIRMATE. Ancora varf mid-swing: :90-93 peak_height=0.6*P95, :100 find_peaks(omega, height=peak_height) CONFIRMAT. Praguri REALE: :95-96 hs_thr=-20.0*scale, to_thr=-10.0*scale (scale=1.0 non-protetic, 0.6 protetic -> -12/-6 dps).`  
💬 Logica (varf pozitiv mid-swing drept ancora, minim dupa peak = HS, minim inainte = TO) si ferestrele temporale (350ms / [-450,-100]ms) sunt CONFIRMATE exact. INSA cifrele de prag '~-100 grade/s pentru HS' si '~-30..-100 grade/s pentru TO' descriu AMPLITUDINEA fiziologica a semnalului (din docstring gait_events.py:13-14), NU pragurile de acceptare folosite de algoritm. Pragurile reale de decizie sunt mult mai permisive: hs_thr=-20 dps (-12 dps protetic) si to_thr=-10 dps (-6 dps protetic). Aceasta discrepanta prag-vs-amplitudine este chiar cauza PPV/F1 scazut (multe false-positive, n_imu_hs>>n_omc_hs). Afirmatia trebuie reformulata sa distinga clar amplitudinea semnalului de pragul algoritmic.

**✅ AF-4.68 — CONFIRMAT**  
Proteza: amplitudini reduse ale omega shank; pragurile scalate la 60% (Maqbool 2017).  
📎 *Dovadă:* `gait_events.py:94 scale=0.6 if prosthetic else 1.0; :95-96 hs_thr=-20.0*scale, to_thr=-10.0*scale -> -12/-6 dps pentru protetic. Docstring :70 'Pentru picior protetic: relaxare praguri la 60% (Maqbool 2017).'`  
💬 Scalarea pragurilor Trojaniello la 60% pentru picior protetic este implementata exact si referinta Maqbool 2017 e declarata. Justificarea (amplitudini omega reduse la proteze pasive) e coerenta cu datele: ROM ankle prosth 17.0 vs intact 38.6 grade (tab01).

**🟡 AF-4.69 — PARTIAL 🟠**  
R-GEDS (Maqbool 2017) pentru proteze active.  
📎 *Dovadă:* `gait_events.py:8-9 '(B) detect_events_maqbool — real-time, prietenos pentru FSM. Bazat pe Maqbool 2017 (referinta directa pentru amputat lower-limb).' Dataset Samala: samala_metadata.py:8-10 toate cele 30 proteze PASIVE, transtibiale; nicio gleznă acționată.`  
💬 Algoritmul Maqbool R-GEDS este implementat ca metoda real-time. INSA caracterizarea 'pentru proteze active' este imprecisa/inselatoare in contextul acestui proiect: TOATE protezele din datasetul Samala pe care s-a validat sunt PASIVE (24 SACH, 3 ESR, 2 sPace, 1 single-axis). Maqbool 2017 a fost dezvoltat pentru amputatii membrului inferior in general; FSM-ul real-time este relevant pentru control de proteza ACTIVA, dar datasetul de validare NU contine proteze active. Formularea ar trebui sa spuna 'orientat catre control real-time de proteza activa' sau pur si simplu 'amputat de membru inferior', nu sa lase impresia ca datele sunt de la proteze active.

**❌ AF-4.70 — CONTRAZIS 🟠** 🔁²  
Masina cu 4 stari: STANCE, SWING, HS_PENDING, perioada refractara; STANCE->SWING cand omega>omega_swing_in; dupa timp minim in swing omega<omega_hs SI |a|>a_hs -> HS_PENDING; TO la STANCE->SWING.  
📎 *Dovadă:* `gait_events.py:188 state='STANCE'; :196 'if state==STANCE'; :201 'elif state==SWING'; :204 'elif state==HS_PENDING'. Doar 3 stari nominale. Refractar = variabila de timp: :186 refract=int(refractary_s*fs); :197 conditia (i-t_last_hs)>refract — NU este o stare. Docstring :156 'Stari: STANCE -> SWING -> HS_PENDING -> STANCE.' Valori: :147 omega_swing_in_dps=50.0; :148 omega_hs_dps=-100.0 (:181 -60.0 protetic); :149 accel_hs_g=1.5 (:182 1.2 protetic).`  
💬 Numarul de stari este GRESIT: masina are 3 stari nominale (STANCE, SWING, HS_PENDING), nu 4. Perioada refractara NU este o stare ci o conditie temporala (i-t_last_hs)>refract evaluata in tranzitia STANCE->SWING. Restul descrierii logicii e corecta: STANCE->SWING la omega>50 dps (emite TO), SWING->HS_PENDING dupa timp minim swing si omega<omega_hs, HS_PENDING->STANCE la confirmare accel. Valorile: omega_swing_in=50 dps CONFIRMAT; omega_hs=-100 dps default dar -60 dps protetic (in validare se foloseste -60 fortat); a_hs=1.5g default dar 1.2g protetic.  ⟶ [CONFIRMAT și de al 2-lea verificator: Am incercat sa refut constatarea colegului dar codul o confirma fara echivoc. In gait_events.py, functia detect_events_maqbool foloseste o singura variabila `state` cu EXACT 3 valori posibile: linia 188 `state = "STANCE"`; linia 196 `if state == "STANCE"`; linia 201 `elif state == "SWING"`; linia 204 `elif state == "HS_PENDING"`. Nu exista a patra ramura `state == ...`. Docstringul (linia 156) declara explicit lantul cu 3 stari: "Stari: STANCE -> SWING -> HS_PENDING -> STANCE." Asa-numita "perioada refractara" NU este o stare ci o variabila de timp: linia 186 `refract = int(refractary_s * fs)`, folosita ca o conditie de garda in tranzitia STANCE->SWING la linia 197: `if omega[i] > omega_swing_in_dps and (i - t_last_hs) > refract`. Deci AF-4.70 numara gresit "4 stari" introducand refractarul drept stare. Restul logicii confirmate de cod: TO emis la STANCE->SWING (linia 198 `to_idx.append(i)`), omega_swing_in_dps=50.0 (linia 147), omega_hs_dps=-100.0 default / -60.0 protetic (liniile 148, 181), accel_hs_g=1.5 default / 1.2 protetic (liniile 149, 182). Validarea forteaza prosthetic=True (validate_events_all.py:89, validate_fsm_all.py:79, notebooks/04_fsm_validation.py:148), deci -60 dps este efectiv folosit in validare. Observatie minora: AF-4.70 atribuie gresit conditia `|a|>a_hs` tranzitiei catre HS_PENDING, dar in cod accel (linia 205) confirma HS_PENDING->STANCE, iar SWING->HS_PENDING (linia 202) cere doar timp minim swing SI omega<omega_hs - aceasta intareste, nu slabeste, constatarea colegului. Eroarea privind numarul de stari este reala.]

**✅ AF-4.71 — CONFIRMAT**  
Avantaj Maqbool: real-time sample-by-sample, potrivit microcontroller; Trojaniello necesita vizualizare globala.  
📎 *Dovadă:* `Maqbool: gait_events.py:195 'for i in range(n)' procesare cauzala sample-by-sample, fara look-ahead; foloseste doar stare curenta + timpi trecuti (t_to, t_last_hs). Trojaniello: :90 p95=np.percentile(omega,95) (statistica globala) si :100 find_peaks pe intregul semnal -> necesita semnalul complet (offline/global).`  
💬 Maqbool este cu adevarat cauzal/online (bucla sample-by-sample, decizie pe baza starii curente si a evenimentelor trecute), deci implementabil pe microcontroller. Trojaniello foloseste percentila globala P95 si find_peaks pe tot semnalul, deci necesita vizualizare globala (offline). Afirmatia este corecta conceptual si sustinuta de cod.

#### Figuri / tabele

| Referință | Există | Sursă | Observații |
| --- | --- | --- | --- |
| tab03 events_validation_summary | da | `D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/tables/tab03_events_validation_summary.csv` | Valorile din WU se regasesc exact: Trojaniello n_trials=290, HS MAE 79.8/median 77.5 ms, HS sens 0.584, HS F1 0.377, TO MAE 60.7/median 58.3, TO sens 0.613; Maqbool n_trials=290, HS MAE 60.2/median 56.7, HS sens 0.633, HS F1 0.395, TO MAE 76.9/median 75.8, TO sens 0.653. NB: n_valid_hs real este 237 (Trojaniello) si 250 (Maqbool), nu 290 — toleranta de potrivire e 150 ms (validate_events_all.py:35-36). |
| fig06 mae_histograms | da | `D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/figs/fig06_mae_histograms.png` | Fisier prezent; relevant pentru distributia MAE a evenimentelor HS/TO discutate in 4.6/4.7. Nu am verificat continutul pixelilor, dar denumirea corespunde subiectului WU. |
| fig07 sens_per_subject | da | `D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/figs/fig07_sens_per_subject.png` | Fisier prezent; reprezinta sensibilitatea per subiect a detectiei, relevant pentru sectiunile Trojaniello/Maqbool. |
| fig08 n_events_scatter | da | `D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/figs/fig08_n_events_scatter.png` | Fisier prezent; reprezinta n_imu vs n_omc events (ilustreaza fals-pozitivele, n_imu_hs>n_omc_hs), relevant pentru PPV scazut discutat la praguri. |

#### ✏️ Corecturi de redactare propuse

**AF-4.67**  
- ❌ Original: *minim dupa peak (~-100 grade/s) = HS; minim inainte de peak (~-30..-100 grade/s) = TO. Ferestre fixe HS [tpeak, tpeak+350ms], TO [tpeak-450ms, tpeak-100ms].*
- ✅ Corectat: **Dupa fiecare varf pozitiv mid-swing, heel strike este localizat ca minimul vitezei unghiulare in fereastra [tpeak, tpeak+350 ms], acceptat doar daca depaseste pragul hs_thr = -20 grade/s (-12 grade/s in modul protetic); toe off este minimul in fereastra [tpeak-450 ms, tpeak-100 ms], acceptat la to_thr = -10 grade/s (-6 grade/s protetic). Valorile fiziologice ale amplitudinii minimului (~-100 grade/s la HS, intre -30 si -100 grade/s la TO) sunt mult mai mari ca magnitudine decat pragurile de acceptare, marja care creste sensibilitatea dar admite fals-pozitive.**

**AF-4.70**  
- ❌ Original: *4 stari: STANCE, SWING, HS_PENDING, perioada refractara.*
- ✅ Corectat: **Masina de stari Maqbool are 3 stari nominale — STANCE, SWING si HS_PENDING — parcurse ciclic (STANCE->SWING->HS_PENDING->STANCE). Perioada refractara NU este o stare separata, ci o conditie temporala: dupa fiecare HS, urmatorul toe off este permis doar dupa ce trec refractary_s = 0.25 s (i - t_last_hs > refract). Tranzitia STANCE->SWING are loc cand omega > omega_swing_in = 50 grade/s si emite TO; SWING->HS_PENDING dupa un timp minim de swing cand omega < omega_HS (=-100 grade/s, sau -60 grade/s in modul protetic); HS_PENDING->STANCE cand |a| > a_HS (=1.5g, sau 1.2g protetic), emitand HS.**

**AF-4.63/64/65**  
- ❌ Original: *Spike HS peste ~1.5g (14.7 m/s2).*
- ✅ Corectat: **Heel strike este confirmat de un spike al magnitudinii acceleratiei peste pragul a_HS. Valoarea nominala este 1.5g (~14.7 m/s2), dar in modul protetic — folosit fortat pentru intregul lot in validare — pragul este relaxat la 1.2g (~11.8 m/s2), pentru a compensa impactul atenuat de piciorul SACH/carbon.**

**AF-4.69**  
- ❌ Original: *R-GEDS (Maqbool 2017) pentru proteze active.*
- ✅ Corectat: **R-GEDS (Maqbool 2017), un detector real-time orientat catre controlul protezelor active de membru inferior. Trebuie subliniat ca datasetul de validare Samala contine exclusiv proteze transtibiale PASIVE (24 SACH, 3 ESR, 2 sPace, 1 single-axis); algoritmul este aplicat aici ca detector de evenimente, nu pe date de la proteze actionate.**

**AF-4.61**  
- ❌ Original: *Altfel HS detectat cu 15-25 ms intarziere.*
- ✅ Corectat: **Filtrarea este aplicata zero-phase (scipy.signal.filtfilt), ceea ce elimina complet defazarea — esential pentru ca timpii evenimentelor sa nu fie distorsionati. Un filtru clasic uni-directional ar introduce o intarziere de grup care, la cutoff 15 Hz, ar putea deplasa momentul detectat al HS cu ordinul a 15-25 ms; aplicarea forward-backward (filtfilt) anuleaza aceasta intarziere.**

#### 📌 Lacune — ce ar trebui adăugat

- **[ridicata]** Capitolul nu mentioneaza ca, in pipeline-ul de validare, AMBII algoritmi ruleaza cu prosthetic=True fortat pe tot lotul, ceea ce schimba pragurile efective (Trojaniello -12/-6 dps; Maqbool omega_HS=-60 dps, a_HS=1.2g). Cifrele 'standard' citate in text (de ex. -20/-10 dps sau 1.5g) NU sunt cele folosite la rezultate.
  - ✍️ *Text propus:* In studiul de validare ambii detectori au fost rulati cu modul protetic activat (prosthetic=True) pe intregul lot Samala, ca alegere conservatoare pentru un set mixt de proteze. In consecinta, pragurile efective au fost relaxate: pentru Trojaniello hs_thr=-12 grade/s si to_thr=-6 grade/s (60% din valorile nominale -20/-10 grade/s), iar pentru Maqbool omega_HS=-60 grade/s si a_HS=1.2g (in loc de -100 grade/s si 1.5g). Aceasta relaxare creste sensibilitatea pe semnalele atenuate ale protezelor pasive, dar contribuie la rata mare de fals-pozitive observata (PPV ~0.28-0.29).
- **[medie]** Nu se mentioneaza dubla filtrare a vitezei unghiulare pentru Samala: omega este derivata din unghi si filtrata in gyro_pitch_dps (cutoff 15 Hz), apoi re-filtrata in interiorul detect_events_* (butter_lowpass cutoff 15 Hz). Acesta este un detaliu de implementare cu impact asupra netezimii semnalului.
  - ✍️ *Text propus:* Pentru datasetul Samala, viteza unghiulara a tibiei nu este masurata direct ci derivata numeric din unghiul de pitch (np.gradient) si filtrata Butterworth 15 Hz in functia gyro_pitch_dps. Deoarece detectorii aplica inca o data filtrul Butterworth 15 Hz intern, semnalul omega trece printr-o dubla filtrare zero-phase, ceea ce reduce suplimentar continutul de inalta frecventa relevant pentru detectia precisa a momentului de impact.
- **[medie]** Magnitudinea acceleratiei pentru Maqbool este folosita NEFILTRATA (intentionat, pentru a pastra spike-urile de impact), spre deosebire de omega care este filtrata. Acest contrast metodologic nu apare in capitol.
  - ✍️ *Text propus:* In detectorul Maqbool, viteza unghiulara este filtrata Butterworth (15 Hz) pentru stabilitatea pragurilor de tranzitie, in timp ce magnitudinea acceleratiei este folosita NEFILTRATA, deliberat, pentru a conserva varful brusc (spike) de impact la heel strike, care altfel ar fi atenuat de filtrare.
- **[medie]** Exista un mecanism de fallback HS in Maqbool care nu e descris: daca acceleratia nu confirma HS in ~600 ms de la TO, HS este acceptat doar pe baza vitezei unghiulare.
  - ✍️ *Text propus:* Pentru a evita pierderea ciclurilor cand pragul de acceleratie nu se atinge (impact atenuat de piciorul SACH/carbon), Maqbool include un fallback: daca dupa intrarea in HS_PENDING acceleratia nu depaseste pragul in aproximativ 600 ms (0.6*fs samples) de la TO, evenimentul HS este acceptat pe baza criteriului de viteza unghiulara.
- **[ridicata]** Pragul nominal real al heel strike (Trojaniello hs_thr=-20 grade/s) nu este mentionat deloc in text, desi este parametrul-cheie care determina performanta detectiei. Textul citeaza doar amplitudinea fiziologica ~-100 grade/s, ceea ce poate induce cititorul in eroare.
  - ✍️ *Text propus:* Pragul de acceptare al minimului de heel strike in Trojaniello este hs_thr=-20 grade/s (nominal), respectiv -12 grade/s in modul protetic — semnificativ mai permisiv decat amplitudinea fiziologica tipica a minimului (~-100 grade/s). Aceasta marja larga creste sensibilitatea pe proteze, dar admite multe minime locale care nu corespund unor heel strike reale, explicand PPV-ul scazut (0.283 Trojaniello).

---

### WU-IV-04 — 4.8 Unghi gleznei + 4.9 Segmentare + 4.10 Parametri temporali

*Sub-secțiunea este în mare măsură SOLIDĂ pe partea de formule (4.10 Parametri temporali, AF-4.74..4.82 toate CONFIRMATE exact contra parameters.py și segmentation.py: cadență 2×60×n/total, stride mean/SD ddof=1, CV=std/mean, stance%=stance_samples/stride_samples×100, swing%=100-stance%, SI Robinson 2×(P-I)/(P+I)×100). Figura Fig 4.9.1 (fig02) există și corespunde descrierii. DOUĂ probleme de exactitate de reparat, ambele non-critice dar relevante pentru rigoare: (1) AF-4.72 — afirmația 'calibrare primul HS' este doar PARȚIAL adevărată: default-ul funcției este reference_idx=100 (static 0,5 s), iar calibrarea pe HS apare doar în pipeline-ul FSM; coexistă două convenții în cod. (2) AF-4.73 — cifra '+25°' pentru valorile non-fiziologice în swing ale coloanelor Noraxon NU există în cod (inventată); restul afirmației e corect, dar valorile HS≈0/push-off≈-18/mid-swing≈+10 sunt afirmații de docstring, nu rezultate de validare. Recomand corecturile de redactare pentru AF-4.72 și AF-4.73 și adăugarea lacunei despre validarea empirică IMU-vs-OMC (PCC +0.652), care întărește exact funcția descrisă aici.*

#### Verdicte pe afirmații

**🟡 AF-4.72 — PARTIAL 🟠**  
compute_ankle_angle derivă unghiul din diferența shank-foot, dorsi+/plantar-, calibrare primul HS=0°, filtru 6 Hz, clipping ±35°.  
📎 *Dovadă:* `io_utils.py:346-397 (compute_ankle_angle); raw=-(shank_pitch-foot_pitch) la l.385; filtru butter(4, wn) cu smooth_cutoff_hz=6.0 la l.348,393; clip ±35° la l.349,397; reference_idx default=100 la l.387; vs. validate_fsm_all.py:80-81 ref_idx=hs_idx[0]`  
💬 Existența funcției, derivarea shank-foot, convenția dorsi+/plantar- (Perry & Burnfield citat l.354,383), filtrul 6 Hz și clippingul ±35° sunt CONFIRMATE exact. ÎNSĂ afirmația 'calibrare primul HS (0°)' este corectă DOAR pentru pipeline-ul FSM (validate_fsm_all.py:80-81, unde ref_idx=events.hs_idx[0]); DEFAULT-ul funcției este reference_idx=100 (=0.5 s static @200Hz, io_utils.py:387), iar fig02_stride_overlay folosește tot reference_idx=100 (01_explore_samala.py:82). Deci în cod coexistă DOUĂ convenții de calibrare diferite — funcția nu calibrează implicit pe primul HS.

**🟡 AF-4.73 — PARTIAL 🟢**  
Coloanele Ankle Dorsiflexion LT/RT Noraxon au semn opus și valori non-fiziologice în swing (+25°). Funcția proprie validată: HS~0, push-off~-18, mid-swing~+10°.  
📎 *Dovadă:* `io_utils.py:196-206 (comentariu coloane inconsistente, 'valori opuse semn și magnitudini ne-fiziologice în swing'); docstring l.201-202 'HS≈0, push-off≈-18°, mid-swing≈+10°'; l.383-384 'la heel-off ankle ~+10° dorsi, la toe-off ankle ~-15° plantar'`  
💬 CONFIRMAT că funcția proprie înlocuiește coloanele Noraxon considerate cu semn opus și non-fiziologice în swing (io_utils.py:196-206), și că docstring-ul afirmă convenția HS≈0/push-off≈-18°/mid-swing≈+10° (l.201-202). DOI probleme: (1) valoarea specifică '+25°' în swing pentru coloana Noraxon NU apare în cod — codul spune doar generic 'valori non-fiziologice/ne-fiziologice în swing', deci '+25 grade' este o cifră neverificabilă/inventată în text. (2) Aceste valori (push-off -18, mid-swing +10) sunt afirmații din DOCSTRING, NU rezultate de validare numerică; pe fig11_overlay_S01_W1_right curba IMU verde atinge push-off ~-16° și mid-swing ~+8° (aproximativ consistent dar nu identic), iar funcția nu e 'validată' formal nicăieri cu aceste praguri.

**✅ AF-4.74 — CONFIRMAT**  
Stride=[HSi,HSi+1], stance=[HSi,TOi], swing=[TOi,HSi+1]; rejecție outlieri [0.5*mediana, 1.5*mediana] în reject_outliers (lo=0.5, hi=1.5).  
📎 *Dovadă:* `segmentation.py:28-50 (stride_samples=hs_end-hs_start, stance_samples=to-hs_start, swing_samples=hs_end-to); reject_outliers lo=0.5,hi=1.5 la l.67, mask (durs>=lo*med)&(durs<=hi*med) la l.73`  
💬 Toate definițiile coincid exact: stride=[hs_start,hs_end], stance=[hs_start,to], swing=[to,hs_end] (GaitCycle l.23-50). reject_outliers păstrează cicluri cu stride_s în [0.5*median, 1.5*median] (l.67,72-73). Default lo=0.5, hi=1.5 confirmat.

**✅ AF-4.75 — CONFIRMAT**  
cadența = 60*2*n_strides/durata_totala (cadence_total=2*cadence_per_side, cadence_per_side=60*n/total).  
📎 *Dovadă:* `parameters.py:62-64: n_steps_per_side=len(cycles); cadence_per_side=60.0*n_steps_per_side/total_s; cadence_total=2.0*cadence_per_side`  
💬 Formula este exact 2×(60×n/total_s), echivalentă cu 60*2*n/total. total_s=strides.sum() (l.58). Confirmat.

**✅ AF-4.76 — CONFIRMAT**  
stride medie + SD (deviație standard).  
📎 *Dovadă:* `parameters.py:66-67: mean_s=strides.mean(); std_s=strides.std(ddof=1) if len(strides)>1 else 0.0`  
💬 Stride mean = strides.mean(), SD = std de eșantion (ddof=1) dacă >1 ciclu, altfel 0. Confirmat. Detaliu: SD folosește ddof=1 (eșantion), nu populație — nemenționat în text dar corect.

**✅ AF-4.77 — CONFIRMAT**  
CV = std/mean.  
📎 *Dovadă:* `parameters.py:68: cv = std_s / mean_s if mean_s > 0 else 0.0`  
💬 CV definit exact ca std/mean (cu protecție mean>0). Confirmat. La export se afișează ca procent (100*stride_cv, l.40), dar valoarea internă e fracție.

**✅ AF-4.78 — CONFIRMAT**  
stance% = (tTO-tHS)/(tHS_next-tHS)*100.  
📎 *Dovadă:* `segmentation.py:52-54: stance_pct = 100.0*self.stance_samples/max(self.stride_samples,1); cu stance_samples=to-hs_start (l.38) și stride_samples=hs_end-hs_start (l.30)`  
💬 stance% = 100*(to-hs_start)/(hs_end-hs_start), identic cu (tTO-tHS)/(tHS_next-tHS)*100 deoarece eșantioanele și timpul diferă doar prin factorul fs care se simplifică. Este proprietate GaitCycle, agregată ulterior (stance_pct_mean, parameters.py:76). Confirmat.

**✅ AF-4.79 — CONFIRMAT**  
swing% = 100 - stance%.  
📎 *Dovadă:* `segmentation.py:56-58: swing_pct = 100.0 - self.stance_pct`  
💬 swing% definit exact ca 100 - stance%. Confirmat.

**✅ AF-4.80 — CONFIRMAT**  
Symmetry Index Robinson = 2*(P-I)/(P+I)*100.  
📎 *Dovadă:* `parameters.py:85-94: return 100.0*2.0*(prosthetic-intact)/s, cu s=prosthetic+intact; return 0.0 dacă s==0`  
💬 SI Robinson 1987 = 100*2*(P-I)/(P+I), cu gardă pentru sumă=0. Identic cu textul. Confirmat.

**✅ AF-4.81 — CONFIRMAT**  
compute_gait_params agregă parametrii temporali pe lista de cicluri.  
📎 *Dovadă:* `parameters.py:49-82: compute_gait_params(cycles) returnează GaitParams cu cadence_total, stride mean/std, cv, stance/swing pct mean/std, duration_total_s; returnează zerouri dacă lista goală (l.51-52)`  
💬 Funcția compute_gait_params există și calculează toți parametrii agregați descriși (cadență, stride mean/std, CV, stance%, swing%). Confirmat.

**✅ AF-4.82 — CONFIRMAT**  
stance% este proprietate a GaitCycle.  
📎 *Dovadă:* `segmentation.py:52-54: @property def stance_pct(self)->float`  
💬 stance_pct (și swing_pct) sunt @property pe dataclass-ul GaitCycle. Confirmat.

#### Figuri / tabele

| Referință | Există | Sursă | Observații |
| --- | --- | --- | --- |
| Fig 4.9.1 (fig02 stride overlay S01 W1 RIGHT) | da | `D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/figs/fig02_stride_overlay_S01_W1_right.png` | Figura există și corespunde exact descrierii: panou stânga = ω shank pitch normalizat per ciclu (S01 W1 RIGHT, n=6 cicluri), panou dreapta = unghi gleznă normalizat per ciclu. Generată de 01_explore_samala.py:76-126 cu side='right', reference_idx=100, Trojaniello prosthetic=False. Pentru S01, latura RIGHT este INTACT (tab01 CSV: S01 right intact, ROM 48.4°), deci mențiunea 'RIGHT intact' din work-unit este corectă. Unghiul gleznă afișat: HS≈-15° la 0%, vârf dorsi ≈+5° la ~45%, minim plantar ≈-35° la ~65% (push-off/early swing) — valorile sunt centrate pe reference_idx=100 (static), NU pe HS=0, deci nu pornesc de la 0° la HS. Există și fig11_overlay_S01_W1_right.png (OMC vs IMU vs FSM) care confirmă vizual PCC negativ FSM (curba roșie întârziată/inversată) și IMU bună (verde urmează OMC negru). |
| fig11 overlay S01 W1 RIGHT (OMC/IMU/FSM) | da | `D:/OneDrive - Realworld Holding b.v/Documents/67/easy-gait/notebooks/figs/fig11_overlay_S01_W1_right.png` | Figură suplimentară relevantă pentru 4.8: suprapunere OMC (negru, referință) / IMU compute_ankle_angle (verde) / FSM comandat (roșu întrerupt). IMU urmează forma OMC (mid-swing pozitiv, push-off negativ), confirmând calitatea funcției. FSM (impedanță, toate negative) este în antifază — coerent cu PCC -0.244 din tab04. |

#### ✏️ Corecturi de redactare propuse

**AF-4.72**  
- ❌ Original: *Calibrare primul HS (0 grade), filtrare 6 Hz, clipping +/-35 grade.*
- ✅ Corectat: **Funcția compute_ankle_angle (io_utils.py:346-397) derivă unghiul gleznei din diferența orientării segmentelor: raw = -(shank_pitch - foot_pitch), cu convenția dorsiflexie pozitivă / plantarflexie negativă (Perry & Burnfield 2010). Asupra semnalului centrat se aplică un filtru low-pass Butterworth de ordin 4 cu cutoff 6 Hz (Winter 1991) și un clipping la ±35° pentru respingerea artefactelor peste ROM-ul fiziologic. Calibrarea la 0° se face față de reference_idx, al cărui default este 100 (0,5 s de poziție statică la 200 Hz); calibrarea explicită pe primul heel-strike detectat (ankle≈0° la contactul inițial) se aplică doar în pipeline-ul de validare FSM (validate_fsm_all.py:80-81).**

**AF-4.73**  
- ❌ Original: *Coloanele Ankle Dorsiflexion LT/RT Noraxon au semn opus si valori non-fiziologice in swing (+25 grade). Functie proprie validata: HS ~0, push-off ~-18, mid-swing ~+10 grade.*
- ✅ Corectat: **Coloanele 'Ankle Dorsiflexion LT/RT' furnizate de Noraxon pe datasetul Samala s-au dovedit inconsistente cu convenția clinică standard — semn opus și magnitudini ne-fiziologice în faza de swing (io_utils.py:196-206); de aceea sunt înlocuite cu funcția proprie compute_ankle_angle. Conform docstring-ului (io_utils.py:201-202), această funcție produce o convenție fiziologic plauzibilă (HS≈0°, push-off≈-18°, mid-swing≈+10°), confirmată calitativ de suprapunerea cu referința OMC (fig11). [Notă: valoarea specifică '+25°' în swing pentru coloanele Noraxon nu este documentată în cod și trebuie eliminată sau înlocuită cu formularea generică 'valori non-fiziologice în swing'.]**

#### 📌 Lacune — ce ar trebui adăugat

- **[medie]** reference_idx default vs. calibrare HS: textul (AF-4.72) prezintă 'calibrare primul HS (0°)' ca pe comportamentul funcției, dar default-ul real este reference_idx=100 (0.5 s static), iar calibrarea pe primul HS apare doar în pipeline-ul FSM (validate_fsm_all.py:80-81). Această dublă convenție trebuie explicitată ca limitare.
  - ✍️ *Text propus:* Trebuie precizat că funcția compute_ankle_angle folosește implicit reference_idx=100 (corespunzător la 0,5 s de poziție statică la 200 Hz), nu primul heel-strike. Calibrarea pe primul HS detectat (ankle≈0° la contactul inițial) se aplică doar în pipeline-ul de validare FSM (validate_fsm_all.py:80-81), în timp ce figurile exploratorii (fig02) folosesc referința statică la 0,5 s. Această dublă convenție de calibrare reprezintă o sursă potențială de inconsistență între figuri și metrici, și ar trebui uniformizată.
- **[scazuta]** Justificarea fiziologică/bibliografică a filtrului 6 Hz și a clippingului ±35° lipsește din formulele temporale, deși codul o documentează (Winter 1991 pentru 6 Hz; Perry & Burnfield pentru ROM max ~30-40°).
  - ✍️ *Text propus:* Filtrul low-pass Butterworth de ordin 4 cu cutoff 6 Hz aplicat pe unghiul gleznei urmează recomandarea clinică Winter (1991) pentru kinematica mersului, iar clippingul la ±35° respinge artefactele IMU mai mari decât ROM-ul fiziologic al gleznei (Perry & Burnfield: ~30° la mers plat, până la ~40° la coborârea scărilor).
- **[scazuta]** SD-ul folosește ddof=1 (deviație standard de eșantion), nu de populație — detaliu metodologic relevant pentru reproductibilitate, nemenționat în text.
  - ✍️ *Text propus:* Deviația standard a duratei stride și a procentelor stance/swing se calculează cu ddof=1 (estimator de eșantion, nepărtinitor), aplicabil doar când există cel puțin două cicluri; în caz contrar SD este 0.
- **[medie]** Calitatea reală a unghiului IMU vs. OMC nu e menționată în secțiunea 4.8, deși rezultatele (tab04) arată că unghiul derivat din IMU (compute_ankle_angle) corelează pozitiv și bine cu OMC (PCC 0.652, RMSE 8.75°), spre deosebire de traiectoria FSM (PCC -0.244). Aceasta validează empiric tocmai funcția descrisă în AF-4.72/4.73.
  - ✍️ *Text propus:* Validarea pe cele 290 de probe Samala (tab04) confirmă calitatea unghiului derivat din IMU prin compute_ankle_angle: corelație Pearson medie +0,652 (median 0,65) și RMSE 8,75° față de referința optică OMC — net superioară traiectoriei comandate de FSM (PCC -0,244, RMSE 13,72°). Acest rezultat susține empiric convenția dorsi+/plantar- și calibrarea adoptate în secțiunea 4.8.

---

### WU-IV-05 — 4.11 FSM control gleznei (5 stari, setpoints, PCHIP, timeout)

*Sub-sectiunea 4.11 este in mare parte SOLIDA: descrierile arhitecturii FSM cu 5 stari, ale pragurilor de tranzitie (foot-flat 30 grade/s, push-off 3 grade / 45%, timeout 1.5x), ale setpoint-urilor (TABEL 4.1 — toate cele 25 de valori corecte) si ale interpolarii PCHIP (waypoint 0.30) corespund EXACT codului din fsm.py si ankle_controller.py. Figura mentionata (fig11_overlay_S01_W1_right) exista si reflecta fidel rezultatele. Doua corecturi necesare, ambele de severitate medie: (1) AF-4.92 — afirmatia 'daca HS lipseste se forteaza S1' este inexacta: timeout-ul forteaza tranzitii INAINTE (S1->S2 etc.), iar S1 se atinge doar pe eveniment HS; (2) AF-4.90 — referinta interna 'Capitolul IX' este eronata (lucrarea are doar capitolele I-V; corect ar fi Capitolul V), iar relatia theta_observed=theta_eq+M/K este un model teoretic, nu o formula implementata. Discrepanta cod/docstring de la push-off (+8 vs 3 grade) NU afecteaza capitolul, care raporteaza corect 3 grade. LACUNA cea mai importanta (importanta ridicata) este absenta discutiei despre PCC negativ al FSM (-0.244) vs PCC pozitiv al IMU (+0.652) — limitarea-cheie a abordarii, recunoscuta explicit in cod si care trebuie inclusa pentru onestitate stiintifica. Recomand: corectarea celor doua afirmatii imprecise, corectarea referintei de capitol si adaugarea paragrafului despre superioritatea estimarii IMU vs comanda FSM de impedanta.*

#### Verdicte pe afirmații

**⚪ AF-4.83 — NEVERIFICABIL 🟢**  
Protezele active (BiOM/Empower, Vanderbilt, SpringActive) folosesc FSM alimentata de IMU: plantarflexie activa push-off, dorsiflexie swing, echilibru neutru mid-stance.  
📎 *Dovadă:* `fsm.py:3 citeaza Au & Herr 2008, Sup 2008, Eilenberg 2010, Bartlett 2021; ankle_controller.py:3,10-12 (BiOM/Vanderbilt/SpringActive)`  
💬 Afirmatie de literatura externa despre proteze comerciale reale, nu despre implementarea proprie. Codul citeaza aceleasi surse (fsm.py:3, ankle_controller.py:3,10-12), dar adevarul afirmatiei nu poate fi confirmat din cod/rezultate. Observatie de nuanta: comentariul din cod (fsm.py:46-48) precizeaza ca in controllere reale stance e controlat prin impedanta, NU prin trajectory tracking de pozitie — deci formularea 'echilibru neutru mid-stance' este imprecisa: setpoint-ul mid-stance comandat e -15 grade (plantarflexie), nu neutru.

**✅ AF-4.84 — CONFIRMAT**  
Implementarea reproduce arhitectura FSM cu 5 stari, traiectorie de referinta per sample IMU.  
📎 *Dovadă:* `fsm.py:28-33 (AnkleState IntEnum S1..S5); fsm.py:170 (bucla 'for i in range(n_samples)' = per sample); fsm.py:229-230 (state_per[i], setp_per[i] per sample); ankle_controller.py:94-95 (traj la fiecare sample t_all=np.arange(n))`  
💬 FSM are exact 5 stari (S1_LOADING..S5_LATE_SWING) si ruleaza cauzal sample-cu-sample, producand stare + setpoint + traiectorie continua per sample. Confirmat integral.

**✅ AF-4.85 — CONFIRMAT**  
S1 Loading: trigger HS; setpoint level -8 grade.  
📎 *Dovadă:* `fsm.py:173-175 ('if i in hs_set: new_state = AnkleState.S1_LOADING'); fsm.py:55 (S1_LOADING: -8.0 pentru 'level')`  
💬 HS forteaza S1_LOADING, iar setpoint-ul level pentru S1 este exact -8.0 grade. Confirmat.

**✅ AF-4.86 — CONFIRMAT 🟢**  
S2 Mid-Stance: trigger foot-flat (|omega_shank|<30 grade/s timp de 50 ms); setpoint -15 grade; 50ms doar la fs=200Hz.  
📎 *Dovadă:* `fsm.py:99 (foot_flat_omega_thr_dps=30.0); fsm.py:100 (foot_flat_min_samples=10, comentariu '50 ms @ 200 Hz'); fsm.py:181-185 (abs(omega)<thr -> ff_counter, >=min_samples -> S2); fsm.py:56 (S2_MIDSTANCE: -15.0)`  
💬 Pragul de 30 grade/s, durata de 10 esantioane si setpoint-ul -15 grade sunt confirmate exact. Cei 50 ms sunt corecti DOAR la fs=200 Hz (10/200=0.05s); pentru Wassall fs=100 Hz aceleasi 10 esantioane = 100 ms. Codul foloseste un numar fix de esantioane (nu un timp absolut), deci durata in ms depinde de fs. Afirmatia e corecta pentru contextul Samala (200 Hz) care e cazul validat, dar ar trebui semnalat ca durata e definita in esantioane.

**✅ AF-4.87 — CONFIRMAT**  
S3 Push-Off: trigger dorsiflexie >3 grade SAU 45% din stride mediana; setpoint -25 grade (Sup 2008 Mode 2); discrepanta docstring +8 grade.  
📎 *Dovadă:* `fsm.py:101 (pushoff_dorsi_thr_deg=3.0, comentariu 'relaxat de la 8 grade'); fsm.py:105 (pushoff_phase_fraction=0.45); fsm.py:199 (ankle_angle>cfg.pushoff_dorsi_thr_deg); fsm.py:201 (trigger_timeout > 0.45*median_stride); fsm.py:57 (S3_PUSHOFF: -25.0). Discrepanta: docstring fsm.py:6 'S3 Push-Off <- dorsiflexie > +8 grade'`  
💬 Pragul real in cod este 3.0 grade (pushoff_dorsi_thr_deg), fallback la 45% din median stride, setpoint -25 grade. Toate confirmate. Discrepanta interna cod/docstring confirmata: docstring (fsm.py:6) inca spune +8 grade, dar valoarea efectiva este 3.0. Capitolul descrie corect valoarea reala (3 grade), deci afirmatia din lucrare este corecta; eroarea e in docstring-ul codului, nu in capitol.

**✅ AF-4.88 — CONFIRMAT**  
S4 Early Swing: trigger TO; setpoint -5 grade.  
📎 *Dovadă:* `fsm.py:176-177 ('elif i in to_set: new_state = AnkleState.S4_EARLY_SWING'); fsm.py:58 (S4_EARLY_SWING: -5.0)`  
💬 TO forteaza S4_EARLY_SWING (prioritate peste logica de stare), iar setpoint-ul level este exact -5.0 grade. Confirmat.

**✅ AF-4.89 — CONFIRMAT**  
S5 Late Swing: trigger peak omega shank (mid-swing); setpoint -3 grade.  
📎 *Dovadă:* `fsm.py:210-218 (S4->S5: peak local omega in fereastra midswing [0.15,0.35]s post-TO: omega[i-1]>omega[i] si omega[i-1]>0); fsm.py:59 (S5_LATE_SWING: -3.0)`  
💬 Tranzitia la S5 se face pe peak local de omega (mid-swing, fereastra 0.15-0.35s dupa TO) sau pe expirarea ferestrei, iar setpoint-ul level este -3.0 grade. Confirmat.

**🟡 AF-4.90 — PARTIAL 🟠**  
Setpoints = echilibre virtuale impedanta theta_eq; theta_observed = theta_eq + M_GRF/K; refera 'Capitolul IX'.  
📎 *Dovadă:* `fsm.py:36-37 ('interpretate ca echilibre virtuale de impedanta (impedance equilibrium theta_eq), nu ca unghiuri observate fiziologic'); fsm.py:44-48 (convenție impedance-style). Relatia exacta theta_observed=theta_eq+M/K NU apare in cod.`  
💬 Partea conceptuala (setpoints = echilibre virtuale theta_eq de impedanta) este confirmata explicit in cod (fsm.py:36-48). Relatia algebrica theta_observed=theta_eq+M_GRF/K nu este implementata/scrisa in cod — e o interpretare teoretica (corecta ca model de impedanta, dar neverificabila din implementare). Referinta interna 'Capitolul IX' este aproape sigur eronata: lucrarea are capitole I-V (acesta este capitolul 4.x = IV), deci o trimitere la 'Capitolul IX' nu poate exista. Probabil ar trebui 'Capitolul V' (sau alt capitol existent). Marcheaza ca eroare de referinta interna.

**✅ AF-4.91 — CONFIRMAT**  
PCHIP (PchipInterpolator scipy), waypoint 30% din durata starii, garanteaza monotonia, evita overshoot; waypoint_position=0.30.  
📎 *Dovadă:* `ankle_controller.py:21 (from scipy.interpolate import PchipInterpolator); ankle_controller.py:31 (waypoint_position: float = 0.30); ankle_controller.py:73-74 (x = s + waypoint_position*(e-s)); ankle_controller.py:93 (PchipInterpolator(...,extrapolate=True)); ankle_controller.py:5-7,40 (garanteaza monotonia, fara overshoot); ankle_controller.py:15-16 (versiunea anterioara CubicHermiteSpline producea overshoot pana la 22 grade)`  
💬 PchipInterpolator din scipy, waypoint la 30% din durata starii (waypoint_position=0.30), proprietatea de monotonie/no-overshoot — toate confirmate exact in cod. Confirmat integral.

**🟡 AF-4.92 — PARTIAL 🟠**  
Timeout pe stare (1.5x durata mediana stride). Daca HS lipseste, forteaza S1 (Varol 2010).  
📎 *Dovadă:* `fsm.py:107 (max_dwell_factor=1.5); fsm.py:154 (max_dwell = max(int(1.5*median_stride), int(0.3*fs))); fsm.py:151 (median_stride=median(diff(hs_idx))); fsm.py:173-174 (HS event -> S1_LOADING); fsm.py:188-189 (in S1: timeout -> S2_MIDSTANCE)`  
💬 Timeout absolut = 1.5*median_stride: CONFIRMAT (max_dwell_factor=1.5, fsm.py:107,154). Insa afirmatia 'daca HS lipseste, forteaza S1' este INEXACTA pentru logica reala: S1_LOADING este fortat DOAR de un eveniment HS efectiv detectat (fsm.py:173-174). max_dwell (1.5x) este folosit numai in S1 ca timeout care duce inainte la S2_MIDSTANCE (fsm.py:188-189), NU inapoi la S1. Restul starilor au timeout-uri proprii care avanseaza FSM (S2->S3 la 0.45*median, S3->S4 la 0.3*median, S4->S5 la 0.35s) — toate forteaza inainte, nu spre S1. Deci timeout-ul NU 'forteaza S1' nicaieri; FSM revine la S1 exclusiv pe HS. Formularea trebuie corectata: timeout-ul realizeaza progresia robusta intre stari cand evenimentul asteptat lipseste, iar HS (cand exista) reseteaza ciclul la S1.

#### Figuri / tabele

| Referință | Există | Sursă | Observații |
| --- | --- | --- | --- |
| Fig 4.11.3.1 OMC vs IMU vs FSM S01 W1 RIGHT | da | `easy-gait/notebooks/figs/fig11_overlay_S01_W1_right.png` | Fisierul exista: fig11_overlay_S01_W1_right.png. Generat de 04_fsm_validation.py:132-173,195 (fig_overlay 'S01',1,'right'). Figura afiseaza trei curbe: OMC (negru, referinta), IMU compute_ankle_angle (verde) si FSM comandat theta_eq impedance (rosu intrerupt). Imaginea confirma vizual rezultatele numerice: curba FSM (rosie) este in plantarflexie aproape tot timpul si in antifaza cu OMC (PCC negativ), in timp ce curba IMU (verde) urmareste forma OMC (PCC pozitiv). Numele descris in capitol ('Fig 4.11.3.1') nu e numele fisierului (fig11), dar continutul corespunde exact. Atentie: in notebook (04_fsm_validation.py:194) latura right e comentata ca 'intact', deci RIGHT este latura intacta, nu protetica — de verificat coerenta cu textul. |
| TABEL 4.1 — setpoints per activitate (level/stair_asc/stair_desc/slope_up/slope_down) | da | `easy-gait/src/easy_gait/fsm.py:52-93` | Toate valorile din TABEL 4.1 corespund EXACT cu SETPOINTS din fsm.py:52-93. Level S1..S5: -8,-15,-25,-5,-3 (fsm.py:55-59) OK. Stair Asc (cheie 'stair_ascent'): -3,-8,-18,-3,0 (fsm.py:63-67) OK. Stair Desc ('stair_descent'): -15,-20,-30,-15,-8 (fsm.py:71-75) OK. Slope Up ('slope_ascent'): -5,-12,-22,-3,-1 (fsm.py:79-83) OK. Slope Down ('slope_descent'): -12,-18,-28,-10,-5 (fsm.py:87-91) OK. Toate cele 25 de valori se potrivesc. |

#### ✏️ Corecturi de redactare propuse

**AF-4.90**  
- ❌ Original: *Setpoints = echilibre virtuale impedanta theta_eq. theta_observed = theta_eq + M_GRF/K. Refera 'Capitolul IX'.*
- ✅ Corectat: **Setpoint-urile reprezinta echilibre virtuale de impedanta (theta_eq), nu unghiuri cinematice observate; conform modelului de impedanta, unghiul efectiv rezulta din echilibrul virtual ajustat de cuplul de reactie la sol fata de stiffness (theta_observed = theta_eq + M_GRF/K). Pentru detalii privind controlul prin impedanta, vezi Capitolul V (NU 'Capitolul IX' — lucrarea contine doar capitolele I-V).**

**AF-4.92**  
- ❌ Original: *Timeout pe stare (1.5x durata mediana stride). Daca HS lipseste, forteaza S1 (Varol 2010).*
- ✅ Corectat: **FSM include un mecanism de toleranta la erori prin timeout, definit ca 1,5 x durata mediana a stride-ului (max_dwell_factor=1.5). Cand evenimentul asteptat intr-o stare nu apare in acest interval, FSM forteaza tranzitia INAINTE catre starea urmatoare (de ex. din S1 Loading catre S2 Mid-Stance la depasirea max_dwell), asigurand progresia robusta a ciclului fara blocaje (Varol, Sup & Goldfarb 2010). Revenirea la S1 Loading se face exclusiv la detectia unui eveniment HS, care reseteaza ciclul; nu prin timeout.**

**AF-4.83**  
- ❌ Original: *...echilibru neutru mid-stance.*
- ✅ Corectat: **...iar in mid-stance comanda de impedanta mentine echilibrul virtual al gleznei (in implementarea proprie, setpoint-ul mid-stance este -15 grade, plantarflexie, conform conventiei de impedanta theta_eq — nu o pozitie neutra observata).**

#### 📌 Lacune — ce ar trebui adăugat

- **[ridicata]** Capitolul nu mentioneaza ca FSM (traiectoria comandata theta_eq) coreleaza NEGATIV cu OMC (PCC mediu -0.244, RMSE 13.72 grade), in timp ce unghiul derivat direct din IMU este net superior (PCC +0.652, RMSE 8.75 grade). Aceasta este limitarea cea mai importanta a abordarii FSM, recunoscuta explicit in cod (fsm.py:44-48) si in notebook (04_fsm_validation.py:12-16).
  - ✍️ *Text propus:* Trebuie subliniat ca traiectoria comandata de FSM reprezinta echilibre virtuale de impedanta (theta_eq), nu o estimare a unghiului articular fiziologic. In consecinta, comparatia directa FSM vs. referinta optica OMC produce metrici slabe: RMSE 13,72 grade (+/-4,93), NRMSE 0,868 si o corelatie Pearson medie NEGATIVA de -0,244 (mediana -0,224), iar amplitudinea comandata (ROM 14,6 grade) este sub cea observata OMC (22,9 grade). Prin contrast, unghiul gleznei estimat direct din IMU (compute_ankle_angle) urmareste mult mai fidel referinta OMC: RMSE 8,75 grade, NRMSE 0,529 si PCC mediu pozitiv +0,652. Aceasta confirma ca obiectivul FSM nu este reproducerea cinematicii observate, ci comanda de impedanta — comparatia RMSE/PCC fata de unghiul articular OMC fiind conceptual nepotrivita pentru evaluarea controlului.
- **[medie]** Nu se mentioneaza ca durata foot-flat de 50 ms (AF-4.86) este definita ca numar FIX de esantioane (foot_flat_min_samples=10), deci echivalentul in milisecunde depinde de fs: 50 ms la 200 Hz (Samala), dar 100 ms la 100 Hz (Wassall).
  - ✍️ *Text propus:* Pragul de foot-flat este definit ca numar fix de esantioane consecutive (foot_flat_min_samples = 10) sub care |omega_shank| < 30 grade/s. La frecventa de esantionare Samala (200 Hz) acesta corespunde la 50 ms; la 100 Hz (Wassall) acelasi numar de esantioane corespunde la 100 ms. Aceasta dependenta de frecventa trebuie avuta in vedere la portarea FSM pe semnale cu fs diferit.
- **[scazuta]** Capitolul nu mentioneaza min_dwell-ul de 20% din median_stride impus inainte de tranzitia S2->S3, mecanism care evita tranzitii instantanee S1->S2->S3 (fsm.py:195-196).
  - ✍️ *Text propus:* Pentru a evita tranzitii instantanee S1->S2->S3 (care apar cand foot-flat este detectat foarte rapid dupa HS), FSM impune un timp minim de stationare in S2 (min_dwell) de 20% din durata mediana a stride-ului inainte de a permite trecerea la Push-Off (fsm.py:195-196).
- **[medie]** Setpoint-urile FSM (inclusiv level: S1..S5) sunt monoton descrescatoare in stance (de la -8 la -25 grade) si TOATE in plantarflexie; capitolul nu explica de ce nu apare dorsiflexie pozitiva, desi fiziologic mid-stance ar fi usor dorsiflex.
  - ✍️ *Text propus:* Setpoint-urile pentru level walking formeaza o curba monoton descrescatoare in faza de sprijin (de la -8 grade in loading la -25 grade in push-off), toate in plantarflexie (negative). Aceasta este o consecinta directa a interpretarii impedance-style (Sup 2008, Tabel 5): valorile reprezinta echilibre virtuale theta_eq, nu unghiuri cinematice observate. Comentariul din implementare (fsm.py:44-48) precizeaza ca aceasta alegere elimina 'balansul' vizual care aparea cand se foloseau unghiuri fiziologice ca setpoints (ex. mid-stance +3 grade dorsi).

---

### WU-IV-06 — 4.12 Vizualizare + Dashboard (animatie proteza, 6 pagini Streamlit)

*Sub-sectiunea 4.12 este in mare parte corecta structural — toate cele 6 pagini Streamlit, animatia 2D, sliderele (fereastra 2-15 s, viteza 0.1x-2.0x) si butoanele Play/Pause exista exact cum sunt descrise (AF-4.96, AF-4.101, AF-4.102 CONFIRMATE). Eroarea cea mai grava este AF-4.94: textul afirma L_TIBIA = 0.33 m, dar codul real foloseste 0.40 m — cifra trebuie corectata. In plus, referinta 'bench-test MTS-type (Hansen/Childress/Knox 2004)' exista doar in documentatia PDF, nu in cod, deci e o atribuire de model care nu se reflecta in implementare. Mai multe afirmatii despre paginile individuale (AF-4.97 'alegere coloane', AF-4.98 'peste shank pitch' in loc de omega, AF-4.99 'Symmetry Index' neafisat, AF-4.100 'stari colorate'/'plot dublu') sunt imprecise si necesita reformulari minore. AF-4.93 si AF-4.95 sunt corecte (inclusiv SWING_LIFT=6 cm si fereastra de blend 80 ms / 5 cadre). Recomandare urgenta: corectati L_TIBIA la 0.40 m si verificati daca referinta Hansen 2004 trebuie pastrata sau retrasa, deoarece nu corespunde implementarii reale (care e un model geometric ad-hoc, nu un roll-over shape din literatura)."*

#### Verdicte pe afirmații

**✅ AF-4.93 — CONFIRMAT**  
Animatie 2D sagitala a componentei protetice (pilon + glezna + talpa).  
📎 *Dovadă:* `easy-gait/src/easy_gait/prosthesis_viz.py:1 (titlu modul 'Vizualizare animata 2D ... vedere sagitala'); compute_segments returneaza 'ankle','knee','toe','heel','foot_poly' (linii 188-196); build_animation_figure deseneaza Tibia (l.269-273), Talpa (l.274-280), Gleznă marker (l.281-286), Genunchi marker (l.287-292).`  
💬 Codul construieste exact o vizualizare 2D in plan sagital cu pilon (tibie), glezna, talpa si genunchi. Afirmatia mentioneaza 'pilon + glezna + talpa', toate prezente; in plus exista si genunchiul (in plus, nu contradictie).

**❌ AF-4.94 — CONTRAZIS 🟠** 🔁²  
Model bench-test MTS (Hansen/Childress/Knox 2004); Tibia L_TIBIA=0.33 m, unghi fix +7 grade, talpa roteste exact fara scalare.  
📎 *Dovadă:* `easy-gait/src/easy_gait/prosthesis_viz.py:36 → L_TIBIA = 0.40 (NU 0.33); l.41 PYLON_TILT_DEG = 7.0; l.26-28 + l.139 'talpa roteste cu unghiul EXACT din date ... fara scaling'. Referinta Hansen/Childress/Knox 2004 NU apare in cod, doar in generatorul PDF (scripts/generate_documentation_pdf.py:826-827) care nu e sursa de adevar.`  
💬 Valoarea L_TIBIA din text (0.33 m) contrazice codul real (0.40 m). PYLON_TILT_DEG=7.0 si rotirea exacta fara scalare sunt corecte. Referinta 'bench-test MTS-type (Hansen, Childress, Knox 2004)' nu are corespondent in cod (apare doar in PDF/documentatie, care e explicatie nu sursa). Cifra 0.33 e gresita.  ⟶ [CONFIRMAT și de al 2-lea verificator: Am incercat sa refut constatarea, dar dovada independenta o confirma fara echivoc. easy-gait/src/easy_gait/prosthesis_viz.py:36 → L_TIBIA = 0.40 (NU 0.33); l.41 → PYLON_TILT_DEG = 7.0 (corect); docstring l.12-14 si l.26-28 → 'talpa roteste cu unghiul EXACT din date (FSM/IMU, fara scaling)' (corect). Cautarea pe tot src/ nu gaseste niciun 0.33 (singurele aparitii de 0.33 sunt valori de date fara legatura in data/processed/*.csv). Referinta 'bench-test MTS-type (Hansen, Childress & Knox 2004)' apare DOAR in scripts/generate_documentation_pdf.py:826-827 (generator PDF = explicatie, nu sursa de adevar) si in PDF-ul binar. Decisiv: chiar si PDF-ul, la l.830, scrie 'L_TIBIA = 0.40 m' — deci 0.33 nu e sustinut nici macar de documentatie. Nu exista nicio interpretare rezonabila in care 0.33 sa fie corect; valoarea reala e 0.40 m.]

**✅ AF-4.95 — CONFIRMAT**  
Stance (S1+S2+S3) cel mai jos punct talpa pe sol; Swing (S4+S5) glezna se ridica 6 cm; interpolare pozitie pe 80 ms (5 cadre la 60 fps).  
📎 *Dovadă:* `prosthesis_viz.py:64 _STANCE_STATES={1,2,3}; l.138-161 _stance_geometry translateaza vertical ca 'cel mai jos punct al poligonului sa fie la y=0' (l.153-155); l.62 SWING_LIFT=0.06 (6 cm); l.164-168 _swing_geometry ridica glezna cu SWING_LIFT; l.240 blend_win=max(int(0.08*resample_hz),3) → la 60 fps int(4.8)=4, fortat impar (l.241-242) → 5 cadre ≈ 0.08 s (80 ms).`  
💬 Toate cele patru detalii sunt corecte: stari stance {1,2,3}, cel mai jos punct pe sol, ridicare swing 0.06 m=6 cm, fereastra de blend 0.08 s=80 ms care la 60 fps da 5 cadre (4.8→5 impar). Singura subtilitate: 5 cadre/60 fps = 83 ms efectiv, dar constanta de proiectare e 0.08 s=80 ms — afirmatia e corecta.

**✅ AF-4.96 — CONFIRMAT**  
Multi-page Streamlit: app.py landing, pages/ pagini, _shared.py functii cached @st.cache_data.  
📎 *Dovadă:* `easy-gait/dashboard/app.py:67-78 (st.navigation cu st.Page home 'Acasă' default + 6 pagini din PAGES_DIR); _shared.py:11,17,23,31 — patru functii decorate @st.cache_data (list_samala_subjects_cached, list_wassall_participants_cached, load_samala_imu_cached, load_wassall_trial_cached).`  
💬 app.py este landing-ul/routerul (functia home + st.navigation), pages/ contine paginile, _shared.py expune functii cached cu @st.cache_data. Toate elementele afirmate sunt verificate in cod.

**🟡 AF-4.97 — PARTIAL 🟢**  
Pagina 1 Signal Explorer: semnale IMU brute, alegere subiect/trial/lateralitate/coloane, Plotly.  
📎 *Dovadă:* `dashboard/pages/1_Explorare_semnale.py:21 header('Explorare semnale'); selectoare subiect (l.36), proba/trial (l.37), picior/lateralitate (l.43-46), slider cutoff filtru (l.47); grafice Plotly go.Figure (l.64-101). NU exista selector de 'coloane' arbitrare — semnalele afisate sunt fixe (shank pitch, omega, acceleratii, unghi glezna).`  
💬 Pagina afiseaza semnale IMU brute+filtrate cu Plotly si permite alegerea subiect/trial/lateralitate — corect. Insa NU are 'alegere coloane'; in loc, ofera un slider de frecventa de taiere. Afirmatia 'alegere ... coloane' e imprecisa: nu se pot alege coloane, semnalele sunt predefinite (4 grafice fixe).

**🟡 AF-4.98 — PARTIAL 🟢**  
Pagina 2 Gait Events: HS/TO Trojaniello+Maqbool peste shank pitch, markeri rosu HS albastru TO.  
📎 *Dovadă:* `dashboard/pages/2_Detectie_evenimente.py:33 selectbox Algoritm ['Trojaniello','Maqbool']; l.48-51 ambele metode; l.61-64 HS marker color='red'; l.65-68 TO marker color='blue'. DAR axa Y / semnalul de fundal este OMEGA (viteza unghiulara, gyro_pitch_dps l.44), NU shank pitch — l.60 'name=viteza unghiulara gamba', l.71 yaxis 'Viteză unghiulară gambă'.`  
💬 HS rosu / TO albastru si ambii algoritmi sunt corecti. Insa markerii sunt suprapusi peste VITEZA UNGHIULARA a gambei (omega, °/s), nu peste 'shank pitch' (unghi de inclinare). Afirmatia 'peste shank pitch' e inexacta — graficul foloseste omega derivat din pitch.

**🟡 AF-4.99 — PARTIAL 🟠**  
Pagina 3 Parameters: tabel cadenta/stride/stance%/CV, Symmetry Index protetic vs intact.  
📎 *Dovadă:* `dashboard/pages/3_Parametri_temporali.py:38-43 coloane cadenta, stride mean/std, stride CV, stance mean/std; l.119-127 sumar protetic vs intact (groupby 'role'). NU se calculeaza/afiseaza explicit Symmetry Index (Robinson) — parameters.symmetry_index nu e apelat in pagina; comparatia protetic vs intact se face prin medii separate, nu prin SI.`  
💬 Tabelul de cadenta/stride/stance%/CV exista, iar comparatia protetic vs intact exista (agregare per rol). Dar 'Symmetry Index' ca metrica nu e calculat in aceasta pagina — afirmatia ca pagina afiseaza Symmetry Index este neconfirmata in cod. Comparatia e facuta cu medii pe rol, nu cu SI Robinson.

**🟡 AF-4.100 — PARTIAL 🟢**  
Pagina 4 FSM Simulator: stari FSM, plot dublu traiectorie PCHIP vs unghi IMU + stari colorate.  
📎 *Dovadă:* `dashboard/pages/4_Simulator_FSM.py:60 generate_trajectory (PCHIP din ankle_controller); l.73-98 subplots cu 3 randuri: faza FSM (l.80-83), tinta+traiectorie (l.85-88), unghi real vs comandat (l.90-93). Traiectoria e plotata cu o singura culoare 'darkorange' (l.88,93); fazele FSM sunt afisate ca linie 'purple shape=hv' (l.80) — NU exista colorare per-stare a curbei in aceasta pagina (colorarea per-stare exista doar in pagina 6 / fig12).`  
💬 Pagina compara traiectoria PCHIP cu unghiul real masurat (din IMU, compute_ankle_angle) si afiseaza fazele FSM — corect ca 'plot dublu traiectorie vs unghi'. Insa 'stari colorate' nu se aplica curbei (fazele sunt o linie purple in step); afirmatia ca starile sunt colorate in pagina 4 e imprecisa. Subplot-ul are de fapt 3 randuri, nu doar 'plot dublu'.

**✅ AF-4.101 — CONFIRMAT**  
Pagina 5 Activity Compare: parametri Wassall per teren, boxplots cu/fara baston.  
📎 *Dovadă:* `dashboard/pages/5_Comparatie_activitati.py:19 header('Comparație activități'); l.33-55 proceseaza probe Wassall, mapeaza terenul (plat/scari/panta/iarba/pietris/denivelat); l.85-95 px.box pe teren cu color='walkaid' (mijloc de sprijin = cu/fara baston); l.124-126 boxplot lot complet.`  
💬 Pagina afiseaza parametri Wassall (cadenta, stance%, stride) per teren ca boxplots, cu separare dupa walkaid (baston). Toate elementele afirmate sunt prezente.

**✅ AF-4.102 — CONFIRMAT**  
Pagina 6 Prosthesis Simulator: animatie 2D, selectoare, slider fereastra 2-15s, slider viteza 0.1x-2.0x, Play/Pause, plot dublu.  
📎 *Dovadă:* `dashboard/pages/6_Simulator_proteza.py:75 slider fereastra 2.0..min(15.0,...) step 0.5; l.87-92 select_slider viteza options=[0.1,0.25,0.5,0.75,1.0,1.5,2.0]; l.111-115 build_animation_figure (animatie 2D); prosthesis_viz.py:318-334 butoane Play/Pause; pagina are selectoare subiect/trial/activitate/sursa unghi (l.28-37) si plot dublu sincron (make_subplots 2 randuri l.120-151).`  
💬 Toate elementele sunt verificate: animatie 2D, selectoare multiple, slider fereastra 2-15 s, slider viteza cu extreme 0.1x si 2.0x, butoane Play/Pause (in build_animation_figure), si plot dublu sincronizat (unghi + faza). Afirmatia este complet sustinuta de cod.

#### Figuri / tabele

| Referință | Există | Sursă | Observații |
| --- | --- | --- | --- |
| fig12_prosthesis_phases.png | da | `easy-gait/notebooks/figs/fig12_prosthesis_phases.png` | Figura exista si afiseaza cele 5 faze FSM ale simulatorului proteza (S01 W1 LEFT, picior protetic): S1 θ=-9.2 grade, S2 θ=-17.0 grade, S3 θ=-23.3 grade, S4 θ=-4.8 grade, S5 θ=-3.3 grade. Valorile sunt toate plantarflexie (negative) si corespund logicii FSM/setpoints level din cod (S1=-8,S2=-15,S3=-25,S4=-5,S5=-3 sunt setpoint-urile; valorile afisate sunt unghiuri de traiectorie reale apropiate). Geometria tibie rigida oblica + talpa pivotanta + glezna pe sol corespunde prosthesis_viz.py. Coerenta cu codul. |

#### ✏️ Corecturi de redactare propuse

**AF-4.94**  
- ❌ Original: *Model bench-test MTS-type (Hansen, Childress, Knox 2004). Tibia LTIBIA = 0.33 m, unghi fix +7 grade. Talpa roteste dupa unghiul exact din date, fara scalare.*
- ✅ Corectat: **Modelul vizual foloseste o tibie (pilon) rigida cu lungime fixa L_TIBIA = 0.40 m si inclinare oblica constanta de +7 grade (PYLON_TILT_DEG = 7.0). Talpa pivoteaza dupa unghiul exact din date (FSM sau IMU), fara nicio scalare sau limitare a unghiului.**

**AF-4.97**  
- ❌ Original: *Pagina 1 Signal Explorer: semnale IMU brute, alegere subiect/trial/lateralitate/coloane, Plotly.*
- ✅ Corectat: **Pagina 1 (Explorare semnale): afiseaza cu Plotly semnalele IMU brute si filtrate pentru o proba aleasa — inclinarea gambei, viteza unghiulara, acceleratiile si unghiul gleznei. Utilizatorul alege setul de date (Samala/Wassall), subiectul/participantul, proba si lateralitatea piciorului, plus frecventa de taiere a filtrului; semnalele afisate sunt predefinite, nu se aleg coloane arbitrare.**

**AF-4.98**  
- ❌ Original: *Pagina 2 Gait Events: HS/TO Trojaniello+Maqbool peste shank pitch, markeri rosu HS albastru TO.*
- ✅ Corectat: **Pagina 2 (Detectie evenimente): afiseaza evenimentele HS/TO detectate cu Trojaniello sau Maqbool, suprapuse peste viteza unghiulara a gambei (omega, derivata din inclinarea gambei), cu markeri rosii pentru contactul calcaiului (HS) si albastri pentru desprindere (TO).**

**AF-4.99**  
- ❌ Original: *Pagina 3 Parameters: tabel cadenta/stride/stance%/CV, Symmetry Index protetic vs intact.*
- ✅ Corectat: **Pagina 3 (Parametri temporali): tabel cu cadenta, durata de pas (medie/abatere), variabilitatea pasului (CV) si procentul de sprijin, plus un sumar comparativ intre piciorul protetic si cel intact (medii agregate pe rol). Indicele de simetrie Robinson este definit in modulul parameters.py, dar nu este afisat in aceasta pagina.**

**AF-4.100**  
- ❌ Original: *Pagina 4 FSM Simulator: stari FSM, plot dublu traiectorie PCHIP vs unghi IMU + stari colorate.*
- ✅ Corectat: **Pagina 4 (Simulator FSM): afiseaza, pe trei sub-grafice sincronizate, faza FSM in timp, unghiul-tinta pe faze impreuna cu traiectoria PCHIP netezita, si comparatia dintre unghiul comandat (traiectoria PCHIP) si unghiul real masurat din IMU. Sunt afisate si metricile RMSE/NRMSE/PCC fata de unghiul real.**

#### 📌 Lacune — ce ar trebui adăugat

- **[medie]** Capitolul nu mentioneaza ca animatia foloseste o tibie RIGIDA cu lungime si unghi constante (genunchiul si glezna culiseaza doar pe verticala, pastrand vectorul tibial fix) — ipoteza de modelare centrala a vizualizarii.
  - 📎 `easy-gait/src/easy_gait/prosthesis_viz.py:36,41,49-59`
  - ✍️ *Text propus:* In modelul vizual, tibia (pilonul) este tratata ca un segment rigid de lungime fixa (L_TIBIA = 0.40 m) si inclinare oblica constanta (PYLON_TILT_DEG = +7 grade fata de verticala). Genunchiul si glezna se deplaseaza exclusiv pe verticala, urcand si coborand impreuna astfel incat vectorul tibial sa ramana constant; doar talpa pivoteaza in jurul gleznei dupa unghiul comandat sau masurat.
- **[medie]** Nu se mentioneaza ca animatia poate fi alimentata din DOUA surse de unghi (traiectoria FSM comandata SAU unghiul real masurat din IMU), selectabile de utilizator — element esential dat fiind ca FSM coreleaza negativ cu OMC.
  - 📎 `easy-gait/dashboard/pages/6_Simulator_proteza.py:33-37,67-72; tab04_fsm_validation_summary.csv`
  - ✍️ *Text propus:* Simulatorul de proteza (pagina 6) permite alegerea sursei unghiului de glezna: fie traiectoria comandata de controlul FSM ('Unghi comandat'), fie unghiul articular real estimat din IMU ('Unghi real masurat'). Aceasta optiune permite compararea vizuala directa intre comanda FSM si miscarea fiziologica masurata, relevanta deoarece traiectoria FSM coreleaza negativ cu referinta optica (PCC mediu -0.244), pe cand unghiul IMU coreleaza pozitiv (PCC 0.652).
- **[medie]** Capitolul nu mentioneaza ca dashboard-ul recalculeaza metricile LIVE (nu citeste CSV-urile de validare pre-calculate) si ca pagina 4 afiseaza tinte din literatura (RMSE<5 grade Bartlett 2021, NRMSE<15%, PCC>0.90) care nu sunt atinse de FSM-ul real.
  - 📎 `easy-gait/dashboard/pages/4_Simulator_FSM.py:64-70; _shared.py:11-35`
  - ✍️ *Text propus:* Toate paginile dashboard-ului recalculeaza metricile in timp real din datele brute, nu citesc tabelele de validare pre-calculate. Pagina 4 (Simulator FSM) afiseaza pe langa valorile calculate si tintele de referinta din literatura (RMSE < 5 grade dupa Bartlett 2021, NRMSE < 15%, PCC > 0.90); in practica, controlul FSM nu atinge aceste tinte (RMSE real ~13.7 grade, PCC mediu negativ -0.244), fapt vizibil direct in interfata.
- **[scazuta]** Nu se mentioneaza existenta variantei web Flask (demo-web) care replica functionalitatea, inclusiv animatia 2D pe canvas HTML cu Play/pauza/scrub si sliders proprii (fereastra 2-15s, viteza 0.25x-2x).
  - 📎 `demo-web/app/templates/prosthesis.html:34-49,87-253`
  - ✍️ *Text propus:* Pe langa dashboard-ul Streamlit exista si o varianta web independenta in Flask (demo-web) cu 7 pagini (home, signals, events, parameters, fsm, activities, prosthesis). Pagina de proteza din demo-web reimplementeaza animatia 2D direct pe un canvas HTML/JavaScript, cu butoane de redare/pauza, slider de derulare (scrub), fereastra reglabila (2-15 s) si viteza de redare (0.25x-2x).

---
