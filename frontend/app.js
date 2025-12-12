const BACKEND_URL = "https://my-clipper-backend.onrender.com";

const tg = window.Telegram.WebApp;
tg.expand();


document.getElementById("video").addEventListener("change", async function () {
    const file = this.files[0];

    if (!file) {
        alert("Файл не выбран!");
        return;
    }

    try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("max_highlights", 3);

        const response = await fetch(`${BACKEND_URL}/upload`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const txt = await response.text();
            alert("Сервер вернул ошибку:\n" + txt);
            return;
        }

        const data = await response.json();

        console.log("RESULT:", data);

        const out = document.getElementById("output");
        out.innerHTML = "<h3>Готовые клипы:</h3>";

        data.highlights.forEach(h => {
            const url = `${BACKEND_URL}/download/${h.file}`;
            out.innerHTML += `
                <div>
                    <b>${h.title}</b><br>
                    <a href="${url}" target="_blank">Скачать клип</a>
                </div>
                <hr>
            `;
        });

    } catch (err) {
        console.error(err);
        alert("Ошибка соединения: " + err.message);
    }
});
