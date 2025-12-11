import os
import subprocess
import shlex
from typing import List, Dict

def ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

def run_cmd(cmd: List[str]):
    """
    Run command and raise subprocess.CalledProcessError on failure.
    """
    subprocess.check_call(cmd)

def extract_audio(video_path: str, out_audio: str):
    """
    Extract mono 16kHz wav suitable for many ASR models.
    """
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        out_audio
    ]
    run_cmd(cmd)
    return out_audio

def cut_clip_ffmpeg(video_path: str, start: float, end: float, out_path: str):
    """
    Cut using ffmpeg with accurate seeking. start/end in seconds (float).
    """
    duration = max(0.1, end - start)
    # use -ss before -i for fast seek approx, but do precise re-encode by placing -ss after -i
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", video_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        out_path
    ]
    run_cmd(cmd)
    return out_path

def generate_srt(subtitles: List[Dict], srt_path: str):
    """
    subtitles: [{'start': 0.0, 'end': 4.0, 'text': 'hello'}, ...]
    Writes simple SRT file.
    """
    def fmt_time(t):
        # t seconds -> "HH:MM:SS,mmm"
        hours = int(t // 3600)
        minutes = int((t % 3600) // 60)
        seconds = int(t % 60)
        millis = int((t - int(t)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, s in enumerate(subtitles, start=1):
            start = fmt_time(float(s.get("start", 0.0)))
            end = fmt_time(float(s.get("end", start)))
            text = s.get("text", "").replace("-->", "->")
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    return srt_path

def burn_subtitles_ffmpeg(video_path: str, subtitles: List[Dict], out_path: str, tmp_dir: str):
    """
    Generate SRT then burn subtitles into video using ffmpeg subtitles filter.
    Needs libass support in ffmpeg build (standard).
    """
    srt_path = os.path.join(tmp_dir, f"subs_{os.path.basename(out_path)}.srt")
    generate_srt(subtitles, srt_path)
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        out_path
    ]
    run_cmd(cmd)
    # optionally remove srt file
    try:
        os.remove(srt_path)
    except Exception:
        pass
    return out_path