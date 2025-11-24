from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.services import user as user_service
from app.services.auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import User

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    JWT 토큰으로 현재 로그인한 사용자를 가져옵니다.
    
    Args:
        credentials: HTTP Authorization Header의 Bearer 토큰
        db: 데이터베이스 세션
        
    Returns:
        User 객체
        
    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우
    """
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자의 정보를 조회합니다.
    
    **인증 필요**: Authorization 헤더에 Bearer 토큰 필요
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 로그인한 사용자의 정보를 수정합니다.
    
    **인증 필요**: Authorization 헤더에 Bearer 토큰 필요
    
    - **name**: 새로운 이름 (선택)
    - **profile_image_url**: 새로운 프로필 이미지 URL (선택)
    """
    updated_user = user_service.update_user(
        db=db,
        user_id=current_user.id,
        user_update=user_update
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 사용자의 정보를 조회합니다.
    
    **인증 필요**: Authorization 헤더에 Bearer 토큰 필요
    
    - **user_id**: 조회할 사용자의 ID
    """
    user = user_service.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user

