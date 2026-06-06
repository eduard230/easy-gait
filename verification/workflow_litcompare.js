export const meta = {
  name: 'comparatie-literatura-v2',
  description: 'Compară rezultatele îmbunătățite (v2) ale proiectului easy-gait cu valorile din literatura de specialitate, cu surse verificabile',
  phases: [
    { title: '0-Verificare cod', detail: 'agent care verifică Opus 4.8 că îmbunătățirile v2 sunt implementate corect și onest în cod', model: 'opus' },
    { title: '1-Research literatură', detail: '3 agenți Opus 4.8 care caută pe net valori exacte din literatură (detecție evenimente, control impedanță, validare profil) cu surse', model: 'opus' },
    { title: '2-Tabel comparativ', detail: 'agent Opus 4.8 care construiește tabelul side-by-side rezultate-vs-literatură și verdictul', model: 'opus' },
    { title: '3-Refutare', detail: 'agent adversarial Opus 4.8 care verifică dacă concluziile rezistă', model: 'opus' },
  ],
}

const ROOT = 'D:/OneDrive - Realworld Holding b.v/Documents/67'
const R = args.results   // cifrele v2 agregate

const RESULTS_TEXT = JSON.stringify(R, null, 2)

const CONTEXT = `
PROIECT: easy-gait — analiza mersului + control FSM gleznă protetică transtibială (dataset Samala 2024, 29 subiecți, IMU+OMC 200 Hz).
S-au implementat ÎMBUNĂTĂȚIRI (v2) față de validarea inițială:

A. DETECȚIE EVENIMENTE HS/TO (validate_events_v2.py, validation.py):
   - Evaluare pe FEREASTRA OMC (evenimentele IMU restrânse la intervalul ~4.5s acoperit de OMC, nu pe tot trial-ul de 14s) — elimină fals-pozitivele artificiale.
   - Corecție de BIAS median (decalaj sistematic IMU vs definiția Zeni-OMC).
B. VALIDARE FSM (validate_fsm_v2.py, ankle_controller.py, gait_profile.py):
   - BUCLA DE IMPEDANȚĂ: θ_obs = θ_eq + M_GRF/K (model GRF normativ scalat la greutatea reală), în loc de a compara echilibrul brut θ_eq cu OMC.
   - VALIDARE PE FORMĂ DE PROFIL: profil FSM normalizat (0-100%) vs banda ±1SD a piciorului intact (357 cicluri OMC).

REZULTATE v2 (agregate, 29 subiecți Samala):
${RESULTS_TEXT}

INTERPRETARE de verificat:
- Detecție: PPV a crescut de la ~0.28 la ~0.65-0.70, F1 de la ~0.38 la ~0.61-0.67, MAE după debias ~26-30 ms (de la ~60-80 ms). Sensibilitatea a rămas ~0.58-0.65 (nu a fost umflată artificial).
- FSM impedanță: PCC a trecut de la -0.22 (echilibru brut) la +0.11 (cu bucla de impedanță); RMSE 12.5°→8.3°. Asta confirmă că PCC negativ din v1 era artefact al metricii greșite.
- Profil: acoperire ±1SD doar 25% — FSM-ul de impedanță NU imită forma cinematică intactă (așteptat: e controller de impedanță, nu trajectory-tracking).
`.trim()

const RESEARCH_SCHEMA = {
  type: 'object',
  required: ['domeniu', 'valori_literatura', 'verdict_incadrare'],
  properties: {
    domeniu: { type: 'string' },
    valori_literatura: {
      type: 'array',
      items: {
        type: 'object',
        required: ['sursa', 'metrica', 'valoare', 'context'],
        properties: {
          sursa: { type: 'string', description: 'Autor an + titlu scurt + URL/DOI dacă există.' },
          metrica: { type: 'string', description: 'ex. MAE HS, sensibilitate, RMSE ankle, PCC.' },
          valoare: { type: 'string', description: 'Valoarea exactă raportată (cu unitate).' },
          context: { type: 'string', description: 'Populație (amputați/sănătoși), senzor, condiții.' },
        },
      },
    },
    verdict_incadrare: { type: 'string', description: 'Se încadrează rezultatele noastre v2 în literatură? Unde stau (mai bine/comparabil/mai slab)?' },
    surse_url: { type: 'array', items: { type: 'string' } },
  },
}

