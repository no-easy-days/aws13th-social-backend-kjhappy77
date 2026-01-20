import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

from utils.data_validator import validate_env
from database import find_user_by_id

load_dotenv()

# ----- 설정 및 상수 (환경변수 검증 로직 추가. 코드 리뷰 반영)-----------------------
SECRET_KEY = validate_env("SECRET_KEY", os.getenv("SECRET_KEY"))
ALGORITHM = validate_env("ALGORITHM", os.getenv("ALGORITHM"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

#----- 비밀 번호 해싱 from JEFF --------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# 1. 비밀번호 해싱
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
# 2. 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
# ----- 토큰 생성 함수 ---------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ----- Oauth 2.0 Bearer 선언 & 토큰 디코딩 및 로그인 인증(의존성 주입) ----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None:
            raise HTTPException(status_code=401, detail="토큰 인증 정보가 유효하지 않습니다.")
        if token_type != "access":
            raise HTTPException(status_code=401, detail="유효한 액세스 토큰이 아닙니다.")

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except JWTError:
        raise HTTPException(status_code=401, detail="토큰 인증 정보가 유효하지 않습니다.")

    user = find_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="일치하는 회원 정보가 없습니다.")

    return user