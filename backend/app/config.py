import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'phrasebook.db')}"
AUDIO_DIR = os.path.join(os.path.dirname(BASE_DIR), "audio")
SECRET_KEY = "change-this-to-a-secure-random-secret-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"
