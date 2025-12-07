from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.database import get_db
from app.models.database_models import Event

router = APIRouter()


class PublicEventResponse(BaseModel):
    event_code: str
    name: str
    issue_location: str
    issue_date: Optional[date] = None
    auto_issue_date: bool = False

    class Config:
        from_attributes = True


@router.get("/{event_code}", response_model=PublicEventResponse)
async def get_event_by_code(
    event_code: str,
    db: Session = Depends(get_db)
):
    """イベントコードからイベント情報を取得（公開API）"""
    event = db.query(Event).filter(Event.event_code == event_code).first()

    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    if not event.is_active:
        raise HTTPException(status_code=403, detail="このURLは現在無効です")

    return PublicEventResponse(
        event_code=event.event_code,
        name=event.name,
        issue_location=event.issue_location,
        issue_date=event.issue_date,
        auto_issue_date=event.auto_issue_date or False
    )
