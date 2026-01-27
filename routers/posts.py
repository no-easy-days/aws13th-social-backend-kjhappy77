from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends

from database import generate_post_id, load_posts, save_posts
from utils.auth import hash_password, verify_password, create_access_token, get_current_user, REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_EXPIRE_MINUTES
from utils.data_validator import validate_and_process_image, sanitize_text

router = APIRouter()

# 1. 게시글 작성 메서드 시작
@router.post("/posts")
async def post_posts(
        title : Annotated[str, Form()],
        contents : Annotated[str, Form()],
        contents_image : Annotated[UploadFile | None, File()] = None,
        user: dict = Depends(get_current_user)
):
    # 코드 리뷰 반영 ------------- XSS 방지
    safe_title = sanitize_text(title)
    safe_contents = sanitize_text(contents)
    posts_json_path = load_posts()
    # 게시물에 첨부할 이미지 검증
    contents_image_url = None
    if contents_image:
        contents_image_url = await validate_and_process_image(contents_image)
    # post_id 부여
    post_id = generate_post_id()
    # ----- 코드 리뷰 반영, 게시물 생성 시간 통일
    posts_created_time = datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S')
    new_post = {
        "post_id": post_id,
        "title": safe_title,
        "contents": safe_contents,
        "contents_image_url": contents_image_url,
        "author_id": user["user_id"],  # ----- 코드리뷰 반영, 추후 작성자 정보 반환 필요함
        "posts_created_time": posts_created_time,
        "posts_modified_time": None
    }
    posts_json_path.append(new_post)
    save_posts(posts_json_path)
    return {
        "status" : "success",
        "message" : "게시글 작성이 완료되었습니다.",
        "data" : {
            "post_id": post_id,
            "title" : safe_title,
            "contents" : safe_contents,
            "contents_image_url": contents_image_url,
            "author" : {
                "user_id" : user["user_id"],
                #"email_address" : user["email_address"], --- 민감 정보 제외, 코드리뷰 반영
                "nickname" : user["nickname"]
            },
            "posts_created_time": posts_created_time,
        }
    }

# 2. 게시글 수정 메서드 시작
@router.patch("/posts/{post_id}")
async def patch_posts(
        post_id: str,
        title: Annotated[str | None, Form()] = None,
        contents : Annotated[str | None, Form()] = None,
        contents_image : Annotated[UploadFile | None, File()] = None
):
    posts_json_path = load_posts()
    # 3가지 중 최소 1개 요청 여부 확인
    if not any([title, contents, contents_image]):
        raise HTTPException(status_code=400, detail="수정할 정보를 입력해주세요.")
    # 대상 게시물 post_id값 바탕으로 찾기
    target_post = None
    for post in posts_json_path:
        if post["post_id"] == post_id:
            target_post = post
            break
    if not target_post:
        raise HTTPException(status_code=404, detail="대상 게시물을 찾을 수 없습니다.")
    # 제목(title) 변경 요청된 경우, 길이 제한
    if title is not None:
        if len(title) > 100:
            raise HTTPException(status_code=400, detail="제목이 너무 깁니다.")
        target_post["title"] = title
    # 내용(contents) 변경 요청된 경우, 길이 제한
    if contents is not None:
        if len(contents) > 5000:
            raise HTTPException(status_code=400, detail="게시글 본문이 너무 깁니다.")
    # 이미지 변경 요청된 경우
    if contents_image:
        contents_image_url = await validate_and_process_image(contents_image)
        with open(contents_image_url, "wb") as f:
            f.write(await contents_image.read())
            target_post["contents_image"] = contents_image_url
    # 게시물에 첨부할 이미지 검증
    target_post["posts_modified_time"] = datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S')
    save_posts(posts_json_path)
    return {
        "status" : "success",
        "message" : "게시글 수정이 완료되었습니다.",
        "data" : {
            "post_id": target_post["post_id"],
            "title" : target_post["title"],
            "contents" : target_post["contents"],
            "contents_image_url": target_post["contents_image_url"]
        },
        "posts_created_time": target_post["posts_created_time"],
        "posts_modified_time" : target_post["posts_modified_time"]
    }