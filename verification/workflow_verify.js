export const meta = {
  name: 'verificare-raport-cs4',
  description: 'Verifică afirmațiile din Raportul CS4 (cap. III-V) contra codului și rezultatelor reale ale proiectului easy-gait',
  whenToUse: 'Verificare factuală multi-agent a unui raport tehnic contra implementării reale',
  phases: [
    { title: '0-Dosar proiect', detail: '2 agenți Opus 4.8 care descoperă singuri tot proiectul (cod + rezultate) și produc ground-truth structurat', model: 'opus' },
    { title: '1-Verificare WU', detail: 'câte un agent Opus 4.8 per work-unit (sub-secțiune): verdict pe fiecare afirmație + lacune + figuri/tabele', model: 'opus' },
    { title: '2-Refutare', detail: 'agent adversarial Opus 4.8 care încearcă să refute constatările critice (CONTRAZIS / lacună majoră)', model: 'opus' },
    { title: '3-Sinteză capitol', detail: 'consolidare per capitol (III, IV, V) într-un raport final acționabil — Opus 4.8', model: 'opus' },
  ],
}

const ROOT = 'D:/OneDrive - Realworld Holding b.v/Documents/67'
const REPORTS = `${ROOT}/verification/reports`

// Normalizare defensivă a `args`: poate sosi ca {workunits:[...]}, ca [...] direct,
// sau ca string JSON. Eșuează clar dacă nu găsim un array.
let workunits
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = null } }
if (Array.isArray(_a)) workunits = _a
else if (_a && Array.isArray(_a.workunits)) workunits = _a.workunits
else if (_a && Array.isArray(_a.items)) workunits = _a.items
if (!Array.isArray(workunits) || workunits.length === 0) {
  throw new Error('args nu conține un array de work-units. Primit: ' + JSON.stringify(args).slice(0, 400))
}

// ──────────────────────────────────────────────────────────────────────────
// Context comun: cum trebuie să lucreze un agent care înțelege proiectul.
// NU primesc răspunsuri de-a gata — primesc HARTA fișierelor și REGULILE de
// verificare. Fiecare agent citește el însuși codul și datele.
// ──────────────────────────────────────────────────────────────────────────
const PROJECT_MAP = `
PROIECTUL (rădăcină: ${ROOT}):
- easy-gait/src/easy_gait/  ← codul sursă Python (sursa de adevăr a IMPLEMENTĂRII):
    preprocessing.py (filtru Butterworth, magnitudine accel), gait_events.py (Trojaniello + Maqbool),
    omc_events.py (Zeni 2008, aliniere OMC↔IMU), segmentation.py (cicluri, rejecție outlieri),
    parameters.py (cadență, stride, stance%, CV, Symmetry Index), fsm.py (FSM 5 stări + SETPOINTS),
    ankle_controller.py (traiectorie PCHIP), prosthesis_viz.py (animație 2D proteză),
    activity_compare.py, validation.py (MAE/RMSE/NRMSE/PCC/F1), io_utils.py, samala_metadata.py.
- easy-gait/notebooks/  ← scripturi de analiză (01..04) care PRODUC rezultatele:
    figs/ (fig01..fig12 PNG), tables/ (tab01..tab05 CSV/TXT cu rezultatele reale agregate).
- easy-gait/data/processed/  ← rezultatele numerice finale (sursa de adevăr a REZULTATELOR):
    events_validation.csv, fsm_validation.csv, wassall_per_trial.csv, wassall_per_terrain.csv, etc.
- easy-gait/data/raw/samala_2024/  ← date brute Samala (30 subiecți S01..S30, IMU CSV + OMC C3D).
- easy-gait/scripts/  ← validate_events_all.py, validate_fsm_all.py, compute_wassall_summary.py (pipeline-uri).
- easy-gait/dashboard/  ← app Streamlit (app.py + pages/1..6) — verifică afirmațiile despre dashboard aici.
- demo-web/  ← variantă web Flask a dashboard-ului.
- easy-gait/docs/  ← ATENȚIE: ALGORITHMS.md, DESIGN.md și PDF-ul de documentație sunt EXPLICAȚII, NU sursă de adevăr. NU le folosi pentru a confirma afirmații — descoperă singur adevărul din COD și REZULTATE.
- easy-gait/tests/  ← teste unitare (pot confirma comportamentul real al funcțiilor).
- datasets/  ← arhive brute Wassall (Pxx.zip) + Participant_info.xlsx.

REGULA DE AUR: sursa de adevăr este CODUL (src/) și REZULTATELE (data/processed/, notebooks/tables/).
Nu te baza pe documentația .md/.pdf. Citește implementarea reală linie cu linie și valorile reale din CSV.
`.trim()

