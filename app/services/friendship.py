from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.friendship import Friendship
from app.models.user import User
from typing import List, Optional

def check_existing_friendship(db: Session, user_id_1: int, user_id_2: int) -> Optional[Friendship]:
    return db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id_1 == user_id_1, Friendship.user_id_2 == user_id_2),
            and_(Friendship.user_id_1 == user_id_2, Friendship.user_id_2 == user_id_1)
        )
    ).first()

def create_friend_request(db: Session, sender_id: int, receiver_id: int) -> Friendship:
    friendship = Friendship(
        user_id_1=sender_id,
        user_id_2=receiver_id,
        status="pending"
    )
    db.add(friendship)
    db.commit()
    db.refresh(friendship)
    return friendship

def get_friends(db: Session, user_id: int) -> List[dict]:
    friendships = db.query(Friendship).filter(
        or_(Friendship.user_id_1 == user_id, Friendship.user_id_2 == user_id),
        Friendship.status == "accepted"
    ).all()
    
    friends = []
    for f in friendships:
        friend_user = f.user_2 if f.user_id_1 == user_id else f.user_1
        friends.append({
            "id": friend_user.id,
            "name": friend_user.name,
            "email": friend_user.email,
            "profile_image_url": friend_user.profile_image_url
        })
    return friends

def get_received_friend_requests(db: Session, user_id: int) -> List[dict]:
    requests = db.query(Friendship).filter(
        Friendship.user_id_2 == user_id,
        Friendship.status == "pending"
    ).all()
    
    result = []
    for req in requests:
        sender = req.user_1
        result.append({
            "friendship_id": req.id,
            "to_user_id": sender.id,
            "to_user_email": sender.email,
            "to_user_name": sender.name,
            "to_user_profile_image": sender.profile_image_url,
            "requested_at": req.created_at
        })
    return result

def get_sent_friend_requests(db: Session, user_id: int) -> List[dict]:
    requests = db.query(Friendship).filter(
        Friendship.user_id_1 == user_id,
        Friendship.status == "pending"
    ).all()
    
    result = []
    for req in requests:
        receiver = req.user_2
        result.append({
            "friendship_id": req.id,
            "to_user_id": receiver.id,
            "to_user_email": receiver.email,
            "to_user_name": receiver.name,
            "to_user_profile_image": receiver.profile_image_url,
            "requested_at": req.created_at
        })
    return result

def accept_friend_request(db: Session, friendship_id: int, user_id: int) -> Optional[Friendship]:
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.user_id_2 == user_id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        return None
        
    friendship.status = "accepted"
    db.commit()
    db.refresh(friendship)
    return friendship

def reject_friend_request(db: Session, friendship_id: int, user_id: int) -> bool:
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.user_id_2 == user_id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        return False
        
    db.delete(friendship)
    db.commit()
    return True

def delete_friendship(db: Session, friendship_id: int, user_id: int) -> bool:
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        or_(Friendship.user_id_1 == user_id, Friendship.user_id_2 == user_id)
    ).first()
    
    if not friendship:
        return False
        
    db.delete(friendship)
    db.commit()
    return True
