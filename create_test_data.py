import sys
import os
from datetime import datetime

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app.db.base import SessionLocal
from app.models.user import User
from app.models.friendship import Friendship
from app.models.cloth_item import ClothItem
from app.services.auth import get_password_hash

def create_test_data(user_email: str):
    db = SessionLocal()
    try:
        # 1. 내 계정 찾기
        me = db.query(User).filter(User.email == user_email).first()
        if not me:
            print(f"Error: User with email '{user_email}' not found.")
            return

        print(f"Found user: {me.name} ({me.email})")

        # 2. 친구 계정 생성 (없으면)
        friend_email = "friend@test.com"
        friend = db.query(User).filter(User.email == friend_email).first()
        if not friend:
            print("Creating friend account...")
            friend = User(
                email=friend_email,
                name="Best Friend",
                hashed_password=get_password_hash("password")
            )
            db.add(friend)
            db.commit()
            db.refresh(friend)
            print(f"Created friend: {friend.name} ({friend.email})")
        else:
            print(f"Found friend: {friend.name}")

        # 3. 친구 관계 맺기 (Accepted)
        friendship = db.query(Friendship).filter(
            ((Friendship.user_id_1 == me.id) & (Friendship.user_id_2 == friend.id)) |
            ((Friendship.user_id_1 == friend.id) & (Friendship.user_id_2 == me.id))
        ).first()

        if not friendship:
            print("Creating friendship...")
            friendship = Friendship(
                user_id_1=me.id,
                user_id_2=friend.id,
                status="accepted"
            )
            db.add(friendship)
            db.commit()
            print("Friendship created and accepted!")
        else:
            if friendship.status != "accepted":
                friendship.status = "accepted"
                db.commit()
                print("Updated friendship status to accepted.")
            else:
                print("Already friends.")

        # 4. 옷 데이터 생성 (내가 빌린 옷)
        borrowed_item = db.query(ClothItem).filter(
            ClothItem.borrower_id == me.id,
            ClothItem.lender_id == friend.id
        ).first()

        if not borrowed_item:
            print("Creating borrowed item...")
            borrowed_item = ClothItem(
                borrower_id=me.id,
                lender_id=friend.id,
                image_url="https://via.placeholder.com/150",
                description="Friend's cool jacket",
                status="borrowed",
                borrowed_at=datetime.utcnow()
            )
            db.add(borrowed_item)
            db.commit()
            print("Created borrowed item.")

        # 5. 옷 데이터 생성 (내가 빌려준 옷)
        lent_item = db.query(ClothItem).filter(
            ClothItem.borrower_id == friend.id,
            ClothItem.lender_id == me.id
        ).first()

        if not lent_item:
            print("Creating lent item...")
            lent_item = ClothItem(
                borrower_id=friend.id,
                lender_id=me.id,
                image_url="https://via.placeholder.com/150",
                description="My vintage jeans",
                status="borrowed",
                borrowed_at=datetime.utcnow()
            )
            db.add(lent_item)
            db.commit()
            print("Created lent item.")

        print("\nSuccess! Test data generated.")
        print("1. Friend 'Best Friend' (friend@test.com) added.")
        print("2. You borrowed a jacket from Best Friend.")
        print("3. You lent jeans to Best Friend.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_test_data.py <your_email>")
    else:
        create_test_data(sys.argv[1])
