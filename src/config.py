# config.py
import os
from dotenv import load_dotenv

load_dotenv()

VIDEO_API_LINK = os.getenv("VIDEO_API_LINK")
VIDEO_API_PROJECT = os.getenv("VIDEO_API_PROJECT")
VIDEO_API_BUCKET = os.getenv("VIDEO_API_BUCKET")
VIDEO_FOLDER = os.path.abspath(os.getenv("VIDEO_FOLDER"))
BACKEND_URL = os.getenv("BACKEND_URL")