document.addEventListener("DOMContentLoaded", () => {

    // URL твоего backend на Render
    const API_URL = "https://my-clipper-backend.onrender.com";  // !!! Поставь свой !!!

    const uploadBtn = document.getElementById("uploadBtn");
    const fileInput = document.getElementById("fileInput");
    const resultBox = document.getElementById("result");

    uploadBtn.onclick = async () => {
        const file = fileInput.files[0];
        if (!file) {
            alert("Выберите видео!");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("max_highlights", 3);

        resultBox.innerHTML = "⏳ Обработка... Это может занять 10–40 секунд...";

        try {
            const res = await fetch(`${API_URL}/upload`, {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                const err = await res.json();
                resultBox.innerHTML = "Ошибка: " + err.detail;
                return;
            }

            const data = await res.json();
            console.log("Ответ сервера:", data);

            resultBox.innerHTML = `
                <h3>Готово!</h3>
                <p>Найдено клипов: ${data.highlights.length}</p>
            `;

            data.highlights.forEach(h => {
                const el = document.createElement("div");
                el.innerHTML = `
                    <p><b>${h.title}</b></p>
                    <video controls width="300" src="${API_URL}/download/${h.file}"></video>
                    <hr>
                `;
                resultBox.appendChild(el);
            });

        } catch (e) {
            console.error(e);
            resultBox.innerHTML = "Ошибка соединения: " + e;
        }
    };
});
