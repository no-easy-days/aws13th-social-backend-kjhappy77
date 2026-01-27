from datetime import datetime, timedelta, timezone
import pymysql.connections
from database import get_db_connection
from pydantic import EmailStr
from typing import Annotated
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends

# 리팩토링한 utils 모듈 불러오기
from database import generate_user_id, find_user_by_id, find_user_by_email, load_users, save_users
from utils.auth import hash_password, verify_password, create_access_token, get_current_user, REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_EXPIRE_MINUTES
from utils.data_validator import validate_nickname, validate_password, validate_and_process_image
from utils.id_generator import generate_new_id

# API Router 선언
router = APIRouter()

# 1. 회원 가입 메서드 시작
@router.post("/users")
async def post_users(
        email_address: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
        nickname: Annotated[str, Form()],
        profile_image: Annotated[UploadFile | None, File()] = None,
        conn: pymysql.connections.Connection = Depends(get_db_connection)

):
    # DB 연동 방식으로 변경.
    cursor = conn.cursor()
    # json 파일에서 users 딕셔너리 불러오기
    #users_json_path = load_users() - 미사용
    # 이메일 중복 확인
    try:
        # 이메일, 닉네임 중복확인 (DB 사용)
        cursor.execute("SELECT user_id FROM users WHERE email_address = %s", (email_address,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="해당 이메일은 이미 등록되어 있습니다.")
        cursor.execute("SELECT user_id FROM users WHERE nickname = %s", (nickname,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="해당 닉네임은 이미 등록되어 있습니다.")
#    if any(user["email_address"] == email_address for user in users_json_path):
#        raise HTTPException(status_code=409, detail="해당 이메일은 이미 등록되어 있습니다.")
        # 비밀번호 정규식 패턴 검증
        validate_password(password)
        # 비밀번호 해싱
#    hashed_password = hash_password(password)
    # 닉네임 정규식 패턴 검증
        validate_nickname(nickname)
    # 닉네임 중복 확인
#    if any(user["nickname"] == nickname for user in users_json_path):
#        raise HTTPException(status_code=409, detail="해당 닉네임은 이미 등록되어 있습니다.")
        # 프로필 이미지 검증
        profile_image_url = None
        if profile_image:
            profile_image_url = await validate_and_process_image(profile_image)
        # user_id 부여
        user_id = generate_user_id(cursor, "users", "user_id", "user")
        hashed_password = hash_password(password)
        sql = """
            INSERT INTO users (user_id, email_address, hashed_password, nickname, profile_image_url)
            VALUES (%s, %s, %s, %s, %s) \
        """
        cursor.execute(sql, (user_id, email_address, hashed_password, nickname, profile_image_url))
        conn.commit()
#    user_id = generate_user_id()
    # ----- 코드 리뷰 반영, 게시물 생성 시간 통일
#    users_created_time = datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S')
    # 등록할 유저 정보 딕셔너리 객체 생성 및 JSON 파일에 저장
#    new_user = {
#        "user_id": user_id,
#        "email_address": email_address,
#        "hashed_password": hashed_password,
#        "nickname": nickname,
#        "profile_image_url": profile_image_url,
#        "users_created_time": users_created_time,
#        "users_modified_time": None
#    }
#    users_json_path.append(new_user)
#    save_users(users_json_path)

        return {
            "status": "success",
            "message": "회원가입이 정상적으로 처리되었습니다.",
            "data": {
                "user_id": user_id,
                "email_address": email_address,
                "nickname": nickname,
                "profile_image_url": profile_image_url,
            }
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

# 2. 로그인 (토큰 발급) 메서드 시작
max_attempts = 5
login_attempts = {}
login_block_ttl = timedelta(minutes=1)
@router.post("/auth/token")
async def post_auth_token(
        email_address: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
):
    # 이메일 사전 등록 여부 확인 --- 코드 리뷰 반영하여 for문에서 함수 형태로 변경
    user = find_user_by_email(str(email_address))
    if user is None:
        raise HTTPException(status_code=401, detail="일치하는 아이디(이메일) 정보가 없습니다.")
    # 해당 계정 로그인 시도 횟수 추출. 시도한 적 없을 경우 None 반환
    attempts = login_attempts.get(email_address)
    if attempts is not None:
        elapsed_time = datetime.now(timezone.utc) - attempts["last_attempt"]
        #print(f"경과시간 : {elapsed_time}")
        if elapsed_time > login_block_ttl:
            del login_attempts[email_address]
            attempts = None
    # 로그인 횟수 5회 초과 여부 확인
    if attempts and attempts["login_count"] >= max_attempts:
        raise HTTPException(status_code=429, detail="로그인 시도 횟수(5회) 초과했습니다. 1분 후 다시 시도하세요.")
    # 비밀번호 해시값 비교 검증, 틀렸을 때
    if not verify_password(password, user["hashed_password"]):
        # 처음 로그인 시도했을 경우
        if not attempts:
            login_attempts[email_address] = {
                "login_count": 1,
                "last_attempt": datetime.now(timezone.utc)
            }
        # 이미 시도한 적 있는 경우
        else:
            attempts["login_count"] += 1
            # 시도 횟수 5회 초과
            if attempts["login_count"] == max_attempts:
                attempts["last_attempt"] = datetime.now(timezone.utc)
        raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다.")
    # 5회 안에 로그인 성공, 로그인 시도 횟수 초기화
    if email_address in login_attempts:
        del login_attempts[email_address]

    access_token = create_access_token(
        data={"sub": user["user_id"], "type": "access"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_access_token(
        data={"sub": user["user_id"], "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return {
        "status": "success",
        "message": "로그인에 성공하였습니다.",
        "data": {
            "user_id": user["user_id"],
            "login_time": datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S'),
            "token_type": "bearer",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "issued_at": datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S')
        }
    }

# 3. 내 프로필 조회 메서드 시작
@router.get("/users/my-page")
async def get_users_my_page(
        user: dict = Depends(get_current_user)
):
    return {
        "status": "success",
        "message": "액세스 토큰 및 사용자 인증이 완료되었습니다.",
        "data": {
                    "user_id": user["user_id"],
        #            "email_address": user["email_address"], -----------민감 개인정보 필터링(코드 리뷰)
                    "nickname": user["nickname"],
                    "profile_image_url": user["profile_image_url"],
                    "users_created_time": user["users_created_time"],
                    "users_modified_time": user["users_modified_time"]
        }
    }

# 4. 내 프로필 수정 메서드 시작
@router.patch("/users/my-page")
async def patch_users_my_page(
        nickname: Annotated[str | None, Form()] = None,
        password: Annotated[str | None, Form()] = None,
        profile_image: Annotated[UploadFile | None, File()] = None,
        target_user: dict = Depends(get_current_user)
):
    users_json_path = load_users()
    # 3가지 중 최소 1개 요청 여부 확인
    if not any([nickname, password, profile_image]):
        raise HTTPException(status_code=400, detail="수정할 정보를 입력해주세요.")
    # 닉네임 변경 요청된 경우
    if nickname:
        # 닉네임 정규식 패턴 검증
        validate_nickname(nickname)
        # 본인 닉네임 제외하고 중복 검사
        if any(i["nickname"] == nickname and i["user_id"] != target_user["user_id"] for i in users_json_path):
            raise HTTPException(status_code=409, detail="해당 닉네임은 이미 존재합니다.")
        # 중복 되는 닉네임 없음 확인, 닉네임 수정 --- 코드 리뷰 반영
        for i, u in enumerate(users_json_path):
            if u["user_id"] == target_user["user_id"]:
                users_json_path[i]["nickname"] = nickname
                save_users(users_json_path)
                break
    # 비밀번호 변경 요청된 경우 (회원 가입과 동일)
    if password:
        validate_password(password)
        target_user["hashed_password"] = hash_password(password)
        save_users(users_json_path)
    # 이미지 변경 요청된 경우 (회원 가입과 동일)
    if profile_image:
        target_user["profile_image_url"] = await validate_and_process_image(profile_image)   # 프로필 수정 시간 DB에 업데이트
        save_users(users_json_path)
    target_user["users_modified_time"] = datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S')
    save_users(users_json_path)
    return {
        "status": "success",
        "message": "프로필 수정이 완료되었습니다.",
        "data": {
            "user_id": target_user["user_id"],
            "email_address" : target_user["email_address"],
            "nickname": target_user["nickname"],
            "profile_image_url": target_user["profile_image_url"],
            "users_created_time": target_user["users_created_time"],
            "users_modified_time": target_user["users_modified_time"]
        }
    }

# 5. 내 프로필 삭제 메서드 구현
@router.delete("/users/my-page")
async def delete_users_my_page(
        password: Annotated[str, Form()],
        target_user: dict = Depends(get_current_user)
):
    users_json_path = load_users()
    # ----- 코드 리뷰 반영, 비밀번호 재검증 로직 추가
    if not verify_password(password, target_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="패스워드가 일치하지 않습니다. ")
    # ----- 코드 리뷰 반영, user_id 기준으로 찾는 로직 추가
    for i, u in enumerate(users_json_path):
        if u["user_id"] == target_user["user_id"]:
            users_json_path.pop(i)
            break
    save_users(users_json_path)
    return {
        "status": "success",
        "message": "유저가 탈퇴처리 되었습니다.",
        "data": {
            "user_id" : target_user["user_id"]
        }
    }

# 6. 다른 사용자 프로필 조회 메서드 구현
@router.get("/users/{user_id}")
async def get_users_user_id(
        user_id: str
):
    # user_id로 유저 찾기
    target_user = find_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {
        "status": "success",
        "message": "요청한 회원의 프로필 조회에 성공했습니다.",
        "data": {
            "user_id": target_user["user_id"],
            #"email_address": target_user["email_address"], --------- 민감 정보 제외(코드 리뷰)
            "nickname": target_user["nickname"],
            "profile_image_url": target_user["profile_image_url"],
            "users_created_time": target_user["users_created_time"]
        }
    }