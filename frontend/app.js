const BACKEND_URL = "https://my-clipper-backend-lp16.onrender.com";

const tg = window.Telegram.WebApp;
tg.expand();

const input = document.getElementById("videoInput");
const button = document.getElementById("uploadBtn");
const output = document.getElementById("output");

button.addEventListener("click", async () => {
    const file = input.files[0];
    if (!file) {
        alert("Выберите видео!");
        return;
    }

    output.innerHTML = "<b>Обработка... ждите 20–40 сек...</b>";

    try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("max_highlights", 3);

        const res = await fetch(`${BACKEND_URL}/upload`, {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            const errText = await res.text();
            output.innerHTML = "Ошибка сервера:<br><pre>" + errText + "</pre>";
            return;
        }

        const data = await res.json();

        output.innerHTML = "<h3>Клипы:</h3>";

        data.highlights.forEach(h => {
            const clipUrl = `${BACKEND_URL}/download/${h.file}`;
            output.innerHTML += `
                <div>
                    <p><b>${h.title}</b></p>
                    <video src="${clipUrl}" controls width="280"></video>
                    <hr>
                </div>
            `;
        });

    } catch (e) {
        output.innerHTML = "Ошибка соединения: " + e.message;
    }
});
