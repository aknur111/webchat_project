from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.config.database import get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.username == payload.username))
    if exists:
        raise HTTPException(400, "Username already exists")
    user = User(username=payload.username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=user.id, username=user.username)
