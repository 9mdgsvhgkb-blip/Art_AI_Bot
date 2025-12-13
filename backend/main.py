import os
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from movie_utils import ensure_dirs, extract_audio, cut_clip_ffmpeg

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
    max_highlights: int = Form(3)
):
    timestamp = int(time.time())
    safe_name = f"{timestamp}_{file.filename}"
    video_path = os.path.join(INPUT_DIR, safe_name)

    with open(video_path, "wb") as f:
        f.write(await file.read())

    duration = 60  # пока тупо 1 минута
    clip_len = 15  # клипы по 15 сек

    outputs = []

    for i in range(max_highlights):
        start = i * clip_len
        end = start + clip_len

        out_name = f"{timestamp}_clip_{i}.mp4"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        cut_clip_ffmpeg(video_path, start, end, out_path)

        outputs.append({
            "file": out_name,
            "title": f"Clip {i+1}",
            "start": start,
            "end": end
        })

    return JSONResponse({"highlights": outputs})

@app.get("/download/{filename}")
def download(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="video/mp4")
