import os
import time
import threading
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from movie_utils import ensure_dirs, cut_clip_ffmpeg, burn_ass_subtitles
from transcribe import transcribe
from highlights import pick_highlights
from subtitles import build_ass_subtitles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TMP_DIR = os.path.join(BASE_DIR, "tmp")

ensure_dirs(INPUT_DIR, OUTPUT_DIR, TMP_DIR)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище задач (пока в памяти)
JOBS = {}


def process_video(job_id, video_path, max_highlights):
    try:
        JOBS[job_id]["status"] = "processing"

        segments = transcribe(video_path)
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


@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    max_highlights: int = Form(5)
):
    job_id = str(int(time.time() * 1000))
    video_path = os.path.join(INPUT_DIR, f"{job_id}_{file.filename}")

    with open(video_path, "wb") as f:
        f.write(await file.read())

    JOBS[job_id] = {
        "status": "queued",
        "results": []
    }

    thread = threading.Thread(
        target=process_video,
        args=(job_id, video_path, max_highlights),
        daemon=True
    )
    thread.start()

    return JSONResponse({"job_id": job_id})


@app.get("/status/{job_id}")
def status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404)
    return {"status": job["status"]}


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