// ──────────────────────────────────────────────────────────────────────────
// SCHEMAS
// ──────────────────────────────────────────────────────────────────────────
const DOSAR_SCHEMA = {
  type: 'object',
  required: ['rezumat', 'fapte', 'fisiere_cheie'],
  properties: {
    rezumat: { type: 'string', description: 'Sinteză 200-400 cuvinte: ce face proiectul, fluxul de date, ce rezultate produce.' },
    fapte: {
      type: 'array', description: 'Fapte atomice verificabile extrase DIRECT din cod/rezultate, cu citare fișier:linie sau fișier→valoare.',
      items: {
        type: 'object', required: ['fapt', 'sursa'],
        properties: {
          fapt: { type: 'string', description: 'Un fapt concret: parametru, prag, formulă, valoare numerică, comportament.' },
          sursa: { type: 'string', description: 'fișier:linie (cod) sau fișier→celulă/valoare (CSV).' },
        },
      },
    },
    fisiere_cheie: { type: 'array', items: { type: 'string' }, description: 'Lista fișierelor relevante citite, cu rol scurt.' },
    discrepante_interne: {
      type: 'array', items: { type: 'string' },
      description: 'Contradicții observate ÎNTRE cod și docstring-uri / între module (opțional).',
    },
  },
}

const VERIFY_SCHEMA = {
  type: 'object',
  required: ['work_unit', 'verdicte', 'lacune', 'figuri_tabele', 'concluzie_sectiune'],
  properties: {
    work_unit: { type: 'string' },
    verdicte: {
      type: 'array', description: 'Câte o intrare PER AFIRMAȚIE (AF-x.y) din work-unit.',
      items: {
        type: 'object',
        required: ['af_id', 'afirmatie_rezumat', 'verdict', 'dovada', 'explicatie'],
        properties: {
          af_id: { type: 'string', description: 'ex. AF-4.42' },
          afirmatie_rezumat: { type: 'string', description: 'Rezumat scurt al afirmației verificate.' },
          verdict: { type: 'string', enum: ['CONFIRMAT', 'PARTIAL', 'CONTRAZIS', 'NEVERIFICABIL'] },
          dovada: { type: 'string', description: 'Citare exactă: fișier:linie din cod SAU fișier→valoare din CSV care susține verdictul. Obligatoriu pentru CONFIRMAT/PARTIAL/CONTRAZIS.' },
          explicatie: { type: 'string', description: 'De ce acest verdict. Pentru CONTRAZIS/PARTIAL: exact ce diferă (valoarea din text vs. valoarea reală).' },
          severitate: { type: 'string', enum: ['critic', 'mediu', 'minor', 'n/a'], description: 'Cât de gravă e o eventuală eroare pentru corectitudinea lucrării.' },
        },
      },
    },
    figuri_tabele: {
      type: 'array', description: 'Verificarea fiecărei figuri/tabel menționate în work-unit.',
      items: {
        type: 'object', required: ['ref', 'exista', 'observatii'],
        properties: {
          ref: { type: 'string', description: 'ex. Fig. 4.3.1 / Tabel 5.1' },
          exista: { type: 'string', enum: ['da', 'nu', 'partial', 'neclar'], description: 'Există fișierul figurii/datele tabelului în proiect?' },
          sursa_fisier: { type: 'string', description: 'Calea către PNG/CSV-ul corespunzător, dacă există.' },
          observatii: { type: 'string', description: 'Valorile din figură/tabel se regăsesc în rezultatele reale? Discrepanțe?' },
        },
      },
    },
    lacune: {
      type: 'array', description: 'Informații prezente în COD/REZULTATE dar ABSENTE din text, care ar trebui adăugate.',
      items: {
        type: 'object', required: ['lacuna', 'propunere_text', 'importanta'],
        properties: {
          lacuna: { type: 'string', description: 'Ce lipsește din capitol.' },
          dovada_proiect: { type: 'string', description: 'fișier:linie / valoare care arată că informația există în proiect.' },
          propunere_text: { type: 'string', description: 'Text concret (în română, gata de inserat în Word) care acoperă lacuna.' },
          importanta: { type: 'string', enum: ['ridicata', 'medie', 'scazuta'] },
        },
      },
    },
    corecturi_redactare: {
      type: 'array', description: 'Reformulări pentru afirmațiile CONTRAZIS/PARTIAL/imprecise.',
      items: {
        type: 'object', required: ['af_id', 'text_original_problema', 'text_corectat'],
        properties: {
          af_id: { type: 'string' },
          text_original_problema: { type: 'string', description: 'Fragmentul problematic.' },
          text_corectat: { type: 'string', description: 'Varianta corectată, gata de copiat în Word.' },
        },
      },
    },
    concluzie_sectiune: { type: 'string', description: 'Verdict de ansamblu pe sub-secțiune: cât de solidă e, ce e urgent de reparat.' },
  },
}

