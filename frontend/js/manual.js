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
const resultModal = document.createElement('div'); // placeholder if you had a modal elsewhere

function isFilled(el){
  if(!el) return false;
  if(el.type === 'checkbox') return el.checked;
  if(el.tagName && el.tagName.toLowerCase() === 'select') return (el.value || '') !== '';
  const v = (el.value || '').toString().trim();
  return v !== '';
}
const progressFields = [ els.gender, els.age, els.height, els.weight, els.systolic, els.diastolic, els.sleep, els.smoking, els.stress ];
function updateProgress(){
  const total = progressFields.length;
  const filled = progressFields.filter(isFilled).length;
  document.title = `Manual Entry — ${Math.round((filled/total)*100)}% complete`;
}

function calculateBMI(){
  const h = parseFloat(els.height.value), w = parseFloat(els.weight.value);
  if(isFinite(h) && isFinite(w) && h > 0){
    const bmi = +(w / ((h/100) ** 2));
    const b = bmi.toFixed(1);
    let label = '—';
    if(bmi < 18.5) label = 'Underweight';
    else if(bmi < 25) label = 'Normal';
    else if(bmi < 30) label = 'Overweight';
    else label = 'Obese';
    bmiBox.textContent = `BMI: ${b} (${label})`;
    s_bmi.textContent = `BMI: ${b} (${label})`;
    return bmi;
  } else {
    bmiBox.textContent = 'BMI: —';
    s_bmi.textContent = 'BMI: —';
    return null;
  }
}

function computeGeneralScore(){
  let score = 0;
  const bmi = calculateBMI();
  const sleep = parseFloat(els.sleep.value);
  const sys = parseFloat(els.systolic.value);
  const dia = parseFloat(els.diastolic.value);
  const age = parseFloat(els.age.value) || 0;

  if(bmi){
    if(bmi < 18.5) score += 1.0;
    else if(bmi < 25) score += 0.0;
    else if(bmi < 30) score += 1.5;
    else score += 3.0;
  }

  if(isFinite(sys) || isFinite(dia)){
    if((isFinite(sys) && sys >= 180) || (isFinite(dia) && dia >= 120)) score += 3.0;
    else if((isFinite(sys) && sys > 140) || (isFinite(dia) && dia > 90)) score += 2.0;
    else if((isFinite(sys) && sys > 130) || (isFinite(dia) && dia > 85)) score += 1.0;
    else if((isFinite(sys) && sys < 90) || (isFinite(dia) && dia < 60)) score += 1.2;
  }

  if(isFinite(sleep)){
    if(sleep < 4) score += 1.5;
    else if(sleep < 6) score += 0.6;
    else if(sleep > 9) score += 0.6;
  }

  if(els.chk_chest && els.chk_chest.checked) score += 1.5;
  if(els.chk_heart && els.chk_heart.checked) score += 2.5;
  if(els.chk_chol && els.chk_chol.checked) score += 1.2;
  if(els.chk_walk && els.chk_walk.checked) score += 1.0;
  if(els.chk_activity && els.chk_activity.checked) score -= 1.0;
  if(els.chk_alcohol && els.chk_alcohol.checked) score += 1.2;

  const smokingVal = (els.smoking && els.smoking.value) || '';
  if(smokingVal === 'current') score += 1.2;
  else if(smokingVal === 'former') score += 0.6;

  score += parseFloat(els.stress.value) || 0;
  if(age >= 60) score += 0.8;

  const raw = Math.max(0, Math.min(12, score));
  const scaled = Math.round((raw / 12) * 4);
  return { score: scaled, raw };
}

const generalStates = [
  { emoji: '💖', text: 'Excellent' },
  { emoji: '❤️', text: 'Good' },
  { emoji: '💓', text: 'Moderate' },
  { emoji: '💔', text: 'Poor' },
  { emoji: '🚨', text: 'Serious' }
];

function updateUIFromScore(){
  const g = computeGeneralScore();
  const gi = Math.max(0, Math.min(4, g.score));
  genEmoji.textContent = generalStates[gi].emoji;
  genText.textContent = generalStates[gi].text;

  genEmoji.style.transform = 'scale(1.14)';
  setTimeout(()=> genEmoji.style.transform = '', 320);

  const sys = els.systolic.value;
  const dia = els.diastolic.value;
  s_bp.textContent = (sys || dia) ? `BP: ${sys || '—'}/${dia || '—'} mmHg` : 'BP: —';

  const alcohol = (els.chk_alcohol && els.chk_alcohol.checked) ? 'Yes' : 'No';
  s_alcohol.textContent = `Alcohol: ${alcohol}`;
  s_general.textContent = generalStates[gi].text;

  legendRows.forEach((r, idx) => {
    if(r) r.classList.toggle('active', idx === gi);
  });
}

/* wire inputs */
const inputs = Array.from(document.querySelectorAll('#healthForm input, #healthForm select'));
inputs.forEach(i => {
  i.addEventListener('input', () => { updateProgress(); calculateBMI(); updateUIFromScore(); });
  i.addEventListener('change', () => { updateProgress(); calculateBMI(); updateUIFromScore(); });
});

/* initial run */
updateProgress();
calculateBMI();
updateUIFromScore();

/* buttons */
document.getElementById('calcNow').addEventListener('click', () => { updateProgress(); calculateBMI(); updateUIFromScore(); });
document.getElementById('healthForm').addEventListener('submit', (e) => {
  e.preventDefault();
  updateProgress();
  calculateBMI();
  updateUIFromScore();
  alert('Submitted (simulated).');
});
document.getElementById('submitBtn').addEventListener('click', () => {
  document.getElementById('healthForm').dispatchEvent(new Event('submit', { cancelable: true }));
});
