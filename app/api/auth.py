from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.user import UserCreate
from app.schemas.user import UserResponse
from app.services import user as user_service
from app.services.auth import verify_password, create_access_token, create_refresh_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    새로운 사용자를 등록합니다.
    
    - **email**: 사용자 이메일 (unique)
    - **name**: 사용자 이름
    - **password**: 비밀번호 (최소 6자)
    """
    # 이메일 중복 체크
    existing_user = user_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    # 사용자 생성
    # 사용자 생성
    user_create = UserCreate(
        email=user_data.email,
        name=user_data.name,
        password=user_data.password
    )
    user = user_service.create_user(db=db, user=user_create)
    
    return user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    로그인하여 JWT 토큰을 발급받습니다.
    
    - **email**: 사용자 이메일
    - **password**: 비밀번호
    
    Returns:
        - **access_token**: 1시간 유효한 액세스 토큰
        - **refresh_token**: 7일 유효한 리프레시 토큰
    """
    # 사용자 확인
    user = user_service.get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 비밀번호 검증
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 생성
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(token: str, db: Session = Depends(get_db)):
    """
    Refresh Token으로 새로운 Access Token을 발급받습니다.
    
    - **token**: Refresh Token
    """
    from app.services.auth import verify_token
    
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 확인
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # 새로운 토큰 발급
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

