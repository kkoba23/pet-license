from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.database_models import Admin, Event
from app.services.auth_service import (
    authenticate_admin,
    create_access_token,
    get_current_admin,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()


# === Pydanticモデル ===
class Token(BaseModel):
    access_token: str
    token_type: str


class AdminInfo(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    name: str
    issue_location: str
    issue_date: Optional[date] = None
    auto_issue_date: bool = False


class EventUpdate(BaseModel):
    name: Optional[str] = None
    issue_location: Optional[str] = None
    issue_date: Optional[date] = None
    auto_issue_date: Optional[bool] = None
    is_active: Optional[bool] = None


class EventResponse(BaseModel):
    id: int
    event_code: str
    name: str
    issue_location: str
    issue_date: Optional[date] = None
    auto_issue_date: bool = False
    is_active: bool
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# === 認証エンドポイント ===
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    admin = authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AdminInfo)
async def get_current_admin_info(
    current_admin: Admin = Depends(get_current_admin)
):
    return current_admin


# === イベント管理エンドポイント ===
@router.get("/events", response_model=List[EventResponse])
async def list_events(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    events = db.query(Event).order_by(Event.created_at.desc()).all()
    return [
        EventResponse(
            id=e.id,
            event_code=e.event_code,
            name=e.name,
            issue_location=e.issue_location,
            issue_date=e.issue_date,
            auto_issue_date=e.auto_issue_date or False,
            is_active=e.is_active,
            created_at=e.created_at.isoformat() if e.created_at else None
        )
        for e in events
    ]


@router.post("/events", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    import uuid
    new_event = Event(
        event_code=str(uuid.uuid4())[:8],
        name=event.name,
        issue_location=event.issue_location,
        issue_date=event.issue_date,
        auto_issue_date=event.auto_issue_date,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return EventResponse(
        id=new_event.id,
        event_code=new_event.event_code,
        name=new_event.name,
        issue_location=new_event.issue_location,
        issue_date=new_event.issue_date,
        auto_issue_date=new_event.auto_issue_date or False,
        is_active=new_event.is_active,
        created_at=new_event.created_at.isoformat() if new_event.created_at else None
    )


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")
    return EventResponse(
        id=event.id,
        event_code=event.event_code,
        name=event.name,
        issue_location=event.issue_location,
        issue_date=event.issue_date,
        auto_issue_date=event.auto_issue_date or False,
        is_active=event.is_active,
        created_at=event.created_at.isoformat() if event.created_at else None
    )


@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    if event_update.name is not None:
        event.name = event_update.name
    if event_update.issue_location is not None:
        event.issue_location = event_update.issue_location
    if event_update.issue_date is not None:
        event.issue_date = event_update.issue_date
    if event_update.auto_issue_date is not None:
        event.auto_issue_date = event_update.auto_issue_date
    if event_update.is_active is not None:
        event.is_active = event_update.is_active

    db.commit()
    db.refresh(event)
    return EventResponse(
        id=event.id,
        event_code=event.event_code,
        name=event.name,
        issue_location=event.issue_location,
        issue_date=event.issue_date,
        auto_issue_date=event.auto_issue_date or False,
        is_active=event.is_active,
        created_at=event.created_at.isoformat() if event.created_at else None
    )


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    db.delete(event)
    db.commit()
    return {"message": "イベントを削除しました"}
