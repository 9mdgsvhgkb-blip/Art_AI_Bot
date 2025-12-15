const API_BASE = "https://fenixaibot.online";

const tg = window.Telegram?.WebApp;
if (tg) tg.expand();

const input = document.getElementById("videoInput");
const button = document.getElementById("uploadBtn");
const output = document.getElementById("output");

button.addEventListener("click", () => {
    input.click();
});

input.addEventListener("change", async () => {
    const file = input.files[0];
    if (!file) return;

    output.innerHTML = "⏳ Видео загружается...";

    const formData = new FormData();
    formData.append("file", file);
    formData.append("max_highlights", 3);

    const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    const jobId = data.job_id;

    output.innerHTML = "🤖 AI анализирует видео...";

    const interval = setInterval(async () => {
        const s = await fetch(`${API_BASE}/status/${jobId}`);
        const status = await s.json();

        if (status.status === "done") {
            clearInterval(interval);

            const r = await fetch(`${API_BASE}/result/${jobId}`);
            const result = await r.json();

            output.innerHTML = "<h3>🎬 Готовые клипы</h3>";

            result.clips.forEach((clip, i) => {
                const url = `${API_BASE}/download/${clip.file}`;
                output.innerHTML += `
                    <div style="margin-bottom:20px">
                        <p><b>Клип ${i + 1}</b></p>
                        <video src="${url}" controls width="280"></video>
                    </div>
                `;
            });
        }

        if (status.status === "error") {
            clearInterval(interval);
            output.innerHTML = "❌ Ошибка обработки видео";
        }

    }, 5000);
});