const REFUTE_SCHEMA = {
  type: 'object',
  required: ['af_id', 'constatare_initiala', 'rezista', 'motivatie'],
  properties: {
    af_id: { type: 'string' },
    constatare_initiala: { type: 'string', description: 'Constatarea critică verificată (CONTRAZIS sau lacună majoră).' },
    rezista: { type: 'boolean', description: 'true = constatarea rezistă (eroarea e reală); false = constatarea e greșită / nejustificată.' },
    motivatie: { type: 'string', description: 'Dovada independentă (fișier:linie / valoare) care confirmă SAU infirmă constatarea inițială.' },
    verdict_final: { type: 'string', enum: ['CONFIRMAT', 'PARTIAL', 'CONTRAZIS', 'NEVERIFICABIL'], description: 'Verdictul corect după re-verificare.' },
  },
}

const SYNTH_SCHEMA = {
  type: 'object',
  required: ['capitol', 'scor_acuratete', 'rezumat_executiv', 'top_probleme', 'recomandari_de_scris'],
  properties: {
    capitol: { type: 'string' },
    scor_acuratete: { type: 'integer', description: '0-100: cât de factual corect e capitolul față de implementarea reală.' },
    rezumat_executiv: { type: 'string', description: 'Sinteză pentru autor: starea capitolului în 150-300 cuvinte.' },
    top_probleme: {
      type: 'array', description: 'Cele mai importante erori confirmate, ordonate după severitate.',
      items: {
        type: 'object', required: ['descriere', 'severitate', 'fix'],
        properties: {
          descriere: { type: 'string' },
          severitate: { type: 'string', enum: ['critic', 'mediu', 'minor'] },
          fix: { type: 'string', description: 'Cum se repară (text corect / valoare corectă).' },
        },
      },
    },
    recomandari_de_scris: {
      type: 'array', description: 'Ce ar trebui ADĂUGAT la capitol (din lacunele confirmate), cu text propus.',
      items: { type: 'string' },
    },
  },
}

// ──────────────────────────────────────────────────────────────────────────
// FAZA 0 — Dosarul proiectului (înțelegere profundă, descoperită singur)
// Doi agenți pe domenii diferite, în paralel, ca să acopere tot.
// ──────────────────────────────────────────────────────────────────────────
phase('0-Dosar proiect')

