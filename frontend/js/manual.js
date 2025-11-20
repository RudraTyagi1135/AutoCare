/* ============================
   Element References
============================ */
const els = {
  gender: document.getElementById('gender'),
  age: document.getElementById('age'),
  height: document.getElementById('height'),
  weight: document.getElementById('weight'),
  systolic: document.getElementById('systolic'),
  diastolic: document.getElementById('diastolic'),
  sleep: document.getElementById('sleep'),
  chk_chest: document.getElementById('chk_chest'),
  chk_heart: document.getElementById('chk_heart'),
  chk_chol: document.getElementById('chk_chol'),
  chk_walk: document.getElementById('chk_walk'),
  chk_activity: document.getElementById('chk_activity'),
  chk_alcohol: document.getElementById('chk_alcohol'),
  smoking: document.getElementById('smoking'),
  stress: document.getElementById('stress')
};

const bmiBox = document.getElementById('bmiBox');
const genEmoji = document.getElementById('genEmoji');
const genText = document.getElementById('genText');
const s_bmi = document.getElementById('s_bmi');
const s_bp = document.getElementById('s_bp');
const s_alcohol = document.getElementById('s_alcohol');
const s_general = document.getElementById('s_general');
const legendRows = [
  document.getElementById('legend0'),
  document.getElementById('legend1'),
  document.getElementById('legend2'),
  document.getElementById('legend3'),
  document.getElementById('legend4')
];

/* ============================
   Helpers
============================ */
function isFilled(el) {
  if (!el) return false;
  if (el.type === 'checkbox') return el.checked;
  if (el.tagName.toLowerCase() === 'select') return el.value.trim() !== '';
  return el.value.trim() !== '';
}

const progressFields = [
  els.gender, els.age, els.height, els.weight,
  els.systolic, els.diastolic, els.sleep, els.smoking, els.stress
];

function updateProgress() {
  const total = progressFields.length;
  const filled = progressFields.filter(isFilled).length;
  document.title = `Manual Entry — ${Math.round((filled / total) * 100)}% complete`;
}

/* ============================
   BMI Calculation
============================ */
function calculateBMI() {
  const h = parseFloat(els.height.value);
  const w = parseFloat(els.weight.value);

  if (isFinite(h) && isFinite(w) && h > 0) {
    const bmi = +(w / ((h / 100) ** 2));
    const val = bmi.toFixed(1);

    let label = '—';
    if (bmi < 18.5) label = 'Underweight';
    else if (bmi < 25) label = 'Normal';
    else if (bmi < 30) label = 'Overweight';
    else label = 'Obese';

    bmiBox.textContent = `BMI: ${val} (${label})`;
    s_bmi.textContent = `BMI: ${val} (${label})`;
    return bmi;
  }

  bmiBox.textContent = 'BMI: —';
  s_bmi.textContent = 'BMI: —';
  return null;
}

/* ============================
   General Score
============================ */
function computeGeneralScore() {
  let score = 0;
  const bmi = calculateBMI();
  const sleep = parseFloat(els.sleep.value);
  const sys = parseFloat(els.systolic.value);
  const dia = parseFloat(els.diastolic.value);
  const age = parseFloat(els.age.value) || 0;

  if (bmi) {
    if (bmi < 18.5) score += 1.0;
    else if (bmi < 25) score += 0.0;
    else if (bmi < 30) score += 1.5;
    else score += 3.0;
  }

  if (isFinite(sys) || isFinite(dia)) {
    if (sys >= 180 || dia >= 120) score += 3.0;
    else if (sys > 140 || dia > 90) score += 2.0;
    else if (sys > 130 || dia > 85) score += 1.0;
    else if (sys < 90 || dia < 60) score += 1.2;
  }

  if (isFinite(sleep)) {
    if (sleep < 4) score += 1.5;
    else if (sleep < 6) score += 0.6;
    else if (sleep > 9) score += 0.6;
  }

  if (els.chk_chest.checked) score += 1.5;
  if (els.chk_heart.checked) score += 2.5;
  if (els.chk_chol.checked) score += 1.2;
  if (els.chk_walk.checked) score += 1.0;
  if (els.chk_activity.checked) score -= 1.0;
  if (els.chk_alcohol.checked) score += 1.2;

  if (els.smoking.checked) score += 1.2;
  score += parseFloat(els.stress.value) || 0;

  if (age >= 60) score += 0.8;

  const raw = Math.max(0, Math.min(12, score));
  const scaled = Math.round((raw / 12) * 4);
  return { score: scaled, raw };
}

/* ============================
   UI Update
============================ */
const generalStates = [
  { emoji: '💖', text: 'Excellent' },
  { emoji: '❤️', text: 'Good' },
  { emoji: '💓', text: 'Moderate' },
  { emoji: '💔', text: 'Poor' },
  { emoji: '🚨', text: 'Serious' }
];

function updateUIFromScore() {
  const g = computeGeneralScore();
  const idx = Math.max(0, Math.min(4, g.score));
  genEmoji.textContent = generalStates[idx].emoji;
  genText.textContent = generalStates[idx].text;

  const sys = els.systolic.value;
  const dia = els.diastolic.value;
  s_bp.textContent = (sys || dia)
    ? `BP: ${sys || '—'}/${dia || '—'} mmHg`
    : 'BP: —';

  s_alcohol.textContent = `Alcohol: ${els.chk_alcohol.checked ? 'Yes' : 'No'}`;
  s_general.textContent = generalStates[idx].text;

  legendRows.forEach((row, i) => {
    row.classList.toggle('active', i === idx);
  });
}

/* ============================
   Input Event Wiring
============================ */
document.querySelectorAll('#healthForm input, #healthForm select')
  .forEach(input => {
    input.addEventListener('input', () => {
      updateProgress();
      calculateBMI();
      updateUIFromScore();
    });
    input.addEventListener('change', () => {
      updateProgress();
      calculateBMI();
      updateUIFromScore();
    });
  });

/* ============================
   Initial Load
============================ */
updateProgress();
calculateBMI();
updateUIFromScore();

/* ============================
   Submit Handler (REAL submit)
============================ */
document.getElementById('healthForm').addEventListener('submit', () => {
  updateProgress();
  calculateBMI();
  updateUIFromScore();
  // Form now submits normally to Flask
});
