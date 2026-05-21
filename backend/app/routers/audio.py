from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import AdminUser, Phrase
from ..schemas import TTSSettingsBase, TTSSettingsOut
from ..utils.tts_settings import get_tts_settings, update_tts_settings
from ..utils.audio_gen import generate_audio_file, audio_file_exists
import os
from ..config import AUDIO_DIR

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.get("/check/{phrase_id}")
def check_audio(phrase_id: int, db: Session = Depends(get_db)):
    p = db.query(Phrase).filter(Phrase.id == phrase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Phrase not found")
    has_file = p.audio_file and audio_file_exists(p.audio_file)
    return {"phrase_id": phrase_id, "has_audio": has_file, "audio_file": p.audio_file if has_file else None}


@router.post("/regenerate/{phrase_id}")
async def regenerate_audio(phrase_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    p = db.query(Phrase).filter(Phrase.id == phrase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Phrase not found")

    settings = get_tts_settings(db)
    filename = f"phrase_{p.id}.mp3"

    await generate_audio_file(p.chinese, filename, settings["voice"], settings["rate"], settings["pitch"])

    p.audio_file = filename
    db.commit()
    db.refresh(p)
    return {"message": "Audio regenerated", "audio_file": filename, "phrase_id": phrase_id, "has_audio": True}


@router.post("/regenerate-all")
async def regenerate_all_audio(db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    settings = get_tts_settings(db)
    phrases = db.query(Phrase).all()
    generated = 0
    errors = 0

    for p in phrases:
        try:
            filename = f"phrase_{p.id}.mp3"
            await generate_audio_file(p.chinese, filename, settings["voice"], settings["rate"], settings["pitch"])
            p.audio_file = filename
            generated += 1
        except Exception:
            errors += 1

    db.commit()
    return {"generated": generated, "errors": errors, "total": len(phrases)}


@router.get("/settings", response_model=TTSSettingsOut)
def get_settings(db: Session = Depends(get_db)):
    s = get_tts_settings(db)
    return TTSSettingsOut(id=1, **s)


@router.put("/settings", response_model=TTSSettingsOut)
def update_settings(body: TTSSettingsBase, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    s = update_tts_settings(db, voice=body.voice, rate=body.rate, pitch=body.pitch)
    return TTSSettingsOut(id=1, **s)
