from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..auth import get_current_user
from ..models import AdminUser, Category, Phrase
from ..schemas import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/api/categories", tags=["categories"])


def _category_to_out(cat: Category) -> CategoryOut:
    return CategoryOut(
        id=cat.id,
        name=cat.name,
        icon=cat.icon,
        sort_order=cat.sort_order,
        phrase_count=len(cat.phrases),
        created_at=cat.created_at,
    )


@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).order_by(Category.sort_order, Category.id).all()
    return [_category_to_out(c) for c in cats]


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return _category_to_out(cat)


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryCreate, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    cat = Category(name=body.name, icon=body.icon, sort_order=body.sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return _category_to_out(cat)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, body: CategoryUpdate, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if body.name is not None:
        cat.name = body.name
    if body.icon is not None:
        cat.icon = body.icon
    if body.sort_order is not None:
        cat.sort_order = body.sort_order
    db.commit()
    db.refresh(cat)
    return _category_to_out(cat)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return None
