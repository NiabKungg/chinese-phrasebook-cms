import asyncio
import os
import edge_tts
from ..config import AUDIO_DIR

os.makedirs(AUDIO_DIR, exist_ok=True)


async def generate_audio_file(text: str, filename: str, voice: str, rate: str, pitch: str) -> str:
    filepath = os.path.join(AUDIO_DIR, filename)
    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=rate,
        pitch=pitch,
    )
    await communicate.save(filepath)
    return filepath


def audio_file_exists(filename: str) -> bool:
    return os.path.isfile(os.path.join(AUDIO_DIR, filename))
