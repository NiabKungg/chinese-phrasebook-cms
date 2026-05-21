from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import verify_password, create_access_token, hash_password
from ..models import AdminUser
from ..schemas import LoginRequest, Token
from ..config import DEFAULT_USERNAME, DEFAULT_PASSWORD

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _ensure_default_admin(db: Session):
    existing = db.query(AdminUser).filter(AdminUser.username == DEFAULT_USERNAME).first()
    if not existing:
        user = AdminUser(
            username=DEFAULT_USERNAME,
            password_hash=hash_password(DEFAULT_PASSWORD),
        )
        db.add(user)
        db.commit()


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    _ensure_default_admin(db)
    user = db.query(AdminUser).filter(AdminUser.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    _ensure_default_admin(db)
    user = db.query(AdminUser).first()
    if not user or not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Password changed successfully"}
