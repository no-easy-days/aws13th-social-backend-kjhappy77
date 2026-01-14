from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import comments
from routers.users import router as users_router
from routers.posts import router as posts_router
from routers.likes import router as likes_router

load_dotenv()

app = FastAPI(
    title="클라우드 커뮤니티 API",
    description="클라우드 커뮤니티 서비스의 백엔드 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users_router)
app.include_router(posts_router)

app.include_router(comments.router)
app.include_router(comments.my_comments_router)
app.include_router(likes_router)



@app.get("/")
def read_root():
    return {"message": "클라우드 커뮤니티 API 서버가 실행 중입니다!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)