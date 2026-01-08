// ======== Сайдбар ========
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
    menuLinks.forEach(l => l.classList.remove('active'));
    link.classList.add('active');
  });
});

// ======== Модальные окна для плавающих кнопок ========
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modalTitle');
const modalText = document.getElementById('modalText');
const modalImage = document.getElementById('modalImage');
const modalButton = document.getElementById('modalButton');
const modalClose = document.getElementById('modalClose');

const floatingButtons = document.querySelectorAll('.icon-btn-wrapper');

floatingButtons.forEach((btnWrapper, index) => {
  btnWrapper.addEventListener('click', () => {
    modal.classList.add('active');

    if(index === 0) {
      modalTitle.textContent = "Нарезка клипов";
      modalText.textContent = "ИИ автоматически ищет лучшие моменты, добавляет субтитры и режет под формат коротких видео.";
      modalImage.src = "clip.jpg"; // путь к фото
    } else if(index === 1) {
      modalTitle.textContent = "ИИ Субтитры";
      modalText.textContent = "ИИ автоматически добавляет субтитры в ваше видео.";
      modalImage.src = "subtitles.jpg"; 
    } else if(index === 2) {
      modalTitle.textContent = "Редактор";
      modalText.textContent = "Загрузите и редактируйте свои видео.";
      modalImage.src = "editor.jpg"; 
    }
  });
});

// Закрытие модалки
modalClose.addEventListener('click', () => modal.classList.remove('active'));
modal.addEventListener('click', (e) => {
  if(e.target === modal) modal.classList.remove('active');
});
