/* ===== Navigation ===== */
const tabs = document.querySelectorAll('.tab');
const screens = document.querySelectorAll('.screen');

tabs.forEach(tab=>{
  tab.onclick=()=>{
    tabs.forEach(t=>t.classList.remove('active'));
    screens.forEach(s=>s.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.go).classList.add('active');
  };
});

/* ===== Telegram Auth ===== */
function onTelegramAuth(user){
  fetch('/auth/telegram', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(user)
  })
  .then(r=>r.json())
  .then(res=>{
    if(!res.ok) return;

    document.getElementById('tg-login').classList.add('hidden');
    document.getElementById('user-info').classList.remove('hidden');

    document.getElementById('avatar').innerText =
      (user.first_name || 'U')[0];

    document.getElementById('username').innerText =
      user.first_name + (user.last_name ? ' ' + user.last_name : '');
  });
}
