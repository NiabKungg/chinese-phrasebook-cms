from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Category, Phrase, Analytics
from typing import List
from pydantic import BaseModel
from ..config import AUDIO_DIR
import os

router = APIRouter(prefix="/api/public", tags=["public"])


class PublicPhrase(BaseModel):
    id: int
    chinese: str
    pinyin: str
    thai: str
    audio_file: str | None = None

    model_config = {"from_attributes": True}


class PublicCategory(BaseModel):
    id: int
    name: str
    icon: str
    phrases: List[PublicPhrase]

    model_config = {"from_attributes": True}


@router.get("/phrasebook", response_model=List[PublicCategory])
def get_phrasebook(db: Session = Depends(get_db)):
    cats = db.query(Category).order_by(Category.sort_order, Category.id).all()
    result = []
    for cat in cats:
        phrases = []
        for p in sorted(cat.phrases, key=lambda x: (x.sort_order, x.id)):
            audio_file = None
            if p.audio_file and os.path.isfile(os.path.join(AUDIO_DIR, p.audio_file)):
                audio_file = p.audio_file
            phrases.append(PublicPhrase(
                id=p.id,
                chinese=p.chinese,
                pinyin=p.pinyin,
                thai=p.thai,
                audio_file=audio_file,
            ))
        if phrases:
            result.append(PublicCategory(
                id=cat.id,
                name=cat.name,
                icon=cat.icon,
                phrases=phrases,
            ))
    return result


@router.post("/track")
async def track_visit(request: Request, db: Session = Depends(get_db)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_record = db.query(Analytics).filter(Analytics.date == today).first()
    if today_record:
        today_record.page_views += 1
    else:
        today_record = Analytics(date=today, page_views=1, unique_visitors=1)
        db.add(today_record)
    db.commit()
    return {"status": "ok"}
