document.addEventListener("DOMContentLoaded", () => {
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

        resultBox.innerHTML = "Загрузка...";

        try {
            let res = await fetch("http://localhost:8000/upload", {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                let err = await res.json();
                resultBox.innerHTML = "Ошибка: " + err.detail;
                return;
            }

            let data = await res.json();
            console.log(data);

            resultBox.innerHTML = "<h3>Готово!</h3>";

            data.highlights.forEach(h => {
                let el = document.createElement("div");
                el.innerHTML = `
                    <p><b>${h.title}</b></p>
                    <video src="http://localhost:8000/download/${h.file}" controls width="300"></video>
                    <hr>
                `;
                resultBox.appendChild(el);
            });

        } catch (e) {
            resultBox.innerHTML = "Ошибка соединения: " + e;
        }
    };
});