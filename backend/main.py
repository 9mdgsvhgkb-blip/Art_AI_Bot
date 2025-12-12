import os
import json
import time
import re

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse

from fastapi.middleware.cors import CORSMiddleware

from movie_utils import ensure_dirs, extract_audio, cut_clip_ffmpeg
from config import INPUT_DIR, OUTPUT_DIR, TMP_DIR, OPENAI_API_KEY
import openai

# ensure dirs
ensure_dirs(INPUT_DIR, OUTPUT_DIR, TMP_DIR)

# setup OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

app = FastAPI(title="My Clipper API")

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно ограничить позже
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...), max_highlights: int = Form(3)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")

    timestamp = int(time.time())
    safe_name = f"{timestamp}_{file.filename}"

    video_path = os.path.join(INPUT_DIR, safe_name)

    # save video
    with open(video_path, "wb") as f:
        f.write(await file.read())

    # extract audio
    audio_path = os.path.join(TMP_DIR, f"{safe_name}.wav")
    extract_audio(video_path, audio_path)

    # transcribe via Whisper
    try:
        with open(audio_path, "rb") as f:
            resp = openai.Audio.transcribe(model="whisper-1", file=f)
        text = resp.get("text", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"transcription failed: {e}")

    # ask GPT for highlights
    prompt = (
        f"У тебя есть расшифровка видео. Найди до {max_highlights} интересных моментов. "
        "Верни строго JSON массив: [{start, end, title, excerpt}].\n\n"
        f"{text}"
    )

    try:
        chat = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.2
        )
        content = chat.choices[0].message["content"]
        highlights = json.loads(content)

    except:
        m = re.search(r"(\[.*\])", content, flags=re.S)
        if not m:
            raise HTTPException(status_code=500, detail="failed to parse GPT output")
        highlights = json.loads(m.group(1))

    results = []

    for i, h in enumerate(highlights):
        start = float(h.get("start", 0))
        end = float(h.get("end", start + 10))

        out_name = f"{timestamp}_hl_{i}.mp4"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        cut_clip_ffmpeg(video_path, start, end, out_path)

        results.append({
            "file": out_name,
            "title": h.get("title", ""),
            "start": start,
            "end": end,
            "excerpt": h.get("excerpt", "")
        })

    return JSONResponse({"transcript": text, "highlights": results})


@app.get("/download/{filename}")
def download(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path, media_type="video/mp4", filename=filename)
