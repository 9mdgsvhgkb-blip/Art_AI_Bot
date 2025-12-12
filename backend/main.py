import os
import uuid
import subprocess
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()

INPUT_DIR = "input"
TMP_DIR = "tmp"
OUTPUT_DIR = "output"

for d in [INPUT_DIR, TMP_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    max_highlights: int = Form(3)
):
    try:
        # Save uploaded video
        video_id = str(uuid.uuid4())
        input_path = f"{INPUT_DIR}/{video_id}.mp4"

        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Extract audio
        audio_path = f"{TMP_DIR}/{video_id}.wav"
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            audio_path,
            "-y"
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 🔥 New OpenAI API (правильный)
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-tts",
                file=audio_file
            )

        text = transcript.text if hasattr(transcript, "text") else transcript["text"]

        # Create highlights
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Extract useful short highlight timestamps."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        clips = []
        for i in range(max_highlights):
            clip_output = f"{OUTPUT_DIR}/{video_id}_{i}.mp4"
            clips.append({
                "title": f"Clip #{i+1}",
                "file": f"{video_id}_{i}.mp4"
            })
            # demo blank clip
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "color=c=black:s=320x240:d=2",
                clip_output
            ])

        return JSONResponse({"highlights": clips})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/download/{filename}")
async def download_file(filename: str):
    path = f"{OUTPUT_DIR}/{filename}"
    if os.path.exists(path):
        return FileResponse(path, media_type="video/mp4")
    return JSONResponse({"error": "File not found"}, status_code=404)
