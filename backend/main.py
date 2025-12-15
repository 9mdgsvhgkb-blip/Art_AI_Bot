import os
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from movie_utils import (
    ensure_dirs,
    extract_audio,
    cut_clip_ffmpeg,
    burn_ass_subtitles
)

from transcribe import transcribe
from highlights import pick_highlights
from subtitles import build_ass_subtitles


# ====== PATHS ======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TMP_DIR = os.path.join(BASE_DIR, "tmp")

ensure_dirs(INPUT_DIR, OUTPUT_DIR, TMP_DIR)

# ====== APP ======
app = FastAPI()

# ====== CORS (КРИТИЧНО) ======
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # потом ограничим
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== ROUTES ======

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    max_highlights: int = Form(5)
):
    ts = int(time.time())
    safe_name = f"{ts}_{file.filename.replace(' ', '_')}"
    video_path = os.path.join(INPUT_DIR, safe_name)

    # сохранить видео
    with open(video_path, "wb") as f:
        f.write(await file.read())

    # 1️⃣ транскрибация
    segments = transcribe(video_path)

    if not segments:
        raise HTTPException(status_code=400, detail="Не удалось распознать речь")

    # 2️⃣ AI-хайлайты
    highlights = pick_highlights(segments, max_highlights)

    outputs = []

    for i, h in enumerate(highlights):
        start = max(h["start"] - 1, 0)
        end = h["end"] + 1

        clip_tmp = os.path.join(TMP_DIR, f"{ts}_clip_{i}.mp4")

        # 3️⃣ нарезка
        cut_clip_ffmpeg(video_path, start, end, clip_tmp)

        # 4️⃣ субтитры (karaoke ass)
        ass_path = os.path.join(TMP_DIR, f"{ts}_subs_{i}.ass")
        build_ass_subtitles(h["words"], ass_path)

        final_name = f"{ts}_final_{i}.mp4"
        final_path = os.path.join(OUTPUT_DIR, final_name)

        # 5️⃣ прожиг субтитров
        burn_ass_subtitles(clip_tmp, ass_path, final_path)

        outputs.append({
            "file": final_name,
            "start": start,
            "end": end,
            "text": h["text"]
        })

    return JSONResponse({"clips": outputs})


@app.get("/download/{filename}")
def download(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path, media_type="video/mp4")
