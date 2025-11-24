from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.base import get_db
from app.schemas.cloth_item import (
    ClothItemCreate,
    ClothItemResponse,
    ClothItemWithUser
)
from app.services import cloth_item as item_service
from app.services import friendship as friendship_service
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("", response_model=ClothItemResponse, status_code=status.HTTP_201_CREATED)
def create_cloth_item(
    item_data: ClothItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    옷을 빌립니다 (대출 등록).
    
    **인증 필요**
    
    - **lender_id**: 빌려주는 사람 (친구) ID
    - **image_url**: 업로드된 이미지 URL (`POST /upload/image`에서 받은 URL)
    - **description**: 옷 설명 (선택)
    """
    # 친구 관계 확인
    friendship = friendship_service.check_existing_friendship(
        db, current_user.id, item_data.lender_id
    )
    
    if not friendship or friendship.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="친구 관계가 아니거나 친구 요청이 수락되지 않았습니다"
        )
    
    # 자기 자신한테 빌리는 거 방지
    if current_user.id == item_data.lender_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신한테는 빌릴 수 없습니다"
        )
    
    # 옷 대출 등록
    cloth_item = item_service.create_cloth_item(
        db=db,
        borrower_id=current_user.id,
        lender_id=item_data.lender_id,
        image_url=item_data.image_url,
        description=item_data.description
    )
    
    return cloth_item


@router.get("/borrowed", response_model=List[ClothItemWithUser])
def get_borrowed_items(
    friend_id: Optional[int] = Query(None, description="특정 친구한테 빌린 옷만 필터링"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내가 빌린 옷 목록을 조회합니다.
    
    **인증 필요**
    
    - **friend_id** (선택): 특정 친구한테 빌린 옷만 필터링
    """
    items = item_service.get_borrowed_items(db, current_user.id, friend_id)
    return items


@router.get("/lent", response_model=List[ClothItemWithUser])
def get_lent_items(
    friend_id: Optional[int] = Query(None, description="특정 친구한테 빌려준 옷만 필터링"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내가 빌려준 옷 목록을 조회합니다.
    
    **인증 필요**
    
    - **friend_id** (선택): 특정 친구한테 빌려준 옷만 필터링
    """
    items = item_service.get_lent_items(db, current_user.id, friend_id)
    return items


@router.post("/{item_id}/request-return", response_model=ClothItemResponse)
def request_return(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    반납 신청을 합니다.
    
    **인증 필요**
    
    - **item_id**: 반납할 옷 ID
    - 빌린 사람(borrower)만 반납 신청 가능
    """
    item = item_service.request_return(db, item_id, current_user.id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="옷을 찾을 수 없거나 반납 신청할 수 없습니다"
        )
    
    return item


@router.post("/{item_id}/approve-return", response_model=ClothItemResponse)
def approve_return(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    반납을 승인합니다.
    
    **인증 필요**
    
    - **item_id**: 반납 승인할 옷 ID
    - 빌려준 사람(lender)만 반납 승인 가능
    """
    item = item_service.approve_return(db, item_id, current_user.id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="옷을 찾을 수 없거나 반납 승인할 수 없습니다"
        )
    
    return item


@router.post("/{item_id}/reject-return", response_model=ClothItemResponse)
def reject_return(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    반납을 거절합니다 (다시 borrowed 상태로).
    
    **인증 필요**
    
    - **item_id**: 반납 거절할 옷 ID
    - 빌려준 사람(lender)만 반납 거절 가능
    """
    item = item_service.reject_return(db, item_id, current_user.id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="옷을 찾을 수 없거나 반납 거절할 수 없습니다"
        )
    
    return item


@router.get("/{item_id}", response_model=ClothItemResponse)
def get_cloth_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 옷의 상세 정보를 조회합니다.
    
    **인증 필요**
    
    - **item_id**: 조회할 옷 ID
    """
    item = item_service.get_cloth_item_by_id(db, item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="옷을 찾을 수 없습니다"
        )
    
    # 빌린 사람 또는 빌려준 사람만 조회 가능
    if item.borrower_id != current_user.id and item.lender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 옷의 정보를 조회할 권한이 없습니다"
        )
    
    return item

@router.post("/{item_id}/nudge", status_code=status.HTTP_200_OK)
def nudge_borrower(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    반납 독촉(조르기) 알림을 보냅니다.
    
    **인증 필요**
    
    - **item_id**: 독촉할 옷 ID
    - 빌려준 사람(lender)만 가능
    """
    item = item_service.get_cloth_item_by_id(db, item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="옷을 찾을 수 없습니다"
        )
    
    if item.lender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
        
    if item.status != "borrowed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="반납 대기 중이거나 이미 반납된 옷입니다"
        )

    # 알림 생성
    from app.schemas.notification import NotificationCreate
    from app.services.notification import notification_service
    from app.models.notification import Notification
    from datetime import datetime, timedelta
    
    # 1. 쿨타임 체크 (30분)
    last_nudge = db.query(Notification).filter(
        Notification.related_item_id == item.id,
        Notification.type == "nudge"
    ).order_by(Notification.created_at.desc()).first()
    
    if last_nudge:
        time_diff = datetime.utcnow() - last_nudge.created_at
        if time_diff < timedelta(minutes=30):
            remaining_minutes = 30 - int(time_diff.total_seconds() / 60)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"조르기는 30분에 한 번만 가능합니다. ({remaining_minutes}분 남음)"
            )

    # 2. 하루 횟수 제한 (3회)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_nudge_count = db.query(Notification).filter(
        Notification.related_item_id == item.id,
        Notification.type == "nudge",
        Notification.created_at >= today_start
    ).count()
    
    if today_nudge_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="조르기는 하루에 3번까지만 가능합니다."
        )
    
    notification_service.create_notification(
        db,
        NotificationCreate(
            user_id=item.borrower_id,
            type="nudge",
            message=f"{current_user.name}님이 '{item.description or '옷'}' 반납을 요청했습니다! 🥺",
            related_item_id=item.id
        )
    )
    
    return {"message": "조르기 알림을 보냈습니다"}
