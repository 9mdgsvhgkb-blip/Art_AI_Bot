// ==================== SIDEBAR ====================
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const closeBtn = document.getElementById('closeBtn');

hamburger.addEventListener('click', () => {
  sidebar.classList.add('active');
  overlay.classList.add('active');
});

closeBtn.addEventListener('click', () => {
  sidebar.classList.remove('active');
  overlay.classList.remove('active');
});

overlay.addEventListener('click', () => {
  sidebar.classList.remove('active');
  closeAllModals();
});

const menuLinks = document.querySelectorAll('.sidebar a');

menuLinks.forEach(link => {
  link.addEventListener('click', () => {
    menuLinks.forEach(l => l.classList.remove('active'));
    link.classList.add('active');
  });
});

// ==================== MODALS ====================
const modalButtons = document.querySelectorAll('.icon-btn-wrapper');
const modals = document.querySelectorAll('.modal');

modalButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const modalId = btn.dataset.modal;
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'flex';
      overlay.classList.add('active');
    }
  });
});

// Функция закрытия всех модалок
function closeAllModals() {
  modals.forEach(modal => {
    modal.style.display = 'none';
  });
  overlay.classList.remove('active');
}

// Закрытие модалки при клике на крестик
const modalCloseButtons = document.querySelectorAll('.modal-close');

modalCloseButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const modal = btn.closest('.modal');
    if (modal) {
      modal.style.display = 'none';
      overlay.classList.remove('active');
    }
  });
});

// Закрытие модалки при клике на overlay (кроме sidebar)
overlay.addEventListener('click', (e) => {
  if (!sidebar.classList.contains('active')) {
    closeAllModals();
  }
});

// Закрытие модалки при клике вне контента
modals.forEach(modal => {
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
      overlay.classList.remove('active');
    }
  });
});
