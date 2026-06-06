export const meta = {
  name: 'verificare-text-adaugat-cs4',
  description: 'Verifică fiecare secțiune tehnică REscrisă în Raportul CS4 contra codului real easy-gait, pentru a confirma zero discrepanțe',
  phases: [
    { title: '1-Verificare secțiuni', detail: 'câte un agent Opus 4.8 per secțiune rescrisă: verifică fiecare afirmație contra codului', model: 'opus' },
    { title: '2-Discrepanțe critice', detail: 'agent adversarial Opus 4.8 re-verifică discrepanțele raportate', model: 'opus' },
    { title: '3-Sinteză', detail: 'consolidare: listă finală de discrepanțe confirmate + verdict', model: 'opus' },
  ],
}

const ROOT = 'D:/OneDrive - Realworld Holding b.v/Documents/67'

// Normalizare defensivă a `args` (poate sosi ca {sections:[...]}, [...] sau string JSON)
let sections
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = null } }
if (Array.isArray(_a)) sections = _a
else if (_a && Array.isArray(_a.sections)) sections = _a.sections
if (!Array.isArray(sections) || sections.length === 0) {
  throw new Error('args nu conține un array de secțiuni. Primit: ' + JSON.stringify(args).slice(0, 300))
}

const PROJECT_MAP = `
Cod sursă (sursa de adevăr): ${ROOT}/easy-gait/src/easy_gait/
  preprocessing.py, gait_events.py, omc_events.py, segmentation.py, parameters.py,
  fsm.py, ankle_controller.py (+ bucla impedanță observed_angle_from_impedance), io_utils.py,
  gait_profile.py, validation.py (+ event_mae_windowed). samala_metadata.py (metadata subiecți).
Rezultate reale: ${ROOT}/easy-gait/data/processed/*.csv (events_validation.csv, events_validation_v2.csv,
  fsm_validation.csv, fsm_validation_v2.csv, wassall_per_terrain.csv), notebooks/tables/tab01..05.
Date brute: ${ROOT}/easy-gait/data/raw/samala_2024/ ; ${ROOT}/datasets/ (Wassall) ; dataverse_README.txt.
REGULA: verifică în COD și REZULTATE, nu în PDF-uri de documentație. Citează fișier:linie / fișier→valoare.
`.trim()

const VERIFY_SCHEMA = {
  type: 'object',
  required: ['sectiune', 'discrepante', 'verdict'],
  properties: {
    sectiune: { type: 'string' },
    discrepante: {
      type: 'array',
      description: 'Orice afirmație din text care NU se potrivește exact cu codul/rezultatele. Gol dacă totul e corect.',
      items: {
        type: 'object',
        required: ['afirmatie', 'problema', 'corect', 'sursa', 'severitate'],
        properties: {
          afirmatie: { type: 'string', description: 'Fragmentul din text care e greșit/imprecis.' },
          problema: { type: 'string', description: 'Ce e greșit.' },
          corect: { type: 'string', description: 'Valoarea/formularea corectă conform codului.' },
          sursa: { type: 'string', description: 'fișier:linie sau fișier→valoare care dovedește.' },
          severitate: { type: 'string', enum: ['critic', 'mediu', 'minor'] },
        },
      },
    },
    afirmatii_confirmate: { type: 'integer', description: 'Câte afirmații verificabile au fost confirmate corecte.' },
    verdict: { type: 'string', description: 'Rezumat: secțiunea e fidelă codului? Ce trebuie corectat?' },
  },
}

const REFUTE_SCHEMA = {
  type: 'object',
  required: ['rezista', 'motivatie'],
  properties: {
    rezista: { type: 'boolean', description: 'true = discrepanța e reală; false = textul era de fapt corect.' },
    motivatie: { type: 'string' },
    corect_final: { type: 'string' },
  },
}

