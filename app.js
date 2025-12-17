const API_BASE = 'https://fenixaibot.online';

const uploadBtn   = document.getElementById('uploadBtn');
const fileInput   = document.getElementById('fileInput');
const progressBox = document.getElementById('progress');
const authModal   = document.getElementById('authModal');
const userBox     = document.getElementById('user');

let token = localStorage.getItem('token');
let currentJobId = null;
let statusTimer = null;

if (token) {
  userBox.innerText = 'Авторизован';
  userBox.classList.remove('hidden');
}

uploadBtn.onclick = () => {
  if (!token) {
    authModal.classList.remove('hidden');
    return;
  }
  fileInput.click();
};

fileInput.onchange = () => {
  const file = fileInput.files[0];
  if (file) uploadVideo(file);
};

function onTelegramAuth(user) {
  fetch(API_BASE + '/auth/telegram', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user)
  })
  .then(r => r.json())
  .then(res => {
    token = res.token;
    localStorage.setItem('token', token);

    authModal.classList.add('hidden');
    userBox.innerText = user.first_name || 'User';
    userBox.classList.remove('hidden');
  });
}

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

function pollStatus() {
  statusTimer = setInterval(() => {
    fetch(API_BASE + '/video/status/' + currentJobId, {
      headers: { 'Authorization': 'Bearer ' + token }
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
