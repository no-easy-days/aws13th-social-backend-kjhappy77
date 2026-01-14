"""
FastAPI Community - 메인
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import get_settings

settings = get_settings()

# FastAPI 인스턴스 초기화 
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="클라우드 커뮤니티 REST API",
    version="1.0.0",
    docs_url="/docs",
)

# 전역 예외 핸들러 - 사용자가 데이터를 잘못 보냈을 때
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "message": "Validation error",
            "detail": "; ".join(error_messages)
        }
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI Community API",
        "version": "1.0.0",
        "docs": "/docs"
    }
