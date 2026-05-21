from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Analytics, Phrase, Category
from ..schemas import DashboardStats
import os
from ..config import AUDIO_DIR

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    today = datetime.utcnow().strftime("%Y-%m-%d")

    total_phrases = db.query(Phrase).count()
    total_categories = db.query(Category).count()
    total_page_views = db.query(Analytics).with_entities(
        Analytics.page_views
    ).all()
    total_page_views = sum(r[0] for r in total_page_views) if total_page_views else 0

    today_record = db.query(Analytics).filter(Analytics.date == today).first()
    today_views = today_record.page_views if today_record else 0

    phrases = db.query(Phrase).all()
    phrases_with_audio = 0
    phrases_missing_audio = 0
    for p in phrases:
        if p.audio_file and os.path.isfile(os.path.join(AUDIO_DIR, p.audio_file)):
            phrases_with_audio += 1
        else:
            phrases_missing_audio += 1

    return DashboardStats(
        total_phrases=total_phrases,
        total_categories=total_categories,
        total_page_views=total_page_views,
        today_views=today_views,
        phrases_with_audio=phrases_with_audio,
        phrases_missing_audio=phrases_missing_audio,
    )
