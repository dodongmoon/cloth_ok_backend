from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.base import engine, Base
from app.models import User, Friendship, ClothItem, Notification

# API 라우터 import
from app.api import auth, users, friends, items, upload

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # Trigger redeploy
    description="옷 대출/반납 관리 API",
    version="1.0.0"
)

# 디버깅용: 모든 서버 에러를 자세히 보여줌
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc()
        },
    )

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["인증 (Auth)"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["사용자 (Users)"])
app.include_router(friends.router, prefix=f"{settings.API_V1_STR}/friends", tags=["친구 (Friends)"])
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["업로드 (Upload)"])
app.include_router(items.router, prefix=f"{settings.API_V1_STR}/items", tags=["옷 대출 (Items)"])

# 정적 파일 서빙 (업로드된 이미지)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "ClothShare API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.on_event("startup")
async def startup_event():
    print("Backend started! Version 1.0.1 - Refresh Token Fix Applied")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}





# 나중에 추가할 라우터들
from app.api import notifications
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["알림 (Notifications)"])

