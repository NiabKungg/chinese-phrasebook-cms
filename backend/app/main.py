from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .routers import auth, categories, phrases, audio, analytics, public
from .auth import hash_password
from .models import AdminUser
from .config import DEFAULT_USERNAME, DEFAULT_PASSWORD

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chinese Phrasebook API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(phrases.router)
app.include_router(audio.router)
app.include_router(analytics.router)
app.include_router(public.router)


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        existing = db.query(AdminUser).first()
        if not existing:
            db.add(AdminUser(
                username=DEFAULT_USERNAME,
                password_hash=hash_password(DEFAULT_PASSWORD),
            ))
            db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}
