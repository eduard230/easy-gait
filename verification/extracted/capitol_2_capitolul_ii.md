# CAPITOLUL II

> Capitol extras automat din `Paun_Raluca_Raport_CS4-final.docx`. Fiecare AFIRMATIE este numerotata pentru verificare independenta.


## DEZVOLTAREA PROTEZEI TRANSTIBIALE ACTIVE

- **[AF-2.1 | #58]** Proteza care face obiectul acestei lucrări va avea mai multe componente, printre care: cupă protetică/suportul bontului (se potrivește direct pe partea amputată a membrului și asigură susținerea și transferul greutății corpului utilizatorului către proteză), scheletul de bază (susține și distribuie greutatea corpului), partea de acționare a gleznei și talpa protetică (oferă o stabilitate cât mai ridicată protezei).
- **[AF-2.2 | #59]** In continuare, pentru dimensionarea protezei s-a realizat un STUDIU ANTROPOMETRIC. S-a presupus că pacientul a suferit o intervenție de amputație a piciorului stâng. Pentru dimensionarea protezei s-a realizat un studiu antropometric ce a presupus masurători precise ale piciorului drept al subiectului. Aceste măsurători au fost extrase din imagini relevante studiului.
- **[AF-2.3 | #60]** Imaginile obtinute au fost oglindite, deoarece proiectarea se face pentru o proteza transtibială de picior stâng. Măsuratorile obtinute au fost centralizate in tabelul următor:

**[TABEL 1]**

| Nr. crt | Denumirea | Dimensiune[mm] |
| --- | --- | --- |
| 1 | Lungimea tălpii | 250 |
| 2 | Lățimea tălpii | 100 |
| 3 | Înălțimea maximă a gleznei | 75 |
| 4 | Circumferința gleznei | 250 |
| 5 | Lungimea feței dorsale a piciorului | 175 |
| 6 | Lungimea gleznei | 40 |
| 7 | Lungimea totală a protezei | 330 |
| 8 | Lungimea dintre cupa protetică și genunchi | 237 |
| 9 | Circumferința la baza bontului | 316 |
| 10 | Lungimea dintre bontul distal și până deasupra genunchiului | 190 |


**[LEGENDA TABEL 2]:** Tabel 2.1. Datele antropometrice ale subiectului.

- **[AF-2.4 | #61]** Dimensionarea corectă a protezei este esențială pentru a asigura confortul, funcționalitatea și satisfacția utilizatorului. O proteză corespunzătoare va permite pacientului să își desfășoare activitățile zilnice și sarcinile specifice cu mai multă ușurință. Prin optimizarea dimensiunilor și a mecanismului de acționare, purtătorul poate să interacționeze cu mediul înconjurător într-un mod cât mai natural și eficient. O proteză dimensionată necorespunzător poate provoca disconfort și poate duce la complicații precum presiuni excesive, iritații ale pielii, deformări, escare sau chiar răni grave, de aceea acest proces este deosebit de important pentru obținerea unui rezultat pe măsura așteptărilor. Executarea design-ului grafic al modelului s-a realizat utilizând mediul de programare software SOLIDWORKS. Sistemul protetic este alcătuit din 3 mari componente: talpa protetică,
- **[AF-2.5 | #62]** glezna acționată electro-mecanic și cupa protetică (suportul bontului).
- **[AF-2.6 | #63]** În continuare va fi exemplificată procedura de realizare a pieselor componente.
- **[AF-2.7 | #64]** Pentru a modela talpa protezei s-a pornit în SOLIDWORKS de la un document Part setat în milimetri (MMGS); conturul 2D al tălpii a fost trasat folosind Line, Rectangle și Circle, apoi transformat în volum printr-o extrudare uniformă de 2 mm cu funcția Extruded Boss/Base, după care marginile au fost rotunjite cu Fillet, iar partea din spate a primit un profil complet curbat prin Full Round Fillet, astfel încât piesa finală să reproducă fidel forma piciorului uman și să îndeplinească cerințele de rezistență, flexibilitate, durabilitate și eficiență economică impuse.

**[FIGURA 15 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 16] (legenda):** Fig. 2.1. Imagine 3D cu talpa protetică a modelului.


**[FIGURA 17 — imagine inline]** Pentru cupa protetică, care face legătura dintre bontul pacientului și restul protezei și preia integral greutatea corpului, s-a pornit, la fel ca în cazul tălpii, de la un document Part în SOLIDWORKS setat pe unități în milimetri; conturul exterior a fost trasat cu Spline raportat la o linie centrală, iar transformarea în volum s-a realizat prin Surface-Revolve; decupajele frontal și posterior au fost obținute tot cu Spline, urmate de Surface-Trim; pentru a crește rigiditatea la solicitările dinamice, s-a aplicat Offset către exterior, adăugând o grosime de circa 5 milimetri, după care piesa a fost concepută în două straturi: unul interior, neted, albastru, de aproximativ 7 milimetri, și unul exterior, gri, perforat, de aproximativ 3 milimetri; la final, cele două componente au fost îmbinate într-un document Assembly prin funcția Mate, rezultând o cupă ușoară, bine adaptată, estetică și ușor de întreținut.


**[FIGURA 18] (legenda):** Fig. 2.2. Imagine 3D cu partea laterală a suportului;

- **[AF-2.8 | #65]** Pentru acționarea protezei transtibiale s-a ales un angrenaj melcat; melcul (⌀ 26 mm, L 91 mm) a fost creat în SOLIDWORKS trasând profilul cu Circle, apoi aplicând Revolve pentru volumul de bază, peste care Helix and Spiral a definit filetul, iar Swept Boss/Base i-a conferit lățimea dorită; roata melcată (⌀ 87 mm) a pornit tot cu Circle, i-a fost adăugat un gol intern dreptunghiular, muchiile au fost teșite cu Chamfer, dinții rotunjiți s-au decupat cu Revolved Cut, pasul elicei a fost descris cu Helix/Spiral, iar multiplicarea celor 43 de dinți s-a realizat prin Circular Pattern. Melcul și roata au fost inserate în fișierul Assembly, aliniate cu Mate și verificate la 40 RPM în Motion Study, rezultând un ansamblu de 113 mm înălțime. Conexiunea cu cupa bontului și talpa se face printr-un pilon cilindric reglabil, plin (⌀ 15 mm, h 5 mm), iar un suport intermediar curbat, înclinat la 20° prin Extrude Cut, stabilizează pilonul pe talpă, completând structura protezei.

**[FIGURA 19 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 20] (legenda):** Fig.2.3. Imagini 3D cu pilonul protezei (A) și cu angrenajul actualizat (B).

- **[AF-2.9 | #66]** Pentru realizarea ansamblului final s-au utilizat aceiași pași descriși anterior. S-a deschis un document nou de tip Assembly, iar cu funcția Insert Component s-au adăugat pe rând talpa protetică, suportul bontului, mecanismul de acționare a gleznei si pilonul de susținere. Utilizând funcția Mate s-a realizat alinierea componentelor, astfel încât accestea să se regăsească în același plan și să funcționeze corespunzător împreună. Pentru verificarea funcționării ansamblului, s-a realizat un studiu al mișcării folosind funcția Motion Study.
- **[AF-2.10 | #67]** În figura 2.4. este reprezentat ansamblul final al sistemului protetic transtibial.

**[FIGURA 21 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 22] (legenda):** Fig. 2.4. Imagini 3D cu partea laterală (A,B) și frontală (C) a ansamblului final

- **[AF-2.11 | #68]** Pentru a simula o mișcare cât mai aproape de cea realizată de o gleznă umană sănătoasă, se vor utiliza date achiziționate de un accelerometru triaxial, reprezentat în figura 2.5. Rolul principal al acestuia este de a analiza mișcarea, poziția și schimbarea vitezei unui sistem într-un anumit context. În această lucrare, rolul accelerometrului va fi de a analiza mișcarea piciorului în diverse unghiuri, în timp ce pacientul execută diferite miscări. De asemenea, el poate fi util și în stabilitatea individului, acesta putând detecta unele mișcări bruște sau schimbări de poziție, și poate permite o conexiune inteligentă între proteză și un smartphone sau alt dispozitiv electronic folosit pentru monitorizare medicală [45].
- **[AF-2.12 | #69]** Toată această monitorizare a mersului poate, într-un final, să ofere confort utilizatorului, să ii îmbunătățească starea de sănătate și să îi crească semnificativ calitatea vieții.

**[FIGURA 23 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 24] (legenda):** Fig.2.5. Accelerometru MPU-9250/6500 [46]

- **[AF-2.13 | #70]** Pentru acționarea electronică a ansamblului, melcul va fi conectat la un servomotor, alimentat de către un microcontroller Arduino UNO R3, ale cărui caracteristici vor fi discutate în capitolul următor.
- **[AF-2.14 | #71]** În continuare, pentru a realiza o proiectare cât mai aproape de realitate, s-a ales ca în modelul 3D să se introducă și modelele 3D ale componentelor electronice utilizate. Astfel, în figura 2.6. este reprezentat 3D în software-ul SOLIDWORKS servo motorul MG90s care va furniza energia necesară pentru a roti angrenajul melcat, și implicit pentru a acționa întreaga gleznă, și amplasarea lui în sistemul protetic. Modelul 3D este preluat de pe platforma online GrabCAD.

**[FIGURA 25 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 26] (legenda):** Fig. 2.6. (A) Model 3D al servomotorului MG90s. (B) Amplasarea lui în sistem. [47]

- **[AF-2.15 | #72]** Deoarece sistemul are nevoie de o parte de control, este absolut necesară introducerea unui
- **[AF-2.16 | #73]** microcontroller Arduino UNO R3 în proiectarea sistemului protetic.
- **[AF-2.17 | #74]** Pentru a-și putea îndeplinii toate funcțiile, dar și din motive de cost, sau estetice, Arduino UNO R3 va fi amplasat la baza pilonului, la distanță cât mai mică atât de servo motor. Schema 3D a microcontroller-ului a fost preluată de pe platforma online GrabCAD.

**[FIGURA 27 — imagine inline]** (fara legenda in paragraful imaginii)


**[FIGURA 28] (legenda):** Fig. 2.7. Modelul 3D al sistemului protetic cu microcontroller-ul și servo-motorul