const dosarDomenii = [
  {
    label: 'dosar:algoritmi',
    focus: `IMPLEMENTAREA algoritmilor: preprocesare (Butterworth: ordin, cutoff-uri, filtfilt, padlen),
      magnitudine accelerație, detecție evenimente (Trojaniello: praguri, ferestre, scalare protetic;
      Maqbool R-GEDS: stări, praguri ω/accel, refractar), Zeni 2008 OMC, aliniere OMC↔IMU (cross-corelație),
      calcul unghi gleznă (compute_ankle_angle: convenție, calibrare, cutoff, clipping), segmentare (cicluri,
      rejecție outlieri 0.5-1.5×median), parametri (formule cadență/stride/CV/stance%/Symmetry Index),
      FSM (cele 5 stări, triggere, SETPOINTS pe activitate, timeout), traiectorie PCHIP (waypoint 30%, monotonie).
      Extrage TOATE valorile numerice/pragurile/formulele REALE din cod, cu fișier:linie.`,
  },
  {
    label: 'dosar:rezultate',
    focus: `REZULTATELE și DATELE: seturile de date (Samala: nr subiecți, fs, tip proteză, OMC; Wassall: nr
      participanți, terenuri, senzori; GaitRec), valorile reale din data/processed/*.csv și notebooks/tables/*
      (validare evenimente MAE/sens/F1 Trojaniello vs Maqbool; validare FSM/IMU RMSE/NRMSE/PCC; biomecanică
      protetic vs intact: cadență/stride/stance%/ROM; Wassall per teren: cadență/stride/CV/stance%).
      Verifică ce figuri (notebooks/figs/*.png) și tabele (notebooks/tables/*) există efectiv. Verifică și
      dashboard-ul (dashboard/pages/) și demo-web. Extrage TOATE valorile numerice REALE cu fișier→valoare.`,
  },
]

const dosare = await parallel(dosarDomenii.map(d => () =>
  agent(
    `Ești un inginer biomecanic + software senior. Trebuie să înțelegi PERFECT acest proiect citind SINGUR codul și rezultatele — NU te baza pe documentația .md/.pdf.\n\n${PROJECT_MAP}\n\nDOMENIUL TĂU: ${d.focus}\n\n` +
    `Citește fișierele relevante (folosește Read/Grep/Glob/Bash). Returnează un dosar structurat cu fapte ATOMICE, fiecare cu sursa exactă (fișier:linie pentru cod, fișier→valoare pentru CSV). Acest dosar va fi folosit ca referință de alți agenți care verifică afirmațiile din raport, deci trebuie să fie PRECIS și COMPLET pe domeniul tău.`,
    { label: d.label, phase: '0-Dosar proiect', schema: DOSAR_SCHEMA, agentType: 'Explore', model: 'opus' }
  )
))

const dosarText = dosare.filter(Boolean).map((d, i) => {
  const fapte = (d.fapte || []).map(f => `  - ${f.fapt}  [${f.sursa}]`).join('\n')
  const disc = (d.discrepante_interne || []).map(x => `  ! ${x}`).join('\n')
  return `### Dosar ${dosarDomenii[i].label}\n${d.rezumat}\n\nFAPTE:\n${fapte}\n${disc ? '\nDISCREPANȚE INTERNE OBSERVATE:\n' + disc : ''}`
}).join('\n\n')

log(`Dosar proiect gata: ${dosare.filter(Boolean).length}/2 domenii, ${dosare.filter(Boolean).reduce((s, d) => s + (d.fapte?.length || 0), 0)} fapte atomice extrase`)

// ──────────────────────────────────────────────────────────────────────────
// FAZA 1+2 — Verificare per work-unit, apoi refutarea adversarială a
// constatărilor critice. PIPELINE: fiecare WU trece prin verificare → refutare
// imediat ce verificarea lui e gata (fără barieră globală).
// ──────────────────────────────────────────────────────────────────────────
phase('1-Verificare WU')

