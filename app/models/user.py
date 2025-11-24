from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    friendships_initiated = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id_1",
        back_populates="user_1"
    )
    friendships_received = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id_2",
        back_populates="user_2"
    )
    items_borrowed = relationship(
        "ClothItem",
        foreign_keys="ClothItem.borrower_id",
        back_populates="borrower"
    )
    items_lent = relationship(
        "ClothItem",
        foreign_keys="ClothItem.lender_id",
        back_populates="lender"
    )

