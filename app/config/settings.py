"""
Configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_AUDIO_DIR = BASE_DIR / "output_audio"
SKILL_DIR = BASE_DIR / "app" / "templates"

# Ensuring directory existence
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUT_AUDIO_DIR.mkdir(exist_ok=True)

AUDIO_VOICE="en-IN-NeerjaNeural"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
ACTIVE_MODEL = "gpt-4o-mini"
OPENAI_BASE_URL="https://api.openai.com/v1"

# Models
EMBEDDING_MODEL="all-MiniLM-L6-v2"
SUMMARIZER_MODEL = "gpt-4o-mini"

# Chroma config
VECTOR_DIR = BASE_DIR/"chroma_db"

# Presets for chunk size
MIN_WORDS=200
MAX_WORDS=250
TOP_N_RESULTS=5

# TTS model config
MODEL_SIZE="small"
DEVICE="cpu"
COMPUTE_TYPE="int8"

#entity model
ENTITY_MODEL="dslim/bert-base-NER"


