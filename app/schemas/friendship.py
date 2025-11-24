from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class FriendRequestCreate(BaseModel):
    friend_email: EmailStr

class FriendRequestCreateById(BaseModel):
    friend_id: int

class FriendRequestItem(BaseModel):
    friendship_id: int
    to_user_id: int
    to_user_email: str
    to_user_name: str
    to_user_profile_image: Optional[str] = None
    requested_at: datetime

class FriendInfo(BaseModel):
    id: int
    name: str
    email: str
    profile_image_url: Optional[str] = None

class FriendshipResponse(BaseModel):
    id: int
    user_id_1: int
    user_id_2: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
