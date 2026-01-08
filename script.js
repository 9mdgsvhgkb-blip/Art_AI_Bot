// SIDEBAR
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const closeBtn = document.getElementById('closeBtn');

hamburger.addEventListener('click', () => {
  sidebar.classList.add('active');
  sidebarOverlay.classList.add('active');
});

closeBtn.addEventListener('click', () => {
  sidebar.classList.remove('active');
  sidebarOverlay.classList.remove('active');
});

sidebarOverlay.addEventListener('click', () => {
  sidebar.classList.remove('active');
  sidebarOverlay.classList.remove('active');
});

document.querySelectorAll('.sidebar a').forEach(link => {
  link.addEventListener('click', () => {
    document.querySelectorAll('.sidebar a').forEach(l => l.classList.remove('active'));
    link.classList.add('active');
  });
});

// MODALS
const modalButtons = document.querySelectorAll('.icon-btn-wrapper');
const modals = document.querySelectorAll('.modal');
const modalOverlay = document.getElementById('modal-overlay');

function closeAllModals() {
  modals.forEach(m => m.classList.remove('active'));
  modalOverlay.classList.remove('active');
}

modalButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const modalId = btn.dataset.modal;
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      modalOverlay.classList.add('active');
    }
  });
});

document.querySelectorAll('.modal-close').forEach(btn => {
  btn.addEventListener('click', () => {
    const modal = btn.closest('.modal');
    if (modal) {
      modal.classList.remove('active');
      modalOverlay.classList.remove('active');
    }
  });
});

modalOverlay.addEventListener('click', closeAllModals);

// Закрытие при клике вне контента модалки
modals.forEach(modal => {
  modal.addEventListener('click', e => {
    if (e.target === modal) closeAllModals();
  });
});
