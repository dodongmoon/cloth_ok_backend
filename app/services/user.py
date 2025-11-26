from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import get_password_hash

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    # 1. 친구 관계 삭제
    from app.models.friendship import Friendship
    from sqlalchemy import or_
    db.query(Friendship).filter(
        or_(Friendship.user_id_1 == user_id, Friendship.user_id_2 == user_id)
    ).delete(synchronize_session=False)
    
    # 2. 아이템 삭제 (빌려준 거, 빌린 거 모두)
    from app.models.cloth_item import ClothItem
    db.query(ClothItem).filter(
        or_(ClothItem.borrower_id == user_id, ClothItem.lender_id == user_id)
    ).delete(synchronize_session=False)
    
    # 3. 사용자 삭제
    db.delete(db_user)
    db.commit()
    return True
