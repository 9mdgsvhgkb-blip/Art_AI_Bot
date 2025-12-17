const API_BASE = 'https://fenixaibot.online';

/* ===============================
   TOKEN FROM URL (CRITICAL)
================================ */
const params = new URLSearchParams(window.location.search);
const urlToken = params.get('token');

if (urlToken) {
  localStorage.setItem('token', urlToken);
  // убираем токен из URL НАВСЕГДА
  window.history.replaceState({}, document.title, '/');
}

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
  if (file) uploadVideo(file);
};

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
    if (e.lengthComputable) {
      progressBox.innerText =
        `Загрузка: ${Math.round((e.loaded / e.total) * 100)}%`;
    }
  };

  xhr.onload = () => {
    const res = JSON.parse(xhr.responseText);
    currentJobId = res.job_id;
    progressBox.innerText = 'Обработка началась…';
    pollStatus();
  };

  xhr.send(form);
}

/* ===============================
   STATUS
================================ */
function pollStatus() {
  statusTimer = setInterval(() => {
    fetch(API_BASE + '/video/status/' + currentJobId, {
      headers: { Authorization: 'Bearer ' + token }
    })
    .then(r => r.json())
    .then(res => {
      progressBox.innerText =
        `Статус: ${res.status} (${res.progress || 0}%)`;

      if (res.status === 'done' || res.status === 'error') {
        clearInterval(statusTimer);
      }
    });
  }, 3000);
}
