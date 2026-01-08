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

// Функция закрытия всех модалок
function closeAllModals() {
  modals.forEach(modal => modal.style.display = 'none');
  overlay.classList.remove('active');
}

// Открытие модалки по кнопке
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

// Закрытие при клике на overlay
overlay.addEventListener('click', () => {
  // Закрываем sidebar и все модалки
  sidebar.classList.remove('active');
  closeAllModals();
});

// Закрытие при клике вне контента модалки
modals.forEach(modal => {
  modal.addEventListener('click', (e) => {
    if (e.target === modal) { // если кликнули именно по затемненной области модалки
      modal.style.display = 'none';
      overlay.classList.remove('active');
    }
  });
});
