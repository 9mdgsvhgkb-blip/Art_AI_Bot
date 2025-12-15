const API_BASE = "https://fenixaibot.online";

// Telegram WebApp
const tg = window.Telegram?.WebApp;
if (tg) tg.expand();

const input = document.getElementById("videoInput");
const button = document.getElementById("uploadBtn");
const output = document.getElementById("output");

// при клике — открываем выбор файла
button.addEventListener("click", () => {
    input.click();
});

// когда файл выбран — начинаем загрузку
input.addEventListener("change", async () => {
    const file = input.files[0];
    if (!file) return;

    output.innerHTML = "<b>⏳ Обработка видео... подожди 20–60 сек</b>";

    try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("max_highlights", 3);

        const res = await fetch(`${API_BASE}/upload`, {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            const err = await res.text();
            output.innerHTML = "❌ Ошибка сервера:<br><pre>" + err + "</pre>";
            return;
        }

        const data = await res.json();

        output.innerHTML = "<h3>🎬 Готовые клипы</h3>";

        data.clips.forEach((clip, i) => {
            const clipUrl = `${API_BASE}/download/${clip.file}`;

            output.innerHTML += `
                <div style="margin-bottom:20px">
                    <p><b>Клип ${i + 1}</b></p>
                    <video src="${clipUrl}" controls width="280"></video>
                </div>
            `;
        });

    } catch (e) {
        console.error(e);
        output.innerHTML = "❌ Ошибка соединения: " + e.message;
    }
});