const TABLE_SCHEMA = {
  type: 'object',
  required: ['tabel_comparativ', 'verdict_global', 'puncte_forte', 'limitari_ramase'],
  properties: {
    tabel_comparativ: {
      type: 'array', description: 'Rânduri side-by-side: metrica noastră vs literatură.',
      items: {
        type: 'object',
        required: ['metrica', 'rezultat_nostru', 'literatura', 'sursa', 'incadrare'],
        properties: {
          metrica: { type: 'string' },
          rezultat_nostru: { type: 'string' },
          literatura: { type: 'string' },
          sursa: { type: 'string' },
          incadrare: { type: 'string', enum: ['mai bine', 'comparabil', 'in interval', 'sub literatura', 'n/a'] },
        },
      },
    },
    verdict_global: { type: 'string', description: 'Concluzie onestă 150-300 cuvinte: sunt rezultatele bune raportat la literatură?' },
    puncte_forte: { type: 'array', items: { type: 'string' } },
    limitari_ramase: { type: 'array', items: { type: 'string' } },
    text_pentru_lucrare: { type: 'string', description: 'Paragraf gata de inserat în Word (română) cu rezultatele v2 + comparația literatură + citări.' },
  },
}

const REFUTE_SCHEMA = {
  type: 'object',
  required: ['concluzie_rezista', 'observatii'],
  properties: {
    concluzie_rezista: { type: 'boolean' },
    observatii: { type: 'string', description: 'Ce e solid, ce e exagerat, ce trebuie nuanțat în verdictul global.' },
    corecturi: { type: 'array', items: { type: 'string' } },
  },
}

// ── FAZA 0: verificare cod ──────────────────────────────────────────────────
phase('0-Verificare cod')
const codeCheck = await agent(
  `Verifică în codul real (${ROOT}/easy-gait/) că îmbunătățirile v2 sunt implementate CORECT și ONEST (nu trucuri care umflă cifrele):\n` +
  `- validation.py: event_mae_windowed + restrict_to_window (fereastra OMC + debias)\n` +
  `- ankle_controller.py: observed_angle_from_impedance, grf_vertical_profile (bucla impedanță)\n` +
  `- gait_profile.py: build_mean_profile, profile_shape_metrics (validare pe formă)\n` +
  `- scripts/validate_events_v2.py și validate_fsm_v2.py (pipeline-uri)\n\n` +
  `Confirmă în special: (1) restrângerea la fereastra OMC e corectă metodologic (nu aruncă evenimente reale din interiorul ferestrei)? (2) corecția de bias e median, nu cherry-picking? (3) sensibilitatea NU a fost umflată artificial? (4) bucla de impedanță folosește un model GRF plauzibil? Citează fișier:linie.\n\n${CONTEXT}`,
  { label: 'verif-cod-v2', phase: '0-Verificare cod', model: 'opus',
    schema: { type: 'object', required: ['implementare_corecta', 'observatii'], properties: {
      implementare_corecta: { type: 'boolean' },
      observatii: { type: 'string' },
      probleme: { type: 'array', items: { type: 'string' } } } } }
)

