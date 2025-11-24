from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClothItemCreate(BaseModel):
    lender_id: int
    image_url: str
    description: Optional[str] = None

class ClothItemResponse(BaseModel):
    id: int
    borrower_id: int
    lender_id: int
    image_url: str
    description: Optional[str] = None
    status: str
    borrowed_at: datetime
    return_requested_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserSummary(BaseModel):
    id: int
    name: str
    profile_image_url: Optional[str] = None

class ClothItemWithUser(ClothItemResponse):
    borrower: Optional[UserSummary] = None
    lender: Optional[UserSummary] = None

class ImageUploadResponse(BaseModel):
    image_url: str
    filename: str
