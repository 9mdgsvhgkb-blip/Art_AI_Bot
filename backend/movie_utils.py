import os
import subprocess


def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def extract_audio(video_path, audio_path):
    """
    Извлекает аудио из видео (16kHz mono) — если понадобится для Whisper отдельно
    """
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ], check=True)


def cut_clip_ffmpeg(video_path, start, end, out_path):
    """
    Нарезает клип по таймкодам (без перекодирования где возможно)
    """
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", video_path,
        "-to", str(end),
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        out_path
    ], check=True)


def burn_ass_subtitles(video_path, ass_path, out_path):
    """
    Прожигает ASS караоке-субтитры + вертикальный формат 9:16
    """
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf",
        f"scale=1080:1920,ass={ass_path}",
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        out_path
    ], check=True)
