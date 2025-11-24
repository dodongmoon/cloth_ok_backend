import os
import shutil
import uuid
from fastapi import UploadFile
from pathlib import Path

UPLOAD_DIR = "uploads"

# 업로드 디렉토리 생성
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_upload_file(upload_file: UploadFile) -> tuple[str, str]:
    """
    파일을 저장하고 파일명과 URL을 반환합니다.
    """
    # 고유한 파일명 생성
    file_ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    # URL 생성 (실제 배포 시에는 도메인/S3 URL 등으로 변경 필요)
    # 현재는 정적 파일 서빙 URL 반환
    file_url = f"/uploads/{filename}"
    
    return filename, file_url
