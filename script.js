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
const modalContent = document.querySelector('.modal-content'); 
const modalTitle = document.getElementById('modalTitle');
const modalText = document.getElementById('modalText');
const modalImage = document.getElementById('modalImage');
const modalButton = document.getElementById('modalButton');
const modalClose = document.getElementById('modalClose');

const floatingButtons = document.querySelectorAll('.icon-btn-wrapper');

floatingButtons.forEach((btnWrapper, index) => {
  btnWrapper.addEventListener('click', () => {
    modal.classList.add('active');
    modalContent.classList.add('show'); 

    if(index === 0) {
      modalTitle.textContent = "Нарезка клипов";
      modalText.textContent = "ИИ автоматически ищет лучшие моменты, добавляет субтитры и режет под формат коротких видео.";
      modalImage.src = "clip.jpg";
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
modalClose.addEventListener('click', () => {
  modal.classList.remove('active');
  modalContent.classList.remove('show'); 
});

modal.addEventListener('click', (e) => {
  if(e.target === modal) {
    modal.classList.remove('active');
    modalContent.classList.remove('show'); 
  }
});

const fileInput = document.getElementById('videoFile');

// Привязка кнопки модалки к инпуту
modalButton.addEventListener('click', () => {
  fileInput.click();
});

// Обработчик выбора файла
fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (!file) return;

  // Определяем, какая кнопка была открыта (по заголовку модалки)
  let endpoint = '';
  if(modalTitle.textContent.includes('Нарезка')) {
    endpoint = '/upload_video_full';      // полный фарш
  } else if(modalTitle.textContent.includes('Субтитры')) {
    endpoint = '/upload_video_subtitles'; // только субтитры
  } else if(modalTitle.textContent.includes('Редактор')) {
    endpoint = '/upload_video';           // только загрузка
  }

  uploadVideo(file, endpoint);

  // Сбрасываем инпут, чтобы можно было выбрать тот же файл снова
  fileInput.value = '';
});

// Функция загрузки
function uploadVideo(file, endpoint) {
  const formData = new FormData();
  formData.append('file', file);

  fetch(endpoint, {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    console.log('Ответ сервера:', data);
    alert('Видео отправлено! ID работы: ' + data.job_id);
    modal.classList.remove('active');
    modalContent.classList.remove('show');
  })
  .catch(err => {
    console.error(err);
    alert('Ошибка при загрузке видео');
  });
}
