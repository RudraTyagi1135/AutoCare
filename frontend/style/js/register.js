// Role toggle logic
document.addEventListener('DOMContentLoaded', () => {
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

  // Optional: client-side confirm password check before submit
  const form = document.getElementById('registerForm');
  const password = document.getElementById('password');
  const confirmPassword = document.getElementById('confirm_password');

  form.addEventListener('submit', (e) => {
    if (password && confirmPassword) {
      if (password.value !== confirmPassword.value) {
        e.preventDefault();
        // simple inline flash-like feedback
        showTempMessage('Passwords do not match', 'error');
        confirmPassword.focus();
      }
    }
  });

  function showTempMessage(message, category = 'info', timeout = 3000) {
    const p = document.createElement('p');
    p.className = `flash ${category}`;
    p.textContent = message;
    // insert after subtitle or at top of form
    const subtitle = document.querySelector('.subtitle');
    subtitle.insertAdjacentElement('afterend', p);
    setTimeout(() => p.remove(), timeout);
  }
});
