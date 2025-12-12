import os
import json
import time
import tempfile
import re
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
import openai

# 👉 Импорт config из папки backend
from backend.config import INPUT_DIR, OUTPUT_DIR, TMP_DIR, OPENAI_API_KEY

from backend.movie_utils import (
    ensure_dirs,
    extract_audio,
    cut_clip_ffmpeg,
    burn_subtitles_ffmpeg
)

# Ensure dirs exist
ensure_dirs(INPUT_DIR, OUTPUT_DIR, TMP_DIR)

# Configure OpenAI (read key from env)
if not OPENAI_API_KEY:
    openai.api_key = None
else:
    openai.api_key = OPENAI_API_KEY

app = FastAPI(title="My Clipper API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...), max_highlights: int = Form(3)):

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set in environment")

    timestamp = int(time.time())
    safe_name = f"{timestamp}_{os.path.basename(file.filename)}"
    video_path = os.path.join(INPUT_DIR, safe_name)

    with open(video_path, "wb") as f:
        f.write(await file.read())

    # Extract audio
    audio_path = os.path.join(TMP_DIR, f"{safe_name}.wav")
    try:
        extract_audio(video_path, audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"audio extraction failed: {e}")

    # Transcribe
    try:
        with open(audio_path, "rb") as fh:
            resp = openai.Audio.transcribe(model="whisper-1", file=fh)
        transcript = resp.get("text", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"transcription failed: {e}")

    # Ask GPT for highlight timestamps
    prompt = (
        "У тебя есть расшифровка видео. Найди до "
        f"{max_highlights} самых интересных фрагментов. Верни строго JSON массив "
        "с объектами: start, end, title, excerpt.\n\n"
        f"Transcript:\n{transcript}"
    )

    try:
        chat_resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.2
        )
        content = chat_resp.choices[0].message["content"]
        highlights = json.loads(content)

    except Exception as e:
        try:
            match = re.search(r"(\[.*\])", content, flags=re.S)
            highlights = json.loads(match.group(1))
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"highlight parsing failed: {e} | {ex}")

    outputs = []
    for i, h in enumerate(highlights):
        start = float(h.get("start", 0.0))
        end = float(h.get("end", start + 10.0))

        out_fname = f"{os.path.splitext(safe_name)[0]}_hl_{i}.mp4"
        out_path = os.path.join(OUTPUT_DIR, out_fname)

        try:
            cut_clip_ffmpeg(video_path, start, end, out_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"cut failed: {e}")

        outputs.append({
            "file": out_fname,
            "title": h.get("title", ""),
            "start": start,
            "end": end,
            "excerpt": h.get("excerpt", "")
        })

    return JSONResponse({"transcript": transcript, "highlights": outputs})


@app.get("/download/{filename}")
def download_file(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path, media_type="video/mp4", filename=filename)
