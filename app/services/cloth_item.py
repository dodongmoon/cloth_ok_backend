from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.cloth_item import ClothItem
from app.models.user import User
from datetime import datetime
from typing import List, Optional

def create_cloth_item(
    db: Session, 
    borrower_id: int, 
    lender_id: int, 
    image_url: str, 
    description: str = None
) -> ClothItem:
    item = ClothItem(
        borrower_id=borrower_id,
        lender_id=lender_id,
        image_url=image_url,
        description=description,
        status="borrowed",
        borrowed_at=datetime.utcnow()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_borrowed_items(db: Session, user_id: int, friend_id: int = None) -> List[ClothItem]:
    query = db.query(ClothItem).filter(ClothItem.borrower_id == user_id)
    
    if friend_id:
        query = query.filter(ClothItem.lender_id == friend_id)
        
    return query.order_by(ClothItem.borrowed_at.desc()).all()

def get_lent_items(db: Session, user_id: int, friend_id: int = None) -> List[ClothItem]:
    query = db.query(ClothItem).filter(ClothItem.lender_id == user_id)
    
    if friend_id:
        query = query.filter(ClothItem.borrower_id == friend_id)
        
    return query.order_by(ClothItem.borrowed_at.desc()).all()

def request_return(db: Session, item_id: int, user_id: int) -> Optional[ClothItem]:
    item = db.query(ClothItem).filter(
        ClothItem.id == item_id,
        ClothItem.borrower_id == user_id
    ).first()
    
    if not item or item.status != "borrowed":
        return None
        
    item.status = "return_requested"
    item.return_requested_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item

def approve_return(db: Session, item_id: int, user_id: int) -> Optional[ClothItem]:
    item = db.query(ClothItem).filter(
        ClothItem.id == item_id,
        ClothItem.lender_id == user_id
    ).first()
    
    if not item or item.status != "return_requested":
        return None
        
    item.status = "returned"
    item.returned_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item

def reject_return(db: Session, item_id: int, user_id: int) -> Optional[ClothItem]:
    item = db.query(ClothItem).filter(
        ClothItem.id == item_id,
        ClothItem.lender_id == user_id
    ).first()
    
    if not item or item.status != "return_requested":
        return None
        
    item.status = "borrowed"
    item.return_requested_at = None
    db.commit()
    db.refresh(item)
    return item

def get_cloth_item_by_id(db: Session, item_id: int) -> Optional[ClothItem]:
    return db.query(ClothItem).filter(ClothItem.id == item_id).first()