const results = await pipeline(
  workunits,

  // STAGE 1: verificare afirmație cu afirmație
  (wu) => agent(
    `Ești verificator factual senior (biomecanică + software). Verifici un work-unit din Raportul CS4 contra IMPLEMENTĂRII și REZULTATELOR REALE ale proiectului.\n\n` +
    `${PROJECT_MAP}\n\n` +
    `=== DOSAR DE PROIECT (referință pre-construită de echipă; verifică-l TOTUȘI tu însuți în cod) ===\n${dosarText}\n\n` +
    `=== WORK-UNIT DE VERIFICAT: ${wu.id} — ${wu.title} ===\n${wu.content}\n\n` +
    `SARCINA:\n` +
    `1. Pentru FIECARE afirmație [AF-x.y] din work-unit: dă un verdict (CONFIRMAT / PARTIAL / CONTRAZIS / NEVERIFICABIL). ` +
    `Deschide fișierele reale din cod/CSV și citează DOVADA exactă (fișier:linie sau fișier→valoare). Pentru valori numerice (praguri, cutoff, MAE, RMSE, PCC, setpoints, nr. subiecți, fs etc.) compară cifra din text cu cifra REALĂ din cod/rezultate. Marchează severitatea erorilor.\n` +
    `2. Pentru fiecare FIGURĂ/TABEL menționat: verifică dacă există fișierul (notebooks/figs/, notebooks/tables/, data/processed/) și dacă valorile descrise corespund rezultatelor reale.\n` +
    `3. LACUNE: ce informație din cod/rezultate NU e menționată în capitol dar ar trebui (parametri importanți, justificări, limitări reale). Propune TEXT CONCRET în română, gata de inserat.\n` +
    `4. CORECTURI DE REDACTARE: pentru afirmațiile CONTRAZIS/PARTIAL/imprecise, scrie varianta corectată gata de copiat în Word.\n\n` +
    `Fii riguros și sceptic: o afirmație e CONFIRMAT doar dacă ai găsit dovada în cod/date. Dacă textul spune o cifră care nu se potrivește cu codul, e CONTRAZIS — citează ambele valori.`,
    { label: `verify:${wu.id}`, phase: '1-Verificare WU', schema: VERIFY_SCHEMA, model: 'opus' }
  ),

  // STAGE 2: refutare adversarială DOAR a constatărilor critice
  async (review, wu) => {
    if (!review) return null
    const critice = (review.verdicte || []).filter(v => v.verdict === 'CONTRAZIS' && (v.severitate === 'critic' || v.severitate === 'mediu'))
    const lacuneMari = (review.lacune || []).filter(l => l.importanta === 'ridicata')

    // Refută fiecare constatare critică, independent (paralel)
    const refutari = await parallel(critice.map(c => () =>
      agent(
        `Ești AVOCATUL DIAVOLULUI. Un coleg a marcat o afirmație din Raportul CS4 ca eroare (CONTRAZIS). ` +
        `Sarcina ta: încearcă din toate puterile să REFUȚI această constatare — poate colegul a citit greșit codul, a confundat un parametru, sau afirmația din text e de fapt corectă într-o interpretare rezonabilă.\n\n` +
        `${PROJECT_MAP}\n\n` +
        `AFIRMAȚIA: ${c.af_id} — ${c.afirmatie_rezumat}\n` +
        `CONSTATAREA COLEGULUI: ${c.explicatie}\n` +
        `DOVADA INVOCATĂ: ${c.dovada}\n\n` +
        `Verifică TU ÎNSUȚI în cod/date. Dacă găsești că eroarea e reală și rezistă, spune rezista=true. Dacă afirmația e de fapt corectă (sau parțial), spune rezista=false și dă verdictul corect. Citează dovada ta independentă.`,
        { label: `refute:${wu.id}:${c.af_id}`, phase: '2-Refutare', schema: REFUTE_SCHEMA, model: 'opus' }
      )
    ))
    return { review, refutari: refutari.filter(Boolean), wu_id: wu.id }
  }
)

// Aplică refutările peste verdicte (corectează fals-pozitivele)
const finalResults = results.filter(Boolean).map(r => {
  const review = r.review
  const refMap = {}
  for (const rf of (r.refutari || [])) refMap[rf.af_id] = rf
  const verdicteAjustate = (review.verdicte || []).map(v => {
    const rf = refMap[v.af_id]
    if (rf && !rf.rezista) {
      return { ...v, verdict: rf.verdict_final, explicatie: `${v.explicatie}  ⟶ [REVIZUIT după refutare: ${rf.motivatie}]`, refutat: true }
    }
    if (rf && rf.rezista) {
      return { ...v, explicatie: `${v.explicatie}  ⟶ [CONFIRMAT și de al 2-lea verificator: ${rf.motivatie}]`, dublu_confirmat: true }
    }
    return v
  })
  return { ...review, verdicte: verdicteAjustate }
})

