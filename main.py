import re
from typing import Annotated
from fastapi import FastAPI, HTTPException, Form, UploadFile, File, Body
from pydantic import EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

app = FastAPI()
#----- 데모용 DB (현재는 임시 리스트) ----------------------------
demo_db = []
#----- 닉네임 생성  -----------------------------------------
nickname_pattern = "^[a-zA-Z0-9가-힣].{5,10}$"
def validate_nickname(nickname: str):
    if not re.match(nickname_pattern, nickname):
        raise HTTPException(
            status_code=422,
            detail="닉네임은 5~10자 길이를 준수해야하며, 숫자, 영문 소문자, 영문 대문자, 한글을 사용할 수 있습니다. 중복 허용 불가입니다."
        )
#----- user_id 부여 (추후 DB 확장성 고려, 함수 형태로 구현)-------
user_counter = 0
def generate_user_id():
    global user_counter
    user_counter += 1
    return f"user_{user_counter}"
#----- 이미지 파일 용량 확인 ----------------------------------
ALLOWED_TYPES = {"image/jpg", "image/png", "image/tiff", "image/bmp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
async def validate_image_size(upload_file):
    size = 0
    chunk_size = 1024 * 1024  # 1MB
    while True:
        chunk = await upload_file.read(chunk_size)
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="이미지 파일은 10MB를 넘을 수 없습니다. "
            )
    await upload_file.seek(0)
#----- 비밀번호 규칙 -------------------------------------------
password_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+=-]).{5,20}$"
def validate_password(password: str):
    if not re.match(password_pattern, password):
        raise HTTPException(
            status_code=422,
            detail="비밀번호는 5~20자 길이를 준수해야하며, 숫자, 영문 소문자, 영문 대문자, 특수 문자가 각각 최소 1개씩 포함되어야 합니다."
        )
#----- 비밀 번호 해싱 from JEFF --------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# 1. 비밀번호 해싱
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
# 2. 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
#----- 로그인 횟수 검증 -----------------------------------------
login_attempts = {}
MAX_ATTEMPTS = 5 # 5회 이상 시도 시 429 에러 반환
#----- 액세스 토큰 생성(로그인 메서드) ----------------------------
load_dotenv() # 환경변수 파일 불러옴
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

# ----- 첫번째. 회원 가입 메서드 시작
@app.post("/users")
async def post_users(
        email_address: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
        nickname: Annotated[str, Form()],
        profile_image: Annotated[UploadFile | None, File()] = None
):
    # 이메일 중복 확인
    if any(user["email_address"] == email_address for user in demo_db):
        raise HTTPException(status_code=409, detail="해당 이메일은 이미 등록되어 있습니다.")
    # 비밀번호 규칙
    validate_password(password)
    # 비밀번호 해싱
    hashed_password = hash_password(password)
    # 닉네임 규칙
    validate_nickname(nickname)
    # 닉네임 중복 확인
    if any(user["nickname"] == nickname for user in demo_db):
        raise HTTPException(status_code=409, detail="해당 닉네임은 이미 등록되어 있습니다.")
    # 코드 리뷰 반영 --> 프로필 이미지 처리 로직 추가
    profile_image_url = None
    # 이미지 파일 확장자 검증
    if profile_image:
        if profile_image.content_type not in ALLOWED_TYPES:
            raise HTTPException(415, "지원하지 않는 이미지 파일 형식입니다. ")
        #TODO : 파일 저장 및 이미지 크기 확인 로직
        await validate_image_size(profile_image)
        profile_image_url = f"/uploads/{profile_image.filename}"
    # user_id 부여
    user_id = generate_user_id()
    # DB에 저장 -- 지금은 리스트에 임시로...
    demo_db.append({
        "user_id": user_id,
        "email_address": email_address,
        "hashed_password": hashed_password,
        "nickname": nickname,
        "profile_image_url": profile_image_url
    })
    return {
        "status" : "success",
        "message" : "회원가입이 정상적으로 처리되었습니다.",
        "user_id" : user_id,
        "email_address" : email_address,
        "nickname" : nickname,
        "profile_image_url" : profile_image if profile_image else None,
        "users_created_time" : datetime.now().strftime('%Y.%m.%d - %H:%M:%S')
    }


# ----- 두번째. 로그인 메서드 시작
@app.post("/auth/token")
async def post_auth_token(
        email_address: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
):
    # 1. 이메일 가입 여부 확인
    is_users_email = None
    for i in demo_db:
        if i["email_address"] == email_address:
            is_users_email = i
            break
    print(is_users_email)
    if is_users_email is None:
        raise HTTPException(status_code=401, detail="일치하는 아이디(이메일) 정보가 없습니다.")
    # 2. 이메일은 확인되었고, 로그인 횟수 검증
    attempts = login_attempts.get(email_address, 0)
    if attempts >= MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="5회 이상 로그인에 실패하였습니다. 너무 많이 시도하였습니다.")
    # 3. 아직 횟수 남았으면, 비밀번호 해시값 검증. 틀리면 횟수 1회 증가
    if not verify_password(password, is_users_email["hashed_password"]):
        login_attempts[email_address] = attempts + 1
        raise HTTPException(status_code=401, detail="비밀번호가 맞지 않습니다. 다시 확인해 주세요.")
    # 4. 비밀번호 해시값 검증 성공 시 초기화
    login_attempts[email_address] = 0
    # 5. 비밀번호 해시값 검증 완료, 액세스 토큰 & 리프레시 토큰 생성
    access_token = create_access_token(
        data={"sub":is_users_email["user_id"]},
        expires_delta=timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    )
    refresh_token = create_access_token(
        data={"sub":is_users_email["user_id"], "type" : "refresh"},
        expires_delta=timedelta(days=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')))
    )
    return {
        "status": "success",
        "message": "로그인에 성공하였습니다.",
        "user_id": is_users_email["user_id"],
        "login_time": datetime.now().strftime('%Y.%m.%d - %H:%M:%S'),
        "token_type": "bearer",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))*60,
        "issued_at": datetime.now().strftime('%Y.%m.%d - %H:%M:%S')
    }


