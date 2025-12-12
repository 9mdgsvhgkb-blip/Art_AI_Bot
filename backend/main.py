import os
import json
import time
import re

# Удаляем прокси Render (fix ошибки "proxies=")
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("ALL_PROXY", None)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from movie_utils import ensure_dirs, extract_audio, cut_clip_ffmpeg
from config import INPUT_DIR, OUTPUT_DIR, TMP_DIR, OPENAI_API_KEY

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# создаём папки
ensure_dirs(INPUT_DIR, OUTPUT_DIR, TMP_DIR)

app = FastAPI(title="Clipper API")

# Разрешим все запросы (Telegram WebApp)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...), max_highlights: int = Form(3)):

    if not OPENAI_API_KEY:
        raise HTTPException(500, "OPENAI_API_KEY missing")

    ts = int(time.time())
    safe_name = f"{ts}_{file.filename}"
    video_path = os.path.join(INPUT_DIR, safe_name)

    # сохраняем видео
    with open(video_path, "wb") as f:
        f.write(await file.read())

    # извлекаем аудио
    audio_path = os.path.join(TMP_DIR, f"{safe_name}.wav")
    extract_audio(video_path, audio_path)

    # *** Whisper API (новая версия) ***
    with open(audio_path, "rb") as audio_file:
        transcript_obj = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    transcript = transcript_obj.text

    # GPT — разбивка видео
    prompt = (
        f"Вот расшифровка видео:\n{transcript}\n\n"
        f"Найди до {max_highlights} ключевых моментов и верни STRICT JSON:\n"
        "[{\"start\": секунд, \"end\": секунд, \"title\": \"\", \"excerpt\": \"\"}]\n"
    )

    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = chat.choices[0].message.content

    try:
        highlights = json.loads(content)
    except:
        match = re.search(r"(\[.*\])", content, re.S)
        if not match:
            raise HTTPException(500, "Failed to parse JSON from GPT")
        highlights = json.loads(match.group(1))

    # режем клипы
    outputs = []
    for i, h in enumerate(highlights):
        start = float(h.get("start", 0))
        end = float(h.get("end", start + 10))

        out_name = f"{safe_name}_hl_{i}.mp4"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        cut_clip_ffmpeg(video_path, start, end, out_path)

        outputs.append({
            "file": out_name,
            "title": h.get("title", ""),
            "start": start,
            "end": end,
            "excerpt": h.get("excerpt", "")
        })

    return JSONResponse({
        "transcript": transcript,
        "highlights": outputs
    })


@app.get("/download/{filename}")
def download_file(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")
    return FileResponse(path, media_type="video/mp4", filename=filename)
