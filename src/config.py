import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
FRAMES_DIR = DATA_DIR / "frames"
CHROMA_DIR = ROOT_DIR / "chroma_db"

TRANSCRIPT_PATH = DATA_DIR / "transcript.txt"
VIDEO_PATH = DATA_DIR / "video.mp4"
CAPTIONS_PATH = DATA_DIR / "captions.json"
INDEX_META_PATH = DATA_DIR / "index_meta.json"

GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS", "")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_B2B")
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat-2-Max")
GIGACHAT_VISION_MODEL = os.getenv("GIGACHAT_VISION_MODEL", "GigaChat-2-Max")

YOUTUBE_URL = os.getenv("YOUTUBE_URL", "https://youtu.be/WXUINIDj5qI")

FRAME_INTERVAL_SEC = 6
CHUNK_SIZE = 380
CHUNK_OVERLAP = 80

DEFAULT_TOP_K = 5
DEFAULT_RRF_K = 60

COLLECTION_NAME = "global_warming"

DATA_DIR.mkdir(exist_ok=True)
FRAMES_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)
