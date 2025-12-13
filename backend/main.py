import os
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from movie_utils import (
    ensure_dirs,
    extract_audio,
    cut_clip_ffmpeg,
    burn_ass_subtitles
)

from transcribe import transcribe
from highlights import pick_highlights
from subtitles import build_ass_subtitles

INPUT_DIR = "input"
OUTPUT_DIR = "output"
TMP_DIR = "tmp"

ensure_dirs(INPUT_DIR, OUTPUT_DIR, TMP_DIR)

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    max_highlights: int = Form(5)
):
    ts = int(time.time())
    video_name = f"{ts}_{file.filename}"
    video_path = os.path.join(INPUT_DIR, video_name)

    with open(video_path, "wb") as f:
        f.write(await file.read())

    # 1️⃣ Речь → текст + слова
    segments = transcribe(video_path)

    # 2️⃣ Выбор лучших моментов
    highlights = pick_highlights(segments, max_highlights)

    outputs = []

    for i, h in enumerate(highlights):
        start = max(h["start"] - 1, 0)
        end = h["end"] + 1

        clip_name = f"{ts}_clip_{i}.mp4"
        clip_path = os.path.join(TMP_DIR, clip_name)

        # 3️⃣ Нарезка клипа
        cut_clip_ffmpeg(video_path, start, end, clip_path)

        # 4️⃣ Субтитры (караоке)
        ass_path = os.path.join(TMP_DIR, f"{ts}_subs_{i}.ass")
        build_ass_subtitles(h["words"], ass_path)

        final_name = f"{ts}_final_{i}.mp4"
        final_path = os.path.join(OUTPUT_DIR, final_name)

        # 5️⃣ Прожиг субтитров
        burn_ass_subtitles(clip_path, ass_path, final_path)

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
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="video/mp4")
