from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.schemas.friendship import (
    FriendRequestCreate,
    FriendshipResponse,
    FriendInfo,
    FriendRequestItem
)
from app.services import friendship as friendship_service
from app.services import user as user_service
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/request", response_model=FriendshipResponse, status_code=status.HTTP_201_CREATED)
def send_friend_request(
    request_data: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    친구 요청을 보냅니다.
    
    **인증 필요**
    
    - **friend_email**: 친구로 추가할 사용자의 이메일
    """
    # 친구의 이메일로 사용자 찾기
    friend = user_service.get_user_by_email(db, request_data.friend_email)
    if not friend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 이메일의 사용자를 찾을 수 없습니다"
        )
    
    # 자기 자신에게 요청 방지
    if friend.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신에게는 친구 요청을 보낼 수 없습니다"
        )
    
    # 이미 친구 관계가 있는지 확인
    existing = friendship_service.check_existing_friendship(db, current_user.id, friend.id)
    if existing:
        if existing.status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 친구입니다"
            )
        elif existing.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 친구 요청이 있습니다"
            )
    
    # 친구 요청 생성
    friendship = friendship_service.create_friend_request(db, current_user.id, friend.id)
    return friendship


@router.get("", response_model=List[FriendInfo])
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    친구 목록을 조회합니다 (accepted 상태만).
    
    **인증 필요**
    """
    friends = friendship_service.get_friends(db, current_user.id)
    return friends


@router.get("/requests/received", response_model=List[FriendRequestItem])
def get_received_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    받은 친구 요청 목록을 조회합니다 (pending 상태만).
    
    **인증 필요**
    """
    requests = friendship_service.get_received_friend_requests(db, current_user.id)
    return requests


@router.get("/requests/sent", response_model=List[FriendRequestItem])
def get_sent_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    보낸 친구 요청 목록을 조회합니다 (pending 상태만).
    
    **인증 필요**
    """
    # 보낸 요청은 스키마를 약간 다르게 해석 (from -> to)
    requests = friendship_service.get_sent_friend_requests(db, current_user.id)
    
    # to_user를 from_user 필드명으로 매핑 (스키마 재사용)
    return [
        {
            "friendship_id": req["friendship_id"],
            "from_user_id": req["to_user_id"],
            "from_user_email": req["to_user_email"],
            "from_user_name": req["to_user_name"],
            "from_user_profile_image": req["to_user_profile_image"],
            "requested_at": req["requested_at"]
        }
        for req in requests
    ]


@router.post("/{friendship_id}/accept", response_model=FriendshipResponse)
def accept_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    친구 요청을 수락합니다.
    
    **인증 필요**
    
    - **friendship_id**: 수락할 친구 요청의 ID
    """
    friendship = friendship_service.accept_friend_request(db, friendship_id, current_user.id)
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="친구 요청을 찾을 수 없거나 수락할 수 없습니다"
        )
    
    return friendship


@router.post("/{friendship_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    친구 요청을 거절합니다.
    
    **인증 필요**
    
    - **friendship_id**: 거절할 친구 요청의 ID
    """
    success = friendship_service.reject_friend_request(db, friendship_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="친구 요청을 찾을 수 없거나 거절할 수 없습니다"
        )
    
    return None


@router.delete("/{friendship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_friend(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    친구 관계를 삭제합니다.
    
    **인증 필요**
    
    - **friendship_id**: 삭제할 친구 관계의 ID
    """
    success = friendship_service.delete_friendship(db, friendship_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="친구 관계를 찾을 수 없거나 삭제할 수 없습니다"
        )
    
    return None

