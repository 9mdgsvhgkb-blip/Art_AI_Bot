import os

# папки для файлов
INPUT_DIR = "input"
OUTPUT_DIR = "output"
TMP_DIR = "tmp"

# ключ OpenAI берём из переменной среды
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
