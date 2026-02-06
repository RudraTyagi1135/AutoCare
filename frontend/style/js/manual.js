const els = {
  gender: document.getElementById('gender'),
  age: document.getElementById('age'),
  height: document.getElementById('height'),
  weight: document.getElementById('weight'),
  systolic: document.getElementById('systolic'),
  diastolic: document.getElementById('diastolic'),
  sleeptime: document.getElementById('sleep'),
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

function calculateBMI() {
  const h = parseFloat(els.height.value || 0);
  const w = parseFloat(els.weight.value || 0);

  if (h > 0 && w > 0) {
    const bmi = w / ((h / 100) ** 2);
    const val = bmi.toFixed(1);

    let label = 'Normal';
    if (bmi < 18.5) label = 'Underweight';
    else if (bmi >= 30) label = 'Obese';

    bmiBox.textContent = `BMI: ${val} (${label})`;
    s_bmi.textContent = `BMI: ${val} (${label})`;
  } else {
    bmiBox.textContent = 'BMI: —';
    s_bmi.textContent = 'BMI: —';
  }
}

function updateUI() {
  calculateBMI();

  const sys = els.systolic.value;
  const dia = els.diastolic.value;

  s_bp.textContent = (sys || dia)
    ? `BP: ${sys || '-'} / ${dia || '-'}`
    : 'BP: —';

  s_alcohol.textContent = els.chk_alcohol.checked ? 'Alcohol: Yes' : 'Alcohol: No';
}

document.querySelectorAll('#healthForm input, #healthForm select')
  .forEach(input => {
    input.addEventListener('input', updateUI);
  });

document.getElementById('healthForm').addEventListener('submit', async (event) => {
  event.preventDefault();

  const payload = {
    gender: els.gender.value,
    age: Number(els.age.value),
    height: Number(els.height.value),
    weight: Number(els.weight.value),
    systolic: Number(els.systolic.value),
    diastolic: Number(els.diastolic.value),
    sleeptime: Number(els.sleeptime.value),
    chest_pain: els.chk_chest.checked ? 1 : 0,
    prior_heart_attack: els.chk_heart.checked ? 1 : 0,
    highchol: els.chk_chol.checked ? 1 : 0,
    diffwalk: els.chk_walk.checked ? 1 : 0,
    physactivity: els.chk_activity.checked ? 1 : 0,
    alcohol: els.chk_alcohol.checked ? 1 : 0,
    smoking: els.smoking.checked ? 1 : 0,
    stress_level: Number(els.stress.value)
  };

  try {
    const response = await fetch('/api/manual-entry', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (result.success) {
      sessionStorage.setItem("autocare_prediction", JSON.stringify(result));
      window.location.href = "/dashboard";
    } else {
      alert("Prediction failed");
    }

  } catch (err) {
    console.error(err);
    alert("Server error");
  }
});
