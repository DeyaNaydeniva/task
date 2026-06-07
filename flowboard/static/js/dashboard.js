const overlay = document.getElementById('modal-overlay');

function openModal() {
  overlay.classList.add('open');
  document.getElementById('proj-name').focus();
}

function closeModal() {
  overlay.classList.remove('open');
  document.getElementById('proj-name').value = '';
  document.getElementById('proj-desc').value = '';
  document.getElementById('proj-name').classList.remove('has-error');
  document.getElementById('proj-name-err').style.display = 'none';
}

overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeModal();
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

function submitProject() {
  const name = document.getElementById('proj-name').value.trim();
  const nameErr = document.getElementById('proj-name-err');
  const nameInput = document.getElementById('proj-name');

  if (!name) {
    nameInput.classList.add('has-error');
    nameErr.style.display = 'block';
    nameInput.focus();
    return;
  }

  nameInput.classList.remove('has-error');
  nameErr.style.display = 'none';
  document.getElementById('create-project-form').submit();
}
