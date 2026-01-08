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
  overlay.classList.remove('active');
});

const menuLinks = document.querySelectorAll('.sidebar a');

menuLinks.forEach(link => {
  link.addEventListener('click', () => {
    menuLinks.forEach(l => l.classList.remove('active')); // убираем активность со всех
    link.classList.add('active'); // добавляем текущей
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

overlay.addEventListener('click', () => {
  modals.forEach(modal => modal.style.display = 'none');
  overlay.classList.remove('active');
});
