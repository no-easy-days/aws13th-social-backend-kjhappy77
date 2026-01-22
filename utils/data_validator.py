import os
import html
import re
from fastapi import HTTPException, UploadFile

#----- 코드리뷰 반영, XSS 방지 -------------------------------------------
def sanitize_text(text: str) -> str:
    return html.escape(text)

#----- 환경 변수 검증 ----------------------------------------------------
def validate_env(name: str, value):
    if value is None:
        raise RuntimeError(f"{name} 환경변수가 설정되지 않았습니다.")
    return value

#----- 정규식, 파일 확장자 패턴 --------------------------------------
nickname_pattern = "^[a-zA-Z0-9가-힣]{6,11}$" # --- 코드 리뷰 반영
password_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*+=-]).{5,20}$"
allowed_image_type = {"image/jpeg", "image/png", "image/tiff", "image/bmp", "image/gif"}
max_file_size = 10 * 1024 * 1024  # 10MB

#----- 닉네임 규칙 -------------------------------------------
def validate_nickname(nickname: str):
    if not re.match(nickname_pattern, nickname):
        raise HTTPException(
            status_code=422,
            detail="닉네임은 5~10자 길이를 준수해야하며, 숫자, 영문, 한글만 사용 가능합니다."
        )

#----- 비밀번호 규칙 -------------------------------------------
def validate_password(password: str):
    if not re.match(password_pattern, password):
        raise HTTPException(
            status_code=422,
            detail="비밀번호는 5~20자, 숫자/영문 대소문자/특수문자를 포함해야 합니다."
        )

#----- 이미지 파일 용량, 형식 검증 (I/O Bound 이기 때문에 async)----------------------------------
async def validate_and_process_image(profile_image: UploadFile) -> str:
    # 이미지 형식 검증
    if profile_image.content_type not in allowed_image_type:
        raise HTTPException(
            status_code=415,
            detail="지원하지 않는 이미지 파일 형식입니다. (jpg, png, tiff, bmp, gif 만 가능)"
        )
    # 파일을 1MB 단위로 읽어서 이미지 용량 검증
    size = 0
    chunk_size = 1024 * 1024  # 1MB 단위
    while True:
        chunk = await profile_image.read(chunk_size)
        if not chunk:
            break
        size += len(chunk)
        if size > max_file_size:
            raise HTTPException(status_code=413, detail="이미지 파일은 10MB를 넘을 수 없습니다.")
    '''
    [중요] 파일 읽기 커서(포인터)를 다시 맨 앞으로 돌려놔야 함
    위에서 용량 체크하느라 파일을 끝까지 다 읽었기 때문에, 
    이걸 안 하면 나중에 파일 저장할 때 0byte 빈 파일이 저장됨.
    '''
    await profile_image.seek(0)
    # 저장 경로 생성. TODO: 추후 실제 저장 로직 추가 위치 추가해야함. 예: await save_file_to_disk(profile_image)
    profile_image_url = f"/uploads/{profile_image.filename}"
    return profile_image_url