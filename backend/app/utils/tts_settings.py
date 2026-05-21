from sqlalchemy.orm import Session
from ..models import TTSSettings

DEFAULT_SETTINGS = {
    "voice": "zh-CN-XiaoxiaoNeural",
    "rate": "-10%",
    "pitch": "+0Hz",
}


def get_tts_settings(db: Session) -> dict:
    settings = db.query(TTSSettings).first()
    if not settings:
        settings = TTSSettings(**DEFAULT_SETTINGS)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return {"voice": settings.voice, "rate": settings.rate, "pitch": settings.pitch}


def update_tts_settings(db: Session, voice: str = None, rate: str = None, pitch: str = None) -> dict:
    settings = db.query(TTSSettings).first()
    if not settings:
        settings = TTSSettings()
        db.add(settings)
    if voice is not None:
        settings.voice = voice
    if rate is not None:
        settings.rate = rate
    if pitch is not None:
        settings.pitch = pitch
    db.commit()
    db.refresh(settings)
    return {"voice": settings.voice, "rate": settings.rate, "pitch": settings.pitch}