const SYNTH_SCHEMA = {
  type: 'object',
  required: ['scor_fidelitate', 'discrepante_confirmate', 'rezumat'],
  properties: {
    scor_fidelitate: { type: 'integer', description: '0-100: cât de fidel codului e textul adăugat.' },
    discrepante_confirmate: {
      type: 'array',
      items: {
        type: 'object',
        required: ['sectiune', 'problema', 'fix', 'severitate'],
        properties: {
          sectiune: { type: 'string' }, problema: { type: 'string' },
          fix: { type: 'string' }, severitate: { type: 'string' },
        },
      },
    },
    rezumat: { type: 'string', description: 'Verdict final pentru autor: e gata de predat? Ce mai trebuie atins?' },
  },
}

// ── FAZA 1: verificare per secțiune (pipeline cu refutare imediată) ──────────
phase('1-Verificare secțiuni')

const results = await pipeline(
  sections,
  (s) => agent(
    `Ești verificator factual senior. Verifici o secțiune REscrisă din Raportul CS4 contra codului REAL al proiectului. Pentru FIECARE afirmație verificabilă (parametru, prag, formulă, cifră, comportament), deschide fișierul real și confirmă sau infirmă. Raportează DOAR discrepanțele (lucruri care nu se potrivesc cu codul); dacă totul e corect, lista de discrepanțe e goală.\n\n` +
    `${PROJECT_MAP}\n\n=== SECȚIUNE: ${s.id} (${s.anchor}) ===\n${s.text}`,
    { label: `verify:${s.id}`, phase: '1-Verificare secțiuni', model: 'opus', schema: VERIFY_SCHEMA }
  ),
  async (rev, s) => {
    if (!rev) return null
    const critice = (rev.discrepante || []).filter(d => d.severitate === 'critic' || d.severitate === 'mediu')
    const verified = await parallel(critice.map(d => () =>
      agent(
        `Avocatul diavolului: un coleg a marcat o discrepanță într-un text tehnic. Verifică TU în cod dacă e reală sau dacă textul era corect.\n\n` +
        `AFIRMAȚIA: ${d.afirmatie}\nPROBLEMA RAPORTATĂ: ${d.problema}\nCORECT (zice colegul): ${d.corect}\nSURSA: ${d.sursa}\n\n${PROJECT_MAP}`,
        { label: `refute:${s.id}`, phase: '2-Discrepanțe critice', model: 'opus', schema: REFUTE_SCHEMA }
      ).then(v => ({ ...d, verdict_refutare: v }))
    ))
    return { ...rev, discrepante_verificate: verified.filter(Boolean) }
  }
)

const clean = results.filter(Boolean)
log(`Verificare gata: ${clean.length} sectiuni, ${clean.reduce((s, r) => s + (r.discrepante?.length || 0), 0)} discrepante brute`)

// ── FAZA 3: sinteză ─────────────────────────────────────────────────────────
phase('3-Sinteză')
const dump = clean.map(r => {
  const disc = (r.discrepante_verificate || r.discrepante || []).map(d => {
    const rf = d.verdict_refutare
    const status = rf ? (rf.rezista ? 'CONFIRMATĂ' : 'INFIRMATĂ (text corect)') : 'neverificată-adversarial'
    return `  [${d.severitate}/${status}] ${d.problema} → corect: ${rf && !rf.rezista ? rf.corect_final : d.corect} (${d.sursa})`
  }).join('\n')
  return `### ${r.sectiune}\nConfirmate corecte: ${r.afirmatii_confirmate || '?'}\nVerdict: ${r.verdict}\nDiscrepanțe:\n${disc || '  (niciuna)'}`
}).join('\n\n')

const synth = await agent(
  `Ești redactor-șef. Consolidează verificarea secțiunilor tehnice rescrise în Raportul CS4. Păstrează DOAR discrepanțele CONFIRMATE adversarial (ignoră-le pe cele infirmate). Dă un scor de fidelitate (0-100) și un verdict final clar: e textul gata de predat sau mai sunt corecturi de făcut?\n\n=== VERIFICĂRI ===\n${dump}`,
  { label: 'sinteza-finala', phase: '3-Sinteză', model: 'opus', schema: SYNTH_SCHEMA }
)

return { sections: clean, synthesis: synth }
