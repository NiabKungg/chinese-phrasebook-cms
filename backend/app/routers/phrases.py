from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
from ..database import get_db
from ..auth import get_current_user
from ..models import AdminUser, Phrase, Category
from ..schemas import PhraseCreate, PhraseUpdate, PhraseOut
from ..config import AUDIO_DIR
from ..utils.audio_gen import generate_audio_file
from ..utils.tts_settings import get_tts_settings

router = APIRouter(prefix="/api/phrases", tags=["phrases"])


def _phrase_to_out(p: Phrase) -> PhraseOut:
    return PhraseOut(
        id=p.id,
        chinese=p.chinese,
        pinyin=p.pinyin,
        thai=p.thai,
        category_id=p.category_id,
        sort_order=p.sort_order,
        audio_file=p.audio_file,
        created_at=p.created_at,
    )


@router.get("/", response_model=List[PhraseOut])
def list_phrases(category_id: int = None, db: Session = Depends(get_db)):
    q = db.query(Phrase).order_by(Phrase.sort_order, Phrase.id)
    if category_id:
        q = q.filter(Phrase.category_id == category_id)
    phrases = q.all()
    return [_phrase_to_out(p) for p in phrases]


@router.get("/{phrase_id}", response_model=PhraseOut)
def get_phrase(phrase_id: int, db: Session = Depends(get_db)):
    p = db.query(Phrase).filter(Phrase.id == phrase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Phrase not found")
    return _phrase_to_out(p)


@router.post("/", response_model=PhraseOut, status_code=status.HTTP_201_CREATED)
async def create_phrase(body: PhraseCreate, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == body.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    phrase = Phrase(
        chinese=body.chinese,
        pinyin=body.pinyin,
        thai=body.thai,
        category_id=body.category_id,
        sort_order=body.sort_order,
    )
    db.add(phrase)
    db.commit()
    db.refresh(phrase)

    try:
        settings = get_tts_settings(db)
        filename = f"phrase_{phrase.id}.mp3"
        await generate_audio_file(phrase.chinese, filename, settings["voice"], settings["rate"], settings["pitch"])
        phrase.audio_file = filename
        db.commit()
        db.refresh(phrase)
    except Exception:
        pass

    return _phrase_to_out(phrase)


@router.put("/{phrase_id}", response_model=PhraseOut)
def update_phrase(phrase_id: int, body: PhraseUpdate, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    p = db.query(Phrase).filter(Phrase.id == phrase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Phrase not found")

    if body.chinese is not None:
        p.chinese = body.chinese
    if body.pinyin is not None:
        p.pinyin = body.pinyin
    if body.thai is not None:
        p.thai = body.thai
    if body.category_id is not None:
        cat = db.query(Category).filter(Category.id == body.category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        p.category_id = body.category_id
    if body.sort_order is not None:
        p.sort_order = body.sort_order

    db.commit()
    db.refresh(p)
    return _phrase_to_out(p)


@router.delete("/{phrase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_phrase(phrase_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    p = db.query(Phrase).filter(Phrase.id == phrase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Phrase not found")
    if p.audio_file:
        filepath = os.path.join(AUDIO_DIR, p.audio_file)
        if os.path.isfile(filepath):
            os.remove(filepath)
    db.delete(p)
    db.commit()
    return None
