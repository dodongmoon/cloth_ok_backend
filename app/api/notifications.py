from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.schemas.notification import Notification
from app.services.notification import notification_service

router = APIRouter()

@router.get("/", response_model=List[Notification])
def read_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 알림 목록 조회
    """
    return notification_service.get_my_notifications(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/{notification_id}/read", response_model=Notification)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    알림 읽음 처리
    """
    notification = notification_service.mark_as_read(db, notification_id=notification_id, user_id=current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
