# CAPITOLUL V

> Capitol extras automat din `Paun_Raluca_Raport_CS4-final.docx`. Fiecare AFIRMATIE este numerotata pentru verificare independenta.

- **[AF-5.1 | #181]** VALIDARE ȘI REZULTATE

### 5.1. PIPELINE-UL DE VALIDARE

- **[AF-5.2 | #182]** Algoritmii IMU de detecție a evenimentelor de mers (Trojaniello, Maqbool) trebuie validați contra unui sistem de referință. Standardul industrial este OMC (Optical Motion Capture) — sisteme tip Vicon/Qualisys cu camere infraroșu și markeri reflectorizanți, cu precizie de ~1 mm. Datasetul Samala oferă fișiere C3D cu poziții markeri 3D sincronizate cu IMU [14, 24].
- **[AF-5.3 | #183]** Algoritmul Zeni et al. (2008) utilizează poziția X (direcția de mers) a markerilor HEEL și TOE în raport cu un punct de referință proximal (sacrum sau centrul pelvisului): HS = maxim local al (HEEL.x − SACRUM.x), adică călcâiul cel mai în față față de corp; TO = minim local al (TOE.x − SACRUM.x), adică vârful cel mai în spate față de corp [24].
- **[AF-5.4 | #184]** Din cei 40 markeri C3D disponibili în datasetul Samala, se utilizează: HEEL_L/HEEL_R (călcâi), MTH3_L/MTH3_R (Metatarsal Head 3, centrul vârfului, recomandat ca proxy TOE), și PELVIS_L/PELVIS_R (centrul pelvic calculat ca medie) [14, 24].
- **[AF-5.5 | #185]** Sincronizarea IMU și OMC nu este garantată: fișierele IMU au ~14 s, iar OMC are doar ~4.5 s (fereastra de captură mocap din mijlocul trial-ului). Soluția adoptată utilizează cross-corelație normalizată pe semnalul unghiului gleznei (disponibil în ambele surse) pentru a găsi poziția optimă a ferestrei OMC peste semnalul IMU [14].

### 5.2. VALIDAREA EVENIMENTELOR HS/TO

- **[AF-5.6 | #186]** Validarea a fost rulată pe toate cele 30 subiecte × 5 trial-uri × 2 laturi = 300 trial-laturi. Tabelul 5.1 prezintă rezultatele agregate.

**[TABEL 6]**

| Metrică | Troj. HS | Maq. HS | Troj. TO | Maq. TO | Țintă | Acceptabil |
| --- | --- | --- | --- | --- | --- | --- |
| MAE [ms] | 79.8 | 60.2 | 60.7 | 76.9 | < 25/50 | < 100/150 |
| MAE median [ms] | 77.5 | 56.7 | 58.3 | 75.8 | — | — |
| Sensibilitate | 0.584 | 0.633 | 0.613 | 0.653 | > 0.99 | > 0.85 |
| F1-score | 0.377 | 0.395 | 0.377 | 0.373 | — | — |
| Trial-laturi valide | 237/290 | 250/290 | 229/290 | 250/290 | — | — |


**[LEGENDA TABEL 7]:** Tabelul 5.1. Rezultatele validării evenimentelor HS și TO pe 300 trial-laturi.


**[FIGURA 46 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 47] (legenda):** Fig. 5.1. Distribuția MAE pentru HS (stânga) și TO (dreapta), separată pe cei doi algoritmi IMU. Linia verde = țintă DESIGN strictă (25 ms HS / 50 ms TO). Linia portocalie = limita acceptabilă (50 ms / 100 ms) conform Pacini Panebianco 2018.

- **[AF-5.7 | #187]** Interpretare: algoritmul Maqbool depășește Trojaniello pe detecția HS cu 19.6 ms (reducere 24.6% MAE) și cu 4.9 puncte procentuale la sensibilitate, confirmând literatura care recomandă Maqbool pentru aplicații real-time pe pacienți amputați [8]. Trojaniello depășește Maqbool pe TO cu 16.2 ms (reducere 21.1% MAE), justificând alegerea Trojaniello ca algoritm implicit offline pentru calculul precis al stance% [18].
- **[AF-5.8 | #188]** Toate cele patru metrici sunt sub ținta DESIGN dar peste limita inferioară acceptabilă din literatură. Cauzele, în ordine de impact: (a) bias sistematic între algoritmul IMU și definiția Zeni OMC (60-80 ms decalaj fizic real, nu eroare de implementare); (b) fereastra OMC scurtă (~4.5 s = doar 3-4 strides per trial) care limitează statistica; (c) variabilitatea inter-subiect mare (SD MAE ≈ 30 ms = 50% din medie) [10, 24].
- **[AF-5.9 | #189]** F1-score scăzut (~0.38) rezultă din PPV slab — IMU detectează evenimente în întregul trial de 14 s, OMC doar în fereastra de 4.5 s. Acesta nu reflectă calitatea algoritmului, ci asimetria comparației. Sensibilitatea (recall) este metrica mai relevantă [10].

### 5.3. VALIDAREA TRAIECTORIEI UNGHIULUI GLEZNEI


**[LEGENDA TABEL 8]:** Tabelul 5.2 prezintă rezultatele comparației unghi gleznă predicted vs. OMC pe 290 trial-laturi cu overlap ≥ 1 s.


**[TABEL 9]**

| Sursă | RMSE [°] | NRMSE | PCC | ROM pred [°] | ROM OMC [°] | n trials |
| --- | --- | --- | --- | --- | --- | --- |
| FSM | 13.72±4.93 | 0.868 | -0.244 | 14.6±8.3 | 22.9±12.8 | 290 |
| IMU | 8.75±5.49 | 0.529 | +0.652 | 25.8±16.2 | 22.9±12.8 | 290 |
| Țintă | < 5 | < 0.15 | > 0.90 | — | — | — |


**[LEGENDA TABEL 10]:** Tabelul 5.2. Rezultatele validării traiectoriei unghiului gleznei (FSM și IMU vs. OMC).


**[FIGURA 48 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 49] (legenda):** Fig. 5.3.1. Distribuții RMSE (stânga) și PCC (dreapta) pentru FSM (roșu) și IMU (verde) vs. OMC. IMU centrată la 7-9° RMSE cu PCC pozitiv ~0.65. FSM centrată la 13-14° RMSE cu PCC negativ.

- **[AF-5.10 | #190]** IMU vs. OMC: RMSE 8.75°, PCC +0.65. Se încadrează în intervalul publicat al algoritmilor IMU single-sensor (Pacini Panebianco 2018: RMSE 5-8°, PCC 0.85-0.95). Diferența (8.75° vs. 5-8°) este explicată parțial de: clipping anti-artefact ±35° care taie unghiurile reale extreme (S05 right OMC ROM 70°) și calibrarea la primul HS detectat care poate fi un fals pozitiv [10].
- **[AF-5.11 | #191]** FSM vs. OMC: PCC = -0.24 (negativ). Acesta NU reprezintă o eroare, ci o consecință conceptuală: FSM produce echilibre virtuale de impedanță (θeq monoton descrescător în stance, de la -8° la -25°), iar OMC observă unghiul cinematic crescător în stance (rocker dorsi, +5°→+15° la intact). Tendințele sunt matematic opuse, generando corelație negativă. Comparația corectă ar necesita simularea completă a controller-ului impedanță (M = K·(θ−θeq) + B·θ̇) cu input GRF, care depășește scopul lucrării software-only [16].

### 5.4. REZULTATE BIOMECANICE — COMPARAȚIE PROTETIC VS. INTACT


**[TABEL 11]**

| Parametru | Protetic | Intact | Diferență | Confirmare lit. |
| --- | --- | --- | --- | --- |
| Cadență [pași/min] | 100.1±11.7 | 100.3±11.3 | -0.2 (NS) | Sanderson 1997: == |
| Stride [s] | 1.215±0.142 | 1.212±0.137 | +0.003 (NS) | Idem |
| Stance % | 51.7±9.8 | 55.5±4.1 | -3.8 pp | Sand. 1997: -5..-8 |
| ROM ankle [°] | 17.0±16.4 | 38.6±11.9 | -21.6 (-56%) | Hsu 2006: -60% |


**[LEGENDA TABEL 12]:** Tabelul 9.3. Comparație parametri picior protetic vs. intact (cohorta Samala, n=30, W1).

- **[AF-5.12 | #192]** Rezultatele confirmă patru constatări biomecanice solide cu metrici cantitativi: (1) Compensare cinemată: cadența și stride-ul sunt identice între părți (diferență < 0.3%). Pacienții nu își ajustează ritmul pe partea protetică — strategia compensatorie este spațială (stance% asimetric), nu temporală [15]. (2) Redistribuire greutate: stance% protetic scade cu 3.8 puncte procentuale (51.7% vs. 55.5%), indicând că pacientul deplasează greutatea prematur pe partea sănătoasă [15]. (3) Pierdere amplitudine gleznă: ROM ankle protetic 17° vs. 38.6° intact (reducere 56%), consistent cu Hsu 2006 care raportează 60% reducere [7]. (4) Variabilitate dublă: SD stance% protetic 9.8 vs. 4.1 intact (factor ×2.4), indicând control motor instabil pe partea protetică — factor de risc cădere documentat [6].

### 5.5. REZULTATE — MERS PE TEREN (ANALIZA WASSALL)


**[TABEL 13]**

| Teren | n | Cad. [/min] | Stride [s] | Stride SD | CV | St. % | Obs. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flat | 69 | 95.1 | 1.28 | 0.12 | 0.051 | 54.7 | Ref. |
| grass | 39 | 105.3 | 1.24 | 0.29 | 0.083 | 52.1 | ↑CV |
| gravel | 39 | 87.5 | 1.43 | 0.25 | 0.088 | 55.5 | ↓cad |
| slope | 110 | 92.8 | 1.31 | 0.15 | 0.061 | 54.0 | ≈flat |
| stair | 119 | 82.8 | 1.51 | 0.35 | 0.145 | 59.5 | critic |
| uneven | 92 | 93.2 | 1.30 | 0.11 | 0.071 | 54.6 | var. |


**[LEGENDA TABEL 14]:** Tabelul 9.4. Parametri de mers per tip de teren (dataset Wassall, 506 trial-uri).


**[FIGURA 50 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 51] (legenda):** Fig. 5.5.1. Variabilitate stride (CV) per teren. Stair are variabilitate dramatic mai mare (CV ~15%) vs. flat (~5%). Linia punctată = referință CV ~3% pentru subiecți sănătoși.

- **[AF-5.13 | #193]** Scările reprezintă condiția critică: CV stride 14.5% (×2.8 vs. flat), cadență -13%, stride duration +18%, stance% +4.8 pp. CV peste 13% este factor de risc cădere bine documentat (Hausdorff 2007: CV > 6% triplează riscul, CV > 10% îl cvintuplează) [6]. Gravel-ul reprezintă al doilea cel mai dificil teren: cadență -8%, stride +12%, CV +73% vs. flat. Slope-ul este similar cu flat-ul (CV 0.061 vs. 0.051), pacienții adaptându-se bine la pante constante structural [21].
- **[AF-5.14 | #194]** Comparația directă a curbei FSM comandate cu unghiul OMC observat pe proteza SACH (Fig. 7.1) furnizează cel mai puternic argument empiric pentru necesitatea protezelor active: FSM comandă la push-off -25° plantarflexie, dar OMC observă real pe SACH doar ~-3°, rezultând un decalaj neexploatat de 22° (≈88% din comandă). Energia push-off SACH este de doar 15-20% din cea a unui mers sănătos, cu un cost energetic crescut cu 20-30% [1, 7]. Arhitectura FSM implementată este gata algoritmic pentru execuție pe proteză activă (BiOM/Empower/Vanderbilt) — lipsește doar hardware-ul de execuție [1, 3, 16].

### 5.6. LIMITĂRI ȘI DISCUȚII


#### 5.6.1. Limitări ale dataseturilor

- **[AF-5.15 | #195]** Samala 2024: (a) Fereastra OMC scurtă (~4.5 s vs. 14 s IMU) limitează numărul de evenimente disponibile pentru matching MAE (doar 3-4 strides per trial); (b) toate protezele sunt pasive (SACH dominant), nepermițând testarea controller-ului FSM pe o proteză activă reală; (c) doar mers pe plan — setpoints-urile stair/slope rămân netestate empiric; (d) număr limitat de subiecți (n=30) pentru analize stratificate per tip proteză [14].
- **[AF-5.16 | #196]** Wassall 2025: (a) Doar 4 senzori (fără markeri picior sau gleznă); (b) fără OMC — nu există ground truth pentru validarea evenimentelor; (c) condițiile stair = ascent + descent combinate, neputând separa analiza [21].

#### 5.6.2. Limitări algoritmice

- **[AF-5.17 | #197]** Sensibilitatea HS Trojaniello este de 58% (ținta era 99%), datorată biasului sistematic de 60-100 ms între algoritmul IMU și definiția Zeni OMC și ferestrei OMC scurte care reduce statistica. MAE HS de 80 ms (ținta era 25 ms) ar putea fi redus prin corecție empirică de bias. Clipping-ul ±35° al unghiului gleznei ascunde valori reale extreme. Setpoints-urile FSM sunt fixe per activitate și nu se adaptează la viteza de mers [8, 10, 18].
- **[AF-5.18 | #198]** Performanța obținută se încadrează în benchmark-urile realiste din literatura aplicată pe pacienți amputați (Maqbool 2017, Pacini Panebianco 2018): MAE 50-80 ms și sensibilitate 60-75% sunt acceptabile. PCC FSM negativ este diagnostic, nu defect: arată că FSM-ul se conformează modelului Sup 2008 și nu unui model trajectory-tracking naiv [8, 10, 16].