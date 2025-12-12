import os
import json
import time
import re

# Удаляем прокси Render
for p in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
    if p in os.environ:
        del os.environ[p]

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from movie_utils import ensure_dirs, extract_audio, cut_clip_ffmpeg
from config import INPUT_DIR, OUTPUT_DIR, TMP_DIR, OPENAI_API_KEY

import openai
openai.api_key = OPENAI_API_KEY

ensure_dirs(INPUT_DIR, OUTPUT_DIR, TMP_DIR)

app = FastAPI(title="Clipper API")

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
        raise HTTPException(500, "OPENAI_API_KEY not set")

    ts = int(time.time())
    safe_name = f"{ts}_{file.filename}"
    video_path = os.path.join(INPUT_DIR, safe_name)

    with open(video_path, "wb") as f:
        f.write(await file.read())

    audio_path = os.path.join(TMP_DIR, f"{safe_name}.wav")
    extract_audio(video_path, audio_path)

    # --- Whisper transcription via old-style openai API ---
    with open(audio_path, "rb") as audio_f:
        transcript_obj = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_f
        )
    transcript = transcript_obj["text"]

    # --- GPT highlights ---
    prompt = (
        f"Вот расшифровка видео:\n{transcript}\n\n"
        f"Найди {max_highlights} важных моментов. Верни STRICT JSON:\n"
        "[{\"start\": 0, \"end\": 10, \"title\": \"...\", \"excerpt\": \"...\"}]"
    )

    chat = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = chat.choices[0].message["content"]

    try:
        highlights = json.loads(content)
    except:
        match = re.search(r"(\[.*\])", content, re.S)
        if not match:
            raise HTTPException(500, "Failed to parse JSON from GPT")
        highlights = json.loads(match.group(1))

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
        raise HTTPException(404, "file not found")
    return FileResponse(path, media_type="video/mp4", filename=filename)
