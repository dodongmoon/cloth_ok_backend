from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

class NotificationService:
    def create_notification(self, db: Session, notification: NotificationCreate) -> Notification:
        db_notification = Notification(
            user_id=notification.user_id,
            type=notification.type,
            message=notification.message,
            related_item_id=notification.related_item_id
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification

    def get_my_notifications(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def mark_as_read(self, db: Session, notification_id: int, user_id: int):
        notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        return notification

notification_service = NotificationService()
