import os

# BASE_DIR = project_root/backend/..
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TMP_DIR = os.path.join(BASE_DIR, "tmp")

# Read API key from environment (do NOT hardcode)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Host/port for uvicorn
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))