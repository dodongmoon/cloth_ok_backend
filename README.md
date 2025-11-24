# ClothShare Backend API

옷 대출/반납 관리 앱의 백엔드 API 서버입니다.

## 기술 스택

- **Python 3.9+**
- **FastAPI** - 고성능 웹 프레임워크
- **SQLAlchemy** - ORM
- **SQLite** - 개발용 데이터베이스 (나중에 PostgreSQL로 변경 예정)
- **JWT** - 인증/인가
- **Uvicorn** - ASGI 서버

## 설치 및 실행

### 1. 가상환경 활성화
```bash
source venv/bin/activate
```

### 2. 패키지 설치 (이미 완료됨)
```bash
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인
서버 실행 후 브라우저에서:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
backend/
├── app/
│   ├── api/           # API 라우터들 (Phase 2+에서 구현)
│   ├── core/          # 설정 파일
│   ├── db/            # 데이터베이스 설정
│   ├── models/        # SQLAlchemy 모델
│   ├── schemas/       # Pydantic 스키마 (Phase 2+에서 구현)
│   └── services/      # 비즈니스 로직 (Phase 2+에서 구현)
├── main.py            # FastAPI 앱 진입점
├── requirements.txt   # 패키지 목록
└── env.example        # 환경변수 예시
```

## 데이터베이스 모델

### User (사용자)
- id, email, name, hashed_password, profile_image_url
- created_at, updated_at

### Friendship (친구 관계)
- id, user_id_1, user_id_2, status (pending/accepted/rejected)
- created_at

### ClothItem (옷 대출 기록)
- id, borrower_id, lender_id, image_url, description
- status (borrowed/return_requested/returned)
- borrowed_at, return_requested_at, returned_at

### Notification (알림)
- id, user_id, type, related_item_id, message
- is_read, created_at

## 다음 단계 (Phase 2)

- [ ] 회원가입/로그인 API 구현
- [ ] JWT 인증 미들웨어 추가
- [ ] Pydantic 스키마 정의
- [ ] 비밀번호 해싱 유틸리티 추가

