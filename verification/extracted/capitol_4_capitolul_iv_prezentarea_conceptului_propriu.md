# CAPITOLUL IV PREZENTAREA CONCEPTULUI PROPRIU

> Capitol extras automat din `Paun_Raluca_Raport_CS4-final.docx`. Fiecare AFIRMATIE este numerotata pentru verificare independenta.


### DESCRIEREA PLATFORMEI SOFTWARE

- **[AF-4.1 | #79]** Soluția propusă constă într-o platformă software modulară dedicată analizei  ciclului de mers al persoajelor cu proteză transtibială și sintezei controlului gleznei pe baza datelor furnizate de senzori inerțiali (IMU). Platforma este concepută astfel încât să permită prelucrarea automată a fișierelor de date, extragerea parametrilor relevanți de mers și generarea unei traiectorii de referință pentru controlul gleznei, fiind structurată pe următoarele componente funcționale: modulul de preprocesare IMU, modulul de detecție a fazelor ciclului de mers, modulul de extragere a parametrilor, modulul de control FSM al gleznei și modulul de vizualizare interactivă (dashboard). Toate acestea sunt implementate în limbajul Python [13, ].

##### Modul de preprocesare IMU

- **[AF-4.2 | #80]** Modulul de preprocesare are rolul de a importa și organiza datele brute provenite din sistemul IMU, stocate sub formă de fișiere CSV. Aceste date includ semnale de accelerație și viteză unghiulară pentru segmentele relevante ale membrului inferior. În cadrul acestui modul se realizează filtrarea semnalelor pentru reducerea zgomotului de măsurare, corectarea offsetului și eliminarea eventualelor derivații. De asemenea, dacă este necesar, se efectuează sincronizarea temporală a canalelor de date, asigurându-se coerența informației pe întreaga durată a înregistrării. Datele preprocesate sunt apoi structurate într-un format adecvat pentru etapele ulterioare de analiză și detecție a evenimentelor de mers [48, 49].

##### Modul de detecție a fazelor ciclului de mers

- **[AF-4.3 | #81]** Pe baza semnalelor IMU preprocesate, acest modul realizează identificarea automată a principalelor evenimente ale ciclului de mers, în special contactul inițial (heel strike – HS) și decolarea degetelor (toe off – TO). Aceste evenimente permit delimitarea clară a fazelor fundamentale ale ciclului de mers: faza de sprijin (stance) și faza de balans (swing). Detecția se bazează pe metode deterministe, utilizând reguli și praguri aplicate asupra semnalelor de accelerație și viteză unghiulară, sau pe metode statistice simple, adaptate caracteristicilor dataset-ului. Performanța algoritmilor de detecție este evaluată prin comparație cu datele de referință disponibile în setul de date, precum unghiurile segmentelor sau informațiile obținute din sisteme de tip motion capture [50, 53].

##### Modul de extragere a parametrilor de mers

- **[AF-4.4 | #82]** Acest modul calculează parametrii temporali și cinematici esențiali pentru caracterizarea mersului. Printre parametrii extrași se numără cadența (exprimată în pași pe minut), durata medie a fazelor de sprijin și balans, durata pasului și variabilitatea temporală a acestuia (de exemplu, deviația standard). În plus, se pot evalua indicatori de regularitate și periodicitate ai semnalelor, precum și, acolo unde datele permit, indicatori de simetrie între membrele stâng și drept. Acești parametri oferă o bază obiectivă pentru analiza diferențelor inter-subiect și pentru evaluarea stabilității mersului [52].

##### Modul de control al gleznei bazat pe faze (FSM)

- **[AF-4.5 | #83]** Modulul de control este bazat pe o mașină de stări finite (Finite State Machine – FSM), care modelează ciclul de mers printr-o succesiune de stări specifice, precum loading response, mid- stance, push-off și swing. Tranzițiile între stări sunt declanșate de evenimentele detectate (HS și TO). Pentru fiecare stare se definește o valoare de referință (setpoint) a unghiului gleznei, iar prin interpolare se obține o traiectorie continuă a unghiului în timp. Traiectoria generată este validată prin comparație cu unghiurile gleznei furnizate în dataset, utilizate ca date de referință, permițând evaluarea realismului și consistenței controlului propus.

##### Modul de vizualizare și raportare (Dashboard)

- **[AF-4.6 | #84]** Modulul de vizualizare și raportare oferă o interfață software pentru interpretarea rezultatelor obținute. Acesta include grafice ale semnalelor brute și filtrate, marcarea evenimentelor HS și TO, reprezentarea fazelor stance și swing pe axa temporală, precum și comparații între unghiul gleznei de referință și traiectoria generată de algoritmul de control. În plus, sunt generate automat tabele cu parametrii de mers extrași pentru fiecare subiect și trial, facilitând analiza comparativă și interpretarea statistică a rezultatelor.

### DESCRIEREA SETULUI DE DATE UTILIZAT

- **[AF-4.7 | #85]** Pentru dezvoltarea, testarea și validarea algoritmilor propuși, lucrarea utilizează exclusiv baze de date publice, bine documentate, care permit analiza mersului la un număr relevant de subiecți și trial-uri. Alegerea acestor seturi de date elimină necesitatea unei achiziții experimentale proprii și permite realizarea unor evaluări reproductibile și cantitative.

##### Dataset principal: purtători de proteză transtibială – Samala et al. (2024)

- **[AF-4.8 | #86]** Acest set de date conține înregistrări de la 30 de participanți purtători de proteză transtibială unilaterală (25 bărbați, 5 femei) cu o vârstă medie de 53 de ani. Participanții utilizează proteze pasive (majoritatea de tip SACH). Achiziția datelor s-a realizat în condiții de mers la viteză confortabilă pe un traseu drept, utilizând un sistem de senzori inerțiali (IMU) Noraxon la o frecvență de 200 Hz, montați pe segmentele membrelor inferioare. Simultan, a fost utilizat un sistem optic de motion capture (OMC) la 200 Hz, oferind date de referință (ground truth) pentru validarea cinematică [54, 55].

##### Achiziția datelor:

- **[AF-4.9 | #87]** Achiziția a fost realizată simultan prin:
- **[AF-4.10 | #88]** senzori inerțiali (IMU) montați pe segmentele membrelor inferioare;
- **[AF-4.11 | #89]** sistem optic de motion capture (OMC), utilizat ca referință biomecanică.
- **[AF-4.12 | #90]** Semnalele IMU includ:
- **[AF-4.13 | #91]** accelerații pe trei axe;
- **[AF-4.14 | #92]** viteze unghiulare pe trei axe.
- **[AF-4.15 | #93]** Datele IMU sunt furnizate în format .CSV și sunt utilizate ca intrare principală pentru:
- **[AF-4.16 | #94]** detecția evenimentelor de mers (heel strike și toe off);
- **[AF-4.17 | #95]** delimitarea fazelor ciclului de mers (stance și swing);
- **[AF-4.18 | #96]** extragerea parametrilor temporali ai mersului.
- **[AF-4.19 | #97]** Sistemul de motion capture a fost utilizat pentru a obține traiectorii și unghiuri articulare, care au fost ulterior procesate și puse la dispoziție sub formă de fișiere CSV.
- **[AF-4.20 | #98]** Datele IMU sunt eșantionate la o frecvență de aproximativ 100 Hz, suficientă pentru captarea
- **[AF-4.21 | #99]** evenimentelor dinamice ale mersului.
- **[AF-4.22 | #100]** Datele de motion capture au fost achiziționate la o frecvență mai mare (100–200 Hz) pentru a
- **[AF-4.23 | #101]** asigura o referință precisă a mișcării articulare.
- **[AF-4.24 | #102]** Unghiurile articulare furnizate în dataset sunt sincronizate temporal cu semnalele IMU [54, 55].

##### Dataset complementar: date IMU în condiții reale de utilizare - Wassall NTNU (2025)

- **[AF-4.25 | #103]** Pentru analiza comportamentului algoritmilor în scenarii mai apropiate de utilizarea cotidiană, se va utiliza un dataset complementar care include date de la 16  utilizatori de proteză transtibială [56].
- **[AF-4.26 | #104]** Datele au fost colectate exclusiv cu senzori IMU purtabili, în condiții reale de teren, fără un sistem optic de referință. Participanții au efectuat activități de mers pe:
- **[AF-4.27 | #105]** teren plan;
- **[AF-4.28 | #106]** scări;
- **[AF-4.29 | #107]** pante;
- **[AF-4.30 | #108]** suprafețe instabile (iarbă, teren denivelat);
- **[AF-4.31 | #109]** cu și fără dispozitive de sprijin.
- **[AF-4.32 | #110]** Semnalele IMU au fost eșantionate la o frecvență de aproximativ 100 Hz, similar cu datasetul principal, permițând reutilizarea acelorași algoritmi de preprocesare și detecție a evenimentelor [35].

##### GaitRec

- **[AF-4.33 | #111]** Datasetul GaitRec conține date de la un număr mare de pacienți, totalizând peste 75.000 de trial-uri bilaterale de mers, bazate pe măsurători ale forțelor de reacțiune la sol (GRF) [57].
- **[AF-4.34 | #112]** Caracteristici principale:
- **[AF-4.35 | #113]** datele sunt achiziționate cu platforme de forță;
- **[AF-4.36 | #114]** sunt disponibile multiple tipare de mers, inclusiv patologice;
- **[AF-4.37 | #115]** frecvența de eșantionare este ridicată (aproximativ 1000 Hz), specifică sistemelor de forță.
- **[AF-4.38 | #116]** Acest dataset este util pentru:
- **[AF-4.39 | #117]** validări statistice la scară largă;
- **[AF-4.40 | #118]** comparații între parametri temporali ai mersului;
- **[AF-4.41 | #119]** studii asupra regularității și simetriei mersului.

### PRELUCRAREA SI ANALIZA DATELOR


#### 4.3.1. Preprocesarea semnalelor

- **[AF-4.42 | #120]** Zgomotul inerent senzorilor inerțiali este atenuat utilizând un filtru low-pass Butterworth de ordinul 4. Filtrarea este aplicată în regim zero-phase (folosind funcția filtfilt din librăria scipy.signal), care execută o filtrare bidirecțională (forward și backward). Această metodă elimină complet defazajul introdus de filtru, aspect absolut critic pentru detectarea cu precizie a evenimentelor de mers în timp. Frecvența de tăiere a fost setată la 15 Hz pentru algoritmul de detecție a evenimentelor de mers și la 6 Hz pentru calculul cinematicii articulare.
- **[AF-4.43 | #121]** Platforma utilizează doi algoritmi avansați pentru detecția automată a momentului de contact inițial al călcâiului (Heel Strike - HS) și a momentului desprinderii degetelor de pe sol (Toe Off - TO):
- **[AF-4.44 | #122]** Algoritmul Trojaniello (Analiză Offline): Considerat standardul de referință în literatură pentru analiza offline, acest algoritm se bazează pe modelul caracteristic al vitezei unghiulare a tibiei în plan sagital (ωshank.). Algoritmul detectează vârful pozitiv din faza de balans (mid-swing) și îl folosește ca ancoră temporală pentru a căuta minimele locale ce corespund impactului călcâiului și ridicării piciorului. Deoarece subiecții purtători de proteze prezintă amplitudini mai reduse ale mișcării, pragurile algoritmului au fost scalate la 60% din valorile standard specifice mersului sănătos.
- **[AF-4.45 | #123]** Algoritmul Maqbool R-GEDS (Analiză Real-Time): Conceput specific pentru comanda protezelor active în timp real, acest algoritm procesează semnalele eșantion cu eșantion. Funcționează pe baza unei mașini de stări (STANCE, SWING, HS_PENDING, perioadă refractară). Deciziile se bazează pe praguri ale vitezei unghiulare și pe calculul magnitudinii vectoriale a accelerației (|a| = √(ax² + ay² + az²) necesar pentru a capta „spike-urile” mecanice de impact la momentul HS (aprox. 1.5g).
- **[AF-4.46 | #124]** Calculul unghiului gleznei
- **[AF-4.47 | #125]** Pentru a respecta convenția clinică standard (Perry & Burnfield), unghiul real al gleznei este calculat intern prin platformă, fiind derivat din diferența de orientare dintre segmentul tibiei (shank pitch) și cel al tălpii (foot pitch). Semnalul rezultat este calibrat la 0° la momentul primului eveniment HS detectat, este filtrat cu un filtru low-pass la 6 Hz și tăiat (clipping) la un interval strict de +/- 35° pentru a elimina artefactele care depășesc limitele anatomice fiziologice.
- **[AF-4.48 | #126]** Segmentarea ciclului de mers și calculul parametrilor
- **[AF-4.49 | #127]** Un ciclu complet de mers (stride) este definit ca intervalul delimitat de două evenimente HS consecutive ale aceluiași picior. Sistemul implementează o etapă de rejecție a outlier-ilor, eliminând ciclurile a căror durată se află în afara intervalului acceptabil față de mediana generală a pașilor. La final, se extrag parametrii temporali clinici: cadența (pași/minut), durata pasului (medie și deviație standard), coeficientul de variație, procentul fazei de sprijin (stance %) și indicele de simetrie Robinson între piciorul protetic și cel intact.
- **[AF-4.50 | #128]** Prelucrarea și analiza datelor au fost realizate în Python. Semnalele de accelerometru și giroscop au fost filtrate și corectate, iar apoi folosite pentru detectarea evenimentelor heel strike și toe off, segmentarea fazelor stance și swing și calculul parametrilor temporali ai mersului, precum durata medie a pasului și cadenta. Rezultatele au fost vizualizate prin grafice pentru a evidenția dinamica mersului și caracteristicile fiecărui subiect.
- **[AF-4.51 | #129]** Analiza semnalelor IMU a început cu identificarea evenimentelor principale ale ciclului de mers, respectiv momentul contactului călcâiului cu solul (heel strike, HS) și momentul ridicării vârfului piciorului (toe off, TO). Detecția acestor evenimente a fost realizată folosind semnale de accelerometru și giroscop înregistrate la nivelul tibiei și al coapsei. Figura 4.3.1. care ilustrează detecția heel strike și toe off prezintă clar momentele de contact inițial și de ridicare a piciorului pentru un trial reprezentativ, evidențiind secvențele de stance și swing. Această vizualizare permite aprecierea preciziei algoritmilor de detecție și constituie baza pentru segmentarea ciclurilor de mers.

**[FIGURA 29 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 30] (legenda):** Fig. 4.3.1. Explorarea semnalelor IMU (comparație picior protetic stâng vs. intact drept), ilustrând detecția evenimentelor HS și TO, magnitudinea accelerației și unghiul calculat al gleznei.


**[FIGURA 31 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 32] (legenda):** Fig. 4.3.2. Suprapunerea pașilor normalizați (100% din ciclul de mers) pentru piciorul intact, demonstrând prezența tiparului fiziologic (rocker ankle).

- **[AF-4.52 | #130]** Pe baza evenimentelor HS și TO, ciclul de mers a fost segmentat în fazele stance și swing.
- **[AF-4.53 | #131]** Segmentarea fazelor ciclului de mers arată delimitarea clară a fiecărei faze, cu marcarea secvențelor de sprijin și balans, facilitând calculul proporției timpului petrecut în fiecare fază. Valorile medii pentru faza stance au fost de aproximativ 49.6%, iar pentru faza swing 50.4%, ceea ce indică un echilibru aproape simetric între cele două faze pentru majoritatea subiecților.

**[FIGURA 33 — imagine inline]** Figura 4.3.3. ilustrează distribuția duratei medii a ciclului de mers (stride mean) pe șase tipuri distincte de suprafețe: teren plan (flat), iarbă (grass), pietriș (gravel), pantă (slope), scări (stair) și teren denivelat (uneven) . Se observă că mediul care impune cele mai mari adaptări este reprezentat de scări (stair), unde pacienții înregistrează pași vizibil mai lungi ca durată comparativ cu deplasarea pe teren plan (o medie de 1.51 s față de 1.28 s). Această creștere indică execuția unui pas mai amplu și adoptarea unei strategii compensatorii necesare pentru menținerea stabilității pe trepte. Totodată, diagrama evidențiază o dispersie crescută a datelor și prezența unor valori extreme izolate (outliers) pe suprafețele dificile, reflectând o variabilitate ridicată a controlului motor și dificultățile specifice întâmpinate de purtătorii de proteze pe teren instabil.


**[FIGURA 34] (legenda):** Fig. 4.3.3. Segmentarea fazelor ciclului de mers.

- **[AF-4.54 | #132]** Variabilitatea duratei pasului a fost analizată pentru a evalua consistența mersului. Valorile medii ale duratei pasului pentru subiecți variază între 0.606 s (S14) și 1.130 s (S02), cu deviații standard între 0.013 s (S10) și 0.152 s (S08). Această informație contureaza regularitatea mersului și adaptările individuale ale ritmului de deplasare.
- **[AF-4.55 | #133]** Parametrii temporali agregati pe subiect au fost calculați pentru a permite comparații între participanți. Durata medie a pasului pe subiect arată variații semnificative, cu valori medii între 0.606 s (S14) și 1.130 s (S02).

**[FIGURA 35] (legenda):** Figura 4.3.5 ilustreaza distribuția cadenței (exprimată în pași pe minut) în funcție de aceleași șase tipuri de suprafețe. Având o relație biomecanică invers proporțională cu durata ciclului de mers, cadența reflectă fidel adaptarea ritmului de deplasare la constrângerile mediului. Conform graficului, se observă că cea mai scăzută cadență mediană se înregistrează pe scări (stair) și pe pietriș (gravel). Pe aceste suprafețe complexe, necesitatea compensării limitărilor mecanice ale protezei și menținerii echilibrului forțează pacienții să adopte un ritm de pășire considerabil mai lent și mai precaut. În contrast, suprafețele cu o predictibilitate mai mare, precum terenul plan (flat) sau iarba (grass), facilitează o cadență superioară, asociată cu o propulsie mai fluidă și un control dinamic stabil. Prezența dispersiei mari a datelor și a valorilor extreme (outliers) pe terenurile dificile confirmă faptul că neregularitățile mediului afectează puternic ritmicitatea mersului, accentuând asimetriile inter-subiect specifice utilizatorilor de proteze transtibiale.


**[FIGURA 36 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 37] (legenda):** Fig. 4.3.4. Cadența per teren. Mediana scade de la flat (107) → uneven (101) → slope (101) → grass (102) → gravel (88) → stair (83). Pacienții merg mai lent pe teren dificil.

- **[AF-4.56 | #134]** Întregul flux de analiză urmează un fir logic clar: pornind de la semnalele brute din IMU, trecând prin detecția evenimentelor HS și TO, segmentarea fazelor stance și swing, analiza variabilității pasului și a semnalelor IMU, și în final calculul parametrilor temporali și agregarea lor pe subiect. Figurile prezentate reflectă fiecare etapă a procesului, permițând interpretarea vizuală și numerică a datelor, oferind o imagine completă asupra dinamicii mersului și asupra performanței algoritmilor de detecție și segmentare temporală.
- **[AF-4.57 | #135]** FLUXUL DE DATE
- **[AF-4.58 | #136]** Fluxul de procesare a datelor parcurge următoarele etape secvențiale: (1) fișierele CSV brute (Samala/Wassall) sunt importate prin funcțiile din io_utils în DataFrame-uri pandas; (2) semnalele sunt preprocesate prin filtrare Butterworth și calcul magnitudine accelerație; (3) algoritmii de detecție (Trojaniello sau Maqbool) identifică evenimentele HS și TO; (4) ciclurile de mers sunt construite și filtrate prin rejecția outlierilor; (5) parametrii temporali sunt calculați (cadență, stride, stance%); (6) pentru simularea FSM, evenimentele detectate alimentează mașina de stări finite care generează traiectoria de referință a unghiului gleznei prin interpolare PCHIP [10, 18, 24].
- **[AF-4.59 | #137]** Pentru pipeline-ul de validare, fișierele C3D cu markeri OMC sunt procesate prin algoritmul Zeni 2008, iar evenimentele OMC rezultate sunt aliniate temporal cu cele IMU prin cross-corelație pe semnalul unghiului gleznei. Metricile de validare (MAE, RMSE, NRMSE, PCC) sunt calculate automat și exportate în fișiere CSV structurate [24].

**[FIGURA 38 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 39] (legenda):** Fig. 4.4.1. Flowchart cu fluxul de lucru al platformei software.

- **[AF-4.60 | #138]** PREPROCESAREA SEMNALELOR

#### 4.5.1. Filtrul low-pass Butterworth

- **[AF-4.61 | #139]** Toate semnalele IMU sunt filtrate cu un filtru Butterworth low-pass, de ordin 4, în regim zero-phase (filtfilt), cu frecvență de tăiere de 15 Hz pentru detecția evenimentelor de mers și 6 Hz pentru cinematica articulară, conform standardelor stabilite de Winter (1991) și Catalfamo (2010) [4, 23]. Aplicarea filtrului filtfilt (forward + backward) elimină defazajul introdus de filtru, aspect esențial pentru detecția precisă a evenimentelor. În caz contrar, momentul HS ar fi detectat cu 15-25 ms întârziere.
- **[AF-4.62 | #140]** Implementarea filtrului utilizează funcțiile butter și filtfilt din biblioteca scipy.signal, cu parametrul padlen ajustat pentru a evita artefactele de margine pe semnale scurte.

#### 4.5.2. Magnitudinea accelerației

- **[AF-4.63 | #141]** Pentru algoritmul Maqbool 2017 (R-GEDS), se calculează magnitudinea vectorială a accelerației:
- **[AF-4.64 | #142]** |a| = √(ax² + ay² + az²)
- **[AF-4.65 | #143]** din accelerațiile shank în sistemul senzorului (m/s²). Spike-urile de impact la heel strike sunt vizibile peste pragul de ~1.5g (14.7 m/s²) [8].

### 4.6. DETECȚIA EVENIMENTELOR DE MERS — ALGORITMUL TROJANIELLO

- **[AF-4.66 | #144]** Primul algoritm implementat pentru detecția evenimentelor heel strike (HS) și toe off (TO) este cel propus de Trojaniello et al. (2014), considerat standardul de referință offline în literatura de specialitate [18].
- **[AF-4.67 | #145]** Principiul algoritmului se bazează pe pattern-ul caracteristic al vitezei unghiulare a tibiei în plan sagital (ωshank,y): vârful pozitiv în faza mid-swing (~+200...+400°/s) reprezintă ancora temporală, minimul local imediat după peak (~-100°/s) corespunde momentului HS (impactul decelerază brusc tibia), iar minimul local imediat înainte de peak (~-30...-100°/s) corespunde momentului TO (tibia începe rotația posterioară). Ferestrele temporale fixe de la peak sunt: HS în [tpeak, tpeak + 350 ms] și TO în [tpeak − 450 ms, tpeak − 100 ms] [18].

#### 4.6.1. Adaptarea pentru piciorul protetic

- **[AF-4.68 | #146]** Subiecții cu proteză prezintă amplitudini reduse ale ωshank (shank-ul este mai puțin dinamic, există pierdere de propriocepție). În consecință, pragurile de detecție sunt scalate la 60% din valorile pentru subiecți sănătoși, conform recomandării lui Maqbool (2017) [8, 18].

### 4.7. DETECȚIA EVENIMENTELOR DE MERS — ALGORITMUL MAQBOOL R-GEDS

- **[AF-4.69 | #147]** Al doilea algoritm implementat este R-GEDS (Real-time Gait Event Detection System), propus de Maqbool et al. (2017), proiectat specific pentru controlul protezelor active ale membrului inferior [8].
- **[AF-4.70 | #148]** Algoritmul utilizează o mașină de stări cu un număr de 4 stări: STANCE, SWING, HS_PENDING și o perioadă refractară. Tranziția STANCE → SWING are loc când ω > ωswing_in. După un timp minim în swing, dacă ω < ωhs ȘI |a| > ahs, starea trece în HS_PENDING, confirmând evenimentul HS. Evenimentul TO este detectat la tranziția STANCE → SWING (intrarea în swing) [8].
- **[AF-4.71 | #149]** Avantajul principal al algoritmului Maqbool este capacitatea de operare în timp real: nu necesită vizualizare globală a semnalului (Trojaniello necesită găsirea maximului mid-swing, care este definit doar după ce a trecut). Maqbool poate fi rulat sample-by-sample în controller-ul protezei active, ceea ce îl face ideal pentru implementarea pe microcontroller [8, 19].

### 4.8. CALCULUL UNGHIULUI GLEZNEI DIN IMU

- **[AF-4.72 | #150]** Funcția compute_ankle_angle derivă unghiul real al gleznei din diferența de orientare între segmentele tibie (shank) și picior (foot). Convenția utilizată este dorsiflexie pozitivă (+) și plantarflexie negativă (-), conform standardului clinic Perry și Burnfield (2010) [11]. Calibrarea se realizează la primul eveniment HS detectat (unghiul este setat la 0°, conform convenției clinice), urmată de filtrare low-pass la 6 Hz (Winter 1991) și clipping la ±35° pentru eliminarea artefactelor care depășesc limitele fiziologice [11, 23].
- **[AF-4.73 | #151]** Notație: coloanele Ankle Dorsiflexion LT/RT furnizate nativ de Noraxon în datasetul Samala prezintă semn opus convenției clinice standard și valori non-fiziologice în faza swing (+25° sau mai mult). Din acest motiv, s-a implementat o funcție proprie de calcul, validată empiric contra ciclului fiziologic Perry și Burnfield: HS ≈ 0°, push-off ≈ -18°, mid-swing ≈ +10° [11].

### 4.9. SEGMENTAREA CICLULUI DE MERS

- **[AF-4.74 | #152]** Un stride complet (un ciclu complet de mers realizat de același picior) este definit ca intervalul [HSi, HSi+1]. Faza stance corespunde intervalului [HSi, TOi], iar faza swing intervalului [TOi, HSi+1]. Rejecția outlierilor se realizează prin eliminarea stride-urilor cu durată în afara intervalului [0.5·mediană, 1.5·mediană], conform Trojaniello (2014) și Pacini Panebianco (2018) [10, 18].

**[FIGURA 40 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 41] (legenda):** Fig. 4.9.1. Suprapunere stride-uri normalizate la 100% gait cycle pentru S01 W1 RIGHT (picior intact). Stânga: ω shank pitch. Dreapta: unghi gleznă. Linia groasă = media; banda umbră = ±1 SD.


### 4.10. PARAMETRII TEMPORALI CALCULAȚI

- **[AF-4.75 | #153]** Funcția compute_gait_params agregează următorii parametri clinici relevanți:
- **[AF-4.76 | #154]** cadența [pași/min] = 60 · 2 · n_strides / durată_totală;
- **[AF-4.77 | #155]** durata stride [s] exprimată ca medie ± deviație standard,
- **[AF-4.78 | #156]** coeficientul de variație CV = std/mean;
- **[AF-4.79 | #157]** procentajul stance = (tTO − tHS) / (tHS_next − tHS) · 100;
- **[AF-4.80 | #158]** procentajul swing = 100 − stance%;
- **[AF-4.81 | #159]** indicele de simetrie Robinson (1987) între partea protetică și cea intactă:
- **[AF-4.82 | #160]** SI = 2·(P − I)/(P + I)·100 [12, 15].

### 4.11. FSM — CONTROLUL ADAPTIV AL GLEZNEI PROTETICE

- **[AF-4.83 | #161]** Protezele active (BiOM/Empower, Vanderbilt powered ankle, SpringActive) utilizează o mașină de stări finite (Finite State Machine — FSM) alimentată de senzori IMU pentru a detecta faza curentă a ciclului de mers și a comanda torque-ul/poziția corespunzătoare a gleznei: plantarflexie activă în push-off, dorsiflexie în swing pentru toe clearance, echilibru neutru în mid-stance [1, 3, 16, 19].
- **[AF-4.84 | #162]** Implementarea din platforma care face obiectul acestei lucrări reproduce arhitectura standard FSM cu 5 stări din literatura, oferind o traiectorie de referință a unghiului gleznei pentru fiecare sample IMU, care în practică ar fi setpoint-ul transmis ca și comandă motorului protezei.

#### 4.11.1. Cele 5 stări FSM

- **[AF-4.85 | #163]** S1 — Loading Response: Trigger-ul de intrare este evenimentul HS detectat. Funcția fiziologică este absorbția impactului prin plantarflexie controlată. Setpoint-ul pentru mers pe plan: -8° (plantarflexie ușoară).
- **[AF-4.86 | #164]** S2 — Mid-Stance: Trigger-ul de intrare este detecția foot-flat (|ωshank| < 30°/s timp de 50 ms). Funcția este tranziția de echilibru — tibia trece peste piciorul pivot. Setpoint level: -15° (interpolare către push-off).
- **[AF-4.87 | #165]** S3 — Push-Off: Trigger-ul de intrare este condiția dorsiflexie > 3° SAU depășirea a 45% din durata stride mediană. Funcția este propulsia activă — plantarflexie maximă. Setpoint level: -25° (conform Sup 2008, Mode 2) [16].
- **[AF-4.88 | #166]** S4 — Early Swing: Trigger-ul de intrare este evenimentul TO detectat. Funcția este repoziționarea gleznei spre neutru pentru evitarea contactului cu solul. Setpoint level: -5°.
- **[AF-4.89 | #167]** S5 — Late Swing: Trigger-ul de intrare este peak-ul ω shank pitch (mid-swing). Funcția este pregătirea HS — ușoară dorsiflexie pentru contactul călcâiului. Setpoint level: -3°.

#### 4.11.2. Setpoints per activitate


**[LEGENDA TABEL 3]:** Tabelul 4.1 prezintă valorile setpoint-urilor (echilibre de impedanță θeq) per activitate, exprimate în grade. Convenția utilizată este: dorsiflexie pozitivă (+), plantarflexie negativă (-), neutru = 0° [16, 17].


**[TABEL 4]**

| Stare | Level | Stair Asc | Stair Desc | Slope Up | Slope Down |
| --- | --- | --- | --- | --- | --- |
| S1 Loading | -8 | -3 | -15 | -5 | -12 |
| S2 Mid-Stance | -15 | -8 | -20 | -12 | -18 |
| S3 Push-Off | -25 | -18 | -30 | -22 | -28 |
| S4 Early Swing | -5 | -3 | -15 | -3 | -10 |
| S5 Late Swing | -3 | 0 | -8 | -1 | -5 |


**[LEGENDA TABEL 5]:** Tabelul 4.1. Setpoints FSM (θeq, grade) per activitate și stare.

- **[AF-4.90 | #168]** Este important de subliniat că valorile setpoint-urilor NU reprezintă unghiuri observate fiziologic la o persoană sănătoasă. Ele reprezintă echilibre virtuale de impedanță (θeq) utilizate de controller-ul Sup, Bohara și Goldfarb (2008). Unghiul observat al gleznei rezultă din: θobserved = θeq + (MGRF / Kstiffness), unde GRF este ground reaction force, iar K este rigiditatea impedanței [16]. Această interpretare este fundamentală pentru înțelegerea rezultatelor validării FSM vs. OMC prezentate în Capitolul IX.

#### 4.11.3. Generarea traiectoriei continue (PCHIP)

- **[AF-4.91 | #169]** Setpoint-urile discrete (constante per stare) trebuie transformate într-o traiectorie continuă netedă, comandabilă unui motor real. Pentru aceasta se utilizează PchipInterpolator (Piecewise Cubic Hermite Interpolating Polynomial) din scipy. Pentru fiecare segment de stare, se plasează un waypoint la 30% din durată, astfel încât traiectoria să atingă setpoint-ul devreme și să-l mențină. PCHIP garantează monotonia între waypoints, evitând overshoot-ul [3].
- **[AF-4.92 | #170]** FSM-ul implementează timeout pe stare (1.5 × durată mediană stride) pentru a evita blocajele atunci când evenimentul așteptat nu apare. Dacă HS lipsește, după timeout, starea se forțează la S1, conform recomandării Varol, Sup și Goldfarb (2010) [19].

**[FIGURA 42 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 43] (legenda):** Fig. 4.11.3.1. Comparație vizuală: OMC (negru) vs. IMU calculat (verde) vs. FSM comandat (roșu) pentru S01 W1 RIGHT (picior intact). Curba FSM are forma de impedance equilibrium — monoton descrescătoare în stance (-8°→-25°), apoi salt rapid spre 0° în swing. Curba OMC este unghiul cinematic real.


### 4.12. VIZUALIZARE ȘI DASHBOARD INTERACTIV

- **[AF-4.93 | #171]** Pentru a oferi feedback intuitiv asupra controlului FSM, dashboard-ul include o animație 2D sagitală (vedere laterală) a componentei protetice — pilon + gleznă + talpă. Aceasta permite vizualizarea directă a modului în care se rotește talpa în funcție de unghiul comandat, cum se mișcă glezna pe verticală (push-off ridică, S1 coboară) și cum corespunde mișcarea cu fazele FSM (S1-S5) [5].
- **[AF-4.94 | #172]** Animația utilizează modelul bench-test MTS-type standard pentru proteze transtibiale (Hansen, Childress și Knox, 2004), cu adaptare pentru vizualizarea doar a componentei protetice (subiectul are genunchiul propriu deasupra socket-ului). Tibia (pilonul) are lungime fixă (LTIBIA = 0.33 m) și unghi fix oblic (+7°), micșându-se rigid pe verticală. Genunchiul urcă/coboară odată cu glezna, păstrând lungimea și unghiul tibiei. Talpa rotește în jurul gleznei după unghiul exact din date (FSM sau IMU), fără scalare [5].
- **[AF-4.95 | #173]** În stance (S1+S2+S3), cel mai jos punct al tălpii (în plantarflexie: vârful; în dorsiflexie: călcâiul) atinge solul, glezna culisând vertical conform geometriei. În swing (S4+S5), glezna se ridică la 6 cm peste poziția neutră. Pentru a evita salturile vizuale la TO și HS, poziția gleznei se interpolează lin pe o fereastră de 80 ms (5 cadre la 60 fps) [5].

**[FIGURA 44 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 45] (legenda):** Fig. 4.12.1. Cele 5 faze ale simulatorului protezei pentru subiectul S01 W1 LEFT (picior protetic). De la stânga la dreapta: S1 (albastru) = călcâi pe sol; S2 (verde) = talpă plată; S3 (roșu) = vârf pe sol, călcâiul ridicat; S4 (portocaliu) = piciorul ridicat; S5 (violet) = piciorul coboară pentru următorul HS.

- **[AF-4.96 | #174]** Dashboard-ul utilizează mecanismul nativ multi-page Streamlit: fișierul app.py este landing page, iar fiecare fișier din directorul pages/ devine o pagină accesibilă din sidebar. Modulul _shared.py definește funcții cached (@st.cache_data) pentru loaders — citirea CSV-urilor se face o singură dată per sesiune.
- **[AF-4.97 | #175]** Pagina 1 — Signal Explorer: Explorare interactivă a semnalelor IMU brute. Permite alegerea subiectului, trial-ului, lateralității și a coloanelor specifice (gyro, accel, orientare). Grafice Plotly cu zoom/pan.
- **[AF-4.98 | #176]** Pagina 2 — Gait Events: Vizualizare evenimente HS/TO detectate de cei doi algoritmi (Trojaniello + Maqbool) suprapuse peste semnalul shank pitch. Markeri colorați (roșu HS, albastru TO). Statistici per trial.
- **[AF-4.99 | #177]** Pagina 3 — Parameters: Tabel cu parametri temporali (cadență, stride, stance%, CV) pentru trial-ul selectat. Symmetry Index între picior protetic și intact. Comparare rapidă a celor 5 trial-uri ale aceluiași subiect.
- **[AF-4.100 | #178]** Pagina 4 — FSM Simulator: Vizualizare stări FSM pe ciclu de mers. Plot dublu: sus = traiectoria comandată (setpoints PCHIP) suprapusă peste unghiul real din IMU; jos = stările FSM colorate per sample (S1-S5).
- **[AF-4.101 | #179]** Pagina 5 — Activity Compare: Agregare parametri Wassall per teren (flat/grass/gravel/slope/stair/uneven). Boxplots Plotly pe cadență, stance%, stride per teren, separate cu/fără baston.
- **[AF-4.102 | #180]** Pagina 6 — Prosthesis Simulator: Animația 2D a componentei protetice. Componente UI: selectoare subiect/trial/activitate/sursă unghi, slider fereastră animație (2-15 s), slider viteză (0.1×–2.0×), buton Play/Pause, plot dublu sincronizat (animație + semnal unghi cu stare FSM) [5].