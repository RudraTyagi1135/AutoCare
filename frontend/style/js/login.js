const userToggle = document.getElementById('userToggle');
const doctorToggle = document.getElementById('doctorToggle');
const roleInput = document.getElementById('roleInput');


[userToggle, doctorToggle].forEach(toggle => {
toggle.addEventListener('click', () => {
userToggle.classList.remove('active');
doctorToggle.classList.remove('active');
toggle.classList.add('active');
roleInput.value = toggle.dataset.role;
});
});