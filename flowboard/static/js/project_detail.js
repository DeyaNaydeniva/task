const overlay = document.getElementById('task-modal-overlay');

function openTaskModal() {
  overlay.classList.add('open');
  document.getElementById('task-title').focus();
}

function closeTaskModal() {
  overlay.classList.remove('open');
  document.getElementById('task-form').reset();
  document.getElementById('task-title').classList.remove('has-error');
  document.getElementById('task-title-err').style.display = 'none';
}

overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeTaskModal();
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeTaskModal();
});

function submitTask() {
  const titleInput = document.getElementById('task-title');
  const titleErr = document.getElementById('task-title-err');

  if (!titleInput.value.trim()) {
    titleInput.classList.add('has-error');
    titleErr.style.display = 'block';
    titleInput.focus();
    return;
  }

  titleInput.classList.remove('has-error');
  titleErr.style.display = 'none';
  document.getElementById('task-form').submit();
}
