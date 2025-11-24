from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.schemas.cloth_item import ImageUploadResponse
from app.services import storage
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    이미지 파일을 업로드합니다.
    
    **인증 필요**
    
    - 지원 포맷: JPG, PNG, HEIC
    - 최대 크기: 10MB (FastAPI 기본값)
    """
    # 파일 확장자 검증
    allowed_extensions = [".jpg", ".jpeg", ".png", ".heic", ".heif"]
    file_ext = None
    if file.filename:
        file_ext = "." + file.filename.split(".")[-1].lower()
    
    if not file_ext or file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(allowed_extensions)}"
        )
    
    # 파일 저장
    try:
        filename, file_url = storage.save_upload_file(file)
        return {
            "image_url": file_url,
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}"
        )