// ── FAZA 1: research literatură (3 domenii, paralel) ────────────────────────
phase('1-Research literatură')
const domenii = [
  { label: 'lit:detectie-evenimente', focus: 'Detecția evenimentelor de mers HS/TO din IMU/giroscop shank la AMPUTAȚI (transtibial/transfemural) vs ground-truth (OMC/GRF). Caută valori EXACTE: MAE/timing error (ms), sensibilitate/recall, PPV/precision, F1. Surse țintă: Maqbool 2017 (IEEE TNSRE 25:1500), Pacini Panebianco 2018 (Gait Posture 66:76), Trojaniello 2014, plus orice studiu 2019-2025 pe amputați. Compară cu rezultatele noastre v2.' },
  { label: 'lit:control-impedanta', focus: 'Controlul de impedanță FSM pentru gleznă protetică activă și CUM se validează. Caută: cum evaluează Sup/Bohara/Goldfarb 2008, Au & Herr 2008, Lawson/Goldfarb controllerele (formă de profil cuplu/unghi/putere vs healthy band, NU corelație de traiectorie). Valori RMSE unghi gleznă raportate. Confirmă dacă PCC negativ între setpoint impedanță și unghi observat e cunoscut/așteptat. Compară cu v2 (impedanță PCC +0.11).' },
  { label: 'lit:unghi-imu-profil', focus: 'Acuratețea estimării unghiului gleznei din IMU single-sensor vs OMC (RMSE °, PCC) la mers, și folosirea benzii ±1SD a profilului normalizat la 0-100% gait cycle ca metodă de validare (Perry & Burnfield, Winter). Valori RMSE/PCC publicate. Compară cu v2 (IMU RMSE 8.1°, PCC 0.65).' },
]
const research = await parallel(domenii.map(d => () =>
  agent(
    `Ești cercetător biomecanic. Caută pe net (WebSearch/WebFetch) valori NUMERICE EXACTE din literatură pe domeniul tău, cu surse verificabile (DOI/URL). Apoi spune dacă rezultatele noastre v2 se încadrează.\n\nDOMENIU: ${d.focus}\n\n${CONTEXT}`,
    { label: d.label, phase: '1-Research literatură', model: 'opus', schema: RESEARCH_SCHEMA }
  )
))

const researchText = research.filter(Boolean).map(r => {
  const vals = (r.valori_literatura || []).map(v => `    - ${v.metrica}: ${v.valoare} [${v.sursa}] (${v.context})`).join('\n')
  return `### ${r.domeniu}\n${vals}\nÎncadrare: ${r.verdict_incadrare}`
}).join('\n\n')

// ── FAZA 2: tabel comparativ + verdict ──────────────────────────────────────
phase('2-Tabel comparativ')
const tableResult = await agent(
  `Ești redactor științific. Pe baza valorilor din literatură găsite de echipă și a rezultatelor noastre v2, construiește un TABEL COMPARATIV side-by-side (metrica noastră vs literatură vs sursă, cu încadrare), un verdict global ONEST și un paragraf gata de inserat în lucrare.\n\n` +
  `Nu inventa cifre — folosește doar valorile din research. Fii sincer: unde suntem mai buni, unde comparabili, unde mai slabi.\n\n` +
  `${CONTEXT}\n\n=== VALORI DIN LITERATURĂ (research echipă) ===\n${researchText}\n\n` +
  `=== VERIFICARE COD v2 ===\n${codeCheck.implementare_corecta ? 'Implementare confirmată corectă.' : 'PROBLEME!'} ${codeCheck.observatii}`,
  { label: 'tabel-comparativ', phase: '2-Tabel comparativ', model: 'opus', schema: TABLE_SCHEMA }
)

// ── FAZA 3: refutare ─────────────────────────────────────────────────────────
phase('3-Refutare')
const refute = await agent(
  `Ești recenzent critic (peer reviewer sceptic). Verifică dacă verdictul global de mai jos rezistă sau e prea optimist. Pune la îndoială fiecare „încadrare în literatură". Verifică în cod/date dacă e cazul (${ROOT}/easy-gait/).\n\n` +
  `VERDICT DE EVALUAT: ${tableResult.verdict_global}\n\n` +
  `TABEL: ${JSON.stringify(tableResult.tabel_comparativ)}\n\n${CONTEXT}`,
  { label: 'refutare-verdict', phase: '3-Refutare', model: 'opus', schema: REFUTE_SCHEMA }
)

return {
  code_check: codeCheck,
  research: research.filter(Boolean),
  comparison: tableResult,
  refutation: refute,
}