log(`Verificare gata: ${finalResults.length} work-units, ${finalResults.reduce((s, r) => s + (r.verdicte?.length || 0), 0)} afirmații verificate`)

// ──────────────────────────────────────────────────────────────────────────
// FAZA 3 — Sinteză per capitol (III, IV, V)
// ──────────────────────────────────────────────────────────────────────────
phase('3-Sinteză capitol')

const byChapter = {}
for (const r of finalResults) {
  // deduce capitolul din work_unit (ex. "WU-IV-03" -> "IV")
  const m = (r.work_unit || '').match(/WU-([A-Z]+)/)
  const ch = m ? m[1] : 'misc'
  ;(byChapter[ch] = byChapter[ch] || []).push(r)
}

const sinteze = await parallel(Object.entries(byChapter).map(([ch, revs]) => () => {
  const dump = revs.map(r => {
    const v = (r.verdicte || []).map(x => `  [${x.verdict}${x.severitate && x.severitate !== 'n/a' ? '/' + x.severitate : ''}] ${x.af_id}: ${x.afirmatie_rezumat} — ${x.explicatie} (${x.dovada || ''})`).join('\n')
    const l = (r.lacune || []).map(x => `  LACUNĂ[${x.importanta}]: ${x.lacuna} → propunere: ${x.propunere_text}`).join('\n')
    const ft = (r.figuri_tabele || []).map(x => `  ${x.ref}: există=${x.exista} — ${x.observatii}`).join('\n')
    const cr = (r.corecturi_redactare || []).map(x => `  CORECTURĂ ${x.af_id}: «${x.text_original_problema}» → «${x.text_corectat}»`).join('\n')
    return `### ${r.work_unit}\nConcluzie: ${r.concluzie_sectiune}\nVERDICTE:\n${v}\nFIGURI/TABELE:\n${ft}\nLACUNE:\n${l}\nCORECTURI:\n${cr}`
  }).join('\n\n')

  return agent(
    `Ești redactor-șef tehnic. Consolidează verificările sub-secțiunilor Capitolului ${ch} din Raportul CS4 într-un raport final ACȚIONABIL pentru autoare (studentă masterand).\n\n` +
    `Pe baza verdictelor de mai jos, dă: un scor de acuratețe (0-100), un rezumat executiv, lista TOP probleme confirmate (ordonate după severitate, cu fix concret) și recomandări de SCRIS (ce să adauge, cu text propus în română). Nu inventa — folosește doar ce e în verdicte.\n\n` +
    `=== VERIFICĂRI CAPITOL ${ch} ===\n${dump}`,
    { label: `synth:cap-${ch}`, phase: '3-Sinteză capitol', schema: SYNTH_SCHEMA, model: 'opus' }
  )
}))

// ──────────────────────────────────────────────────────────────────────────
// RETURN — date structurate pe care main-loop le scrie în fișiere .md
// ──────────────────────────────────────────────────────────────────────────
return {
  dosare: dosare.filter(Boolean),
  workunit_reports: finalResults,
  syntheses: sinteze.filter(Boolean),
  stats: {
    work_units: finalResults.length,
    afirmatii_verificate: finalResults.reduce((s, r) => s + (r.verdicte?.length || 0), 0),
    contrazis: finalResults.reduce((s, r) => s + (r.verdicte || []).filter(v => v.verdict === 'CONTRAZIS').length, 0),
    partial: finalResults.reduce((s, r) => s + (r.verdicte || []).filter(v => v.verdict === 'PARTIAL').length, 0),
    lacune: finalResults.reduce((s, r) => s + (r.lacune?.length || 0), 0),
  },
}
