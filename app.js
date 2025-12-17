/* ===============================
   CONFIG
================================ */
const API_BASE = 'https://fenixaibot.online';

/* ===============================
   ELEMENTS
================================ */
const uploadBtn   = document.getElementById('uploadBtn');
const fileInput   = document.getElementById('fileInput');
const progressBox = document.getElementById('progress');
const authModal   = document.getElementById('authModal');
const userBox     = document.getElementById('user');

/* ===============================
   STATE
================================ */
let token = localStorage.getItem('token');
let currentJobId = null;
let statusTimer = null;

/* ===============================
   INIT
================================ */
if (token) {
  userBox.innerText = 'Авторизован';
  userBox.classList.remove('hidden');
}

/* ===============================
   UPLOAD BUTTON
================================ */
uploadBtn.onclick = () => {
  if (!token) {
    authModal.classList.remove('hidden');
    return;
  }
  fileInput.click();
};

/* ===============================
   FILE SELECT
================================ */
fileInput.onchange = () => {
  const file = fileInput.files[0];
  if (!file) return;

  uploadVideo(file);
};

/* ===============================
   TELEGRAM AUTH
================================ */
function onTelegramAuth(user) {
  fetch(API_BASE + '/auth/telegram', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(user)
  })
  .then(r => r.json())
  .then(res => {
    if (!res.token) {
      alert('Ошибка авторизации');
      return;
    }

    token = res.token;
    localStorage.setItem('token', token);

    authModal.classList.add('hidden');
    userBox.innerText = user.first_name || 'User';
    userBox.classList.remove('hidden');
  })
  .catch(() => {
    alert('Ошибка соединения с сервером');
  });
}

/* ===============================
   VIDEO UPLOAD
================================ */
function uploadVideo(file) {
  const form = new FormData();
  form.append('video', file);

  const xhr = new XMLHttpRequest();
  xhr.open('POST', API_BASE + '/video/upload');
  xhr.setRequestHeader('Authorization', 'Bearer ' + token);

  progressBox.classList.remove('hidden');
  progressBox.innerText = 'Загрузка: 0%';

  xhr.upload.onprogress = e => {
    if (!e.lengthComputable) return;
    const percent = Math.round((e.loaded / e.total) * 100);
    progressBox.innerText = `Загрузка: ${percent}%`;
  };

  xhr.onload = () => {
    if (xhr.status !== 200) {
      progressBox.innerText = 'Ошибка загрузки';
      return;
    }

    const res = JSON.parse(xhr.responseText);
    currentJobId = res.job_id;

    progressBox.innerText = 'Видео загружено. Обработка началась…';

    startStatusPolling();
  };

  xhr.onerror = () => {
    progressBox.innerText = 'Ошибка сети';
  };

  xhr.send(form);
}

/* ===============================
   STATUS POLLING
================================ */
function startStatusPolling() {
  if (!currentJobId) return;

  statusTimer = setInterval(() => {
    fetch(API_BASE + '/video/status/' + currentJobId, {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    })
    .then(r => r.json())
    .then(res => {
      if (!res.status) return;

      progressBox.innerText =
        `Статус: ${res.status} (${res.progress || 0}%)`;

      if (res.status === 'done') {
        clearInterval(statusTimer);
        progressBox.innerText = 'Готово 🎉 Клип(ы) готовы';
      }

      if (res.status === 'error') {
        clearInterval(statusTimer);
        progressBox.innerText = 'Ошибка обработки';
      }
    });
  }, 3000);
}
