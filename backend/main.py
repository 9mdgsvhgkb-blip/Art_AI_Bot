import os
import time
import threading
import subprocess
import hashlib
import hmac
import jwt

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from movie_utils import cut_clip_ffmpeg, burn_ass_subtitles
from transcribe import transcribe
from highlights import pick_highlights
from subtitles import build_ass_subtitles

# ===== PATHS =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TMP_DIR = os.path.join(BASE_DIR, "tmp")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

# ===== APP =====
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== FRONTEND STATIC =====
app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")

# ===== JOB STORAGE =====
JOBS = {}

# ===== JWT CONFIG =====
BOT_TOKEN = "8584232857:AAHBbzQF66B31suqTKYKvBDJJevBQJ6xcMI"
JWT_SECRET = "645788555788567"
JWT_ALGO = "HS256"

# ===== JWT DEP =====
def get_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, "No auth header")
    token = auth.split(" ")[1]
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])

# ===== UTILS =====
def has_audio(video_path: str) -> bool:
    cmd = [
        "ffprobe",
        "-i", video_path,
        "-show_streams",
        "-select_streams", "a",
        "-loglevel", "error"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return bool(result.stdout)

# ===== PROCESS VIDEO =====
def process_video(job_id: str, video_path: str, max_highlights: int):
    try:
        JOBS[job_id]["status"] = "processing"

        if not has_audio(video_path):
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = "Видео не содержит аудио дорожки"
            return

        segments = transcribe(video_path)
        if not segments:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = "Не удалось распознать речь"
            return

        highlights = pick_highlights(segments, max_highlights)
        results = []

        for i, h in enumerate(highlights):
            start = max(h["start"] - 1, 0)
            end = h["end"] + 1

            clip_tmp = os.path.join(TMP_DIR, f"{job_id}_clip_{i}.mp4")
            cut_clip_ffmpeg(video_path, start, end, clip_tmp)

            ass_path = os.path.join(TMP_DIR, f"{job_id}_subs_{i}.ass")
            build_ass_subtitles(h["words"], ass_path)

            final_name = f"{job_id}_final_{i}.mp4"
            final_path = os.path.join(OUTPUT_DIR, final_name)

            burn_ass_subtitles(clip_tmp, ass_path, final_path)

            results.append({
                "file": final_name,
                "start": start,
                "end": end,
                "text": h["text"]
            })

        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["results"] = results

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)

# ===== ROUTES =====
@app.post("/upload")
async def upload_video(
    user=Depends(get_user),
    file: UploadFile = File(...),
    max_highlights: int = Form(3)
):
    job_id = str(int(time.time() * 1000))
    video_path = os.path.join(INPUT_DIR, f"{job_id}_{file.filename}")

    with open(video_path, "wb") as f:
        f.write(await file.read())

    JOBS[job_id] = {"status": "queued"}

    threading.Thread(
        target=process_video,
        args=(job_id, video_path, max_highlights),
        daemon=True
    ).start()

    return {"job_id": job_id}

@app.get("/status/{job_id}")
def status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404)
    return {"status": job["status"], "error": job.get("error")}

@app.get("/result/{job_id}")
def result(job_id: str):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        raise HTTPException(404)
    return {"clips": job["results"]}

@app.get("/download/{filename}")
def download(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404)
    return FileResponse(path, media_type="video/mp4")

@app.get("/health")
def health():
    return {"status": "ok"}

# ===== TELEGRAM LOGIN =====
@app.api_route("/auth", methods=["GET", "POST"])
async def telegram_auth(request: Request):
    data = dict(request.query_params)
    user_hash = data.pop("hash", None)

    if not user_hash:
        return JSONResponse({"error": "no hash"}, 400)

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    h = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if h != user_hash:
        return JSONResponse({"error": "bad hash"}, 403)

    token = jwt.encode({
        "id": data["id"],
        "username": data.get("username"),
        "exp": int(time.time()) + 3600
    }, JWT_SECRET, algorithm=JWT_ALGO)

    return RedirectResponse(
        url=f"https://fenixaibot.ru/dashboard.html?token={token}",
        status_code=302
    )
