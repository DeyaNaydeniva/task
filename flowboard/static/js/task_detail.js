/* Edit modal */
const editOverlay = document.getElementById('edit-modal-overlay');

function openEditModal() {
  editOverlay.classList.add('open');
  document.getElementById('edit-title').focus();
}

function closeEditModal() {
  editOverlay.classList.remove('open');
  document.getElementById('edit-title').classList.remove('has-error');
  document.getElementById('edit-title-err').style.display = 'none';
}

function submitEdit() {
  const titleInput = document.getElementById('edit-title');
  const titleErr = document.getElementById('edit-title-err');
  if (!titleInput.value.trim()) {
    titleInput.classList.add('has-error');
    titleErr.style.display = 'block';
    titleInput.focus();
    return;
  }
  titleInput.classList.remove('has-error');
  titleErr.style.display = 'none';
  document.getElementById('edit-form').submit();
}

editOverlay.addEventListener('click', (e) => {
  if (e.target === editOverlay) closeEditModal();
});

/* Delete confirm modal */
const deleteOverlay = document.getElementById('delete-modal-overlay');

function openDeleteModal() {
  deleteOverlay.classList.add('open');
}

function closeDeleteModal() {
  deleteOverlay.classList.remove('open');
}

deleteOverlay.addEventListener('click', (e) => {
  if (e.target === deleteOverlay) closeDeleteModal();
});

/* Close both on Escape */
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeEditModal();
    closeDeleteModal();
  }
});

/* Add label — submit to the selected label's toggle URL */
function addLabel() {
  const sel = document.getElementById('add-label-select');
  const opt = sel.options[sel.selectedIndex];
  const url = opt ? opt.dataset.url : null;
  if (!url) return;
  const form = sel.closest('form');
  form.action = url;
  form.submit();
}
