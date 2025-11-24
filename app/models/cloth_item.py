from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class ClothItem(Base):
    __tablename__ = "cloth_items"

    id = Column(Integer, primary_key=True, index=True)
    borrower_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 빌린 사람
    lender_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 빌려준 사람
    image_url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="borrowed")  # borrowed, return_requested, returned
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    return_requested_at = Column(DateTime, nullable=True)
    returned_at = Column(DateTime, nullable=True)

    # Relationships
    borrower = relationship("User", foreign_keys=[borrower_id], back_populates="items_borrowed")
    lender = relationship("User", foreign_keys=[lender_id], back_populates="items_lent")
    notifications = relationship("Notification", back_populates="cloth_item", cascade="all, delete-orphan")

