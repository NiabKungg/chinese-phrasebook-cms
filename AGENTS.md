# AGENTS.md

## Project
Full-stack Chinese phrasebook for Thai travelers. 

- **Backend:** FastAPI + SQLite + edge_tts
- **Admin Panel:** Vanilla JS + TailwindCSS (SPA at `admin/index.html`)
- **Public Frontend:** `index.html` - fetches data dynamically from API

## Architecture
```
backend/
  app/
    main.py          FastAPI entry point
    database.py      SQLAlchemy engine + session
    models.py         ORM models (Category, Phrase, TTSSettings, Analytics, AdminUser)
    schemas.py        Pydantic schemas
    auth.py           bcrypt + JWT auth
    config.py         Settings (DB path, secrets, defaults)
    routers/
      auth.py         POST /api/auth/login
      categories.py   CRUD /api/categories
      phrases.py      CRUD /api/phrases
      audio.py        TTS generation + settings
      analytics.py    Dashboard stats
      public.py       GET /api/public/phrasebook, POST /api/public/track
    utils/
      audio_gen.py    edge_tts wrapper
      tts_settings.py TTS settings CRUD
  seed.py             Seed DB from legacy sentence data
admin/
  index.html          Admin CMS SPA
index.html            Public phrasebook (dynamic API fetch)
audio/                MP3 files (phrase_{id}.mp3)
```

## Running the app
```bash
cd backend
pip install -r requirements.txt
python seed.py                    # Seed DB (skips audio if --quick)
python -m uvicorn app.main:app --reload
```
- API at http://localhost:8000
- Admin at `admin/index.html` (open directly, points to localhost:8000)
- Admin credentials: `admin` / `admin123`

## Audio files
- Naming: `audio/phrase_{id}.mp3` (e.g. `audio/phrase_42.mp3`)
- Generated via edge_tts with configurable voice/rate/pitch in Admin CMS
- Files are not committed to git

## When adding phrases
- Use the Admin CMS (recommended) or the API directly
- Audio auto-generated from CMS via "Regenerate" button
- The old `generate_audio.py` is kept for reference but the canonical audio pipeline is now in `backend/app/utils/audio_gen.py`
