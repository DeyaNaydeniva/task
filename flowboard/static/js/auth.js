function switchTab(tab) {
  const isSignIn = tab === 'signin';
  document.getElementById('tab-signin').classList.toggle('active', isSignIn);
  document.getElementById('tab-signup').classList.toggle('active', !isSignIn);
  document.getElementById('panel-signin').classList.toggle('active', isSignIn);
  document.getElementById('panel-signup').classList.toggle('active', !isSignIn);
  document.getElementById('success-msg').style.display = 'none';
  document.getElementById('header-title').textContent = isSignIn ? 'Welcome back' : 'Create an account';
  document.getElementById('header-sub').innerHTML = isSignIn
    ? "Don't have an account? <a onclick=\"switchTab('signup')\">Sign up</a>"
    : "Already have an account? <a onclick=\"switchTab('signin')\">Sign in</a>";
}

function clearErrors() {
  document.querySelectorAll('.field-error').forEach(el => el.style.display = 'none');
  document.querySelectorAll('input').forEach(el => el.classList.remove('has-error'));
}

function showError(inputId, errId) {
  const input = document.getElementById(inputId);
  const err = document.getElementById(errId);
  if (input && err) {
    input.classList.add('has-error');
    err.style.display = 'block';
  }
}

function handleSignIn() {
  clearErrors();
  const email = document.getElementById('si-email').value.trim();
  const pass = document.getElementById('si-password').value;
  let valid = true;
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showError('si-email', 'si-email-err'); valid = false;
  }
  if (!pass) { showError('si-password', 'si-pass-err'); valid = false; }
  if (!valid) return;

  document.getElementById('signin-form').submit();
}

function handleSignUp() {
  clearErrors();
  const fname = document.getElementById('su-fname').value.trim();
  const lname = document.getElementById('su-lname').value.trim();
  const email = document.getElementById('su-email').value.trim();
  const pass = document.getElementById('su-password').value;
  const confirm = document.getElementById('su-confirm').value;
  let valid = true;
  if (!fname) { showError('su-fname', 'su-fname-err'); valid = false; }
  if (!lname) { showError('su-lname', 'su-lname-err'); valid = false; }
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showError('su-email', 'su-email-err'); valid = false;
  }
  if (!pass || pass.length < 8) { showError('su-password', 'su-pass-err'); valid = false; }
  if (!confirm || confirm !== pass) { showError('su-confirm', 'su-confirm-err'); valid = false; }
  if (!valid) return;

  document.getElementById('signup-form').submit();
}

/* Open the correct tab if Django redirected back with errors */
document.addEventListener('DOMContentLoaded', () => {
  const active = document.body.dataset.activeTab;
  if (active === 'signup') switchTab('signup');
});
