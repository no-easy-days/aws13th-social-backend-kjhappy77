from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends, Query

from database import load_comments, save_comments, generate_comment_id, load_users, load_posts
from utils.auth import get_current_user
from utils.data_validator import sanitize_text, validate_and_process_image

router = APIRouter()

# 1. 댓글 작성 메서드 구현
@router.post("/posts/{post_id}/comments")
async def create_comment(
        post_id: str,
        comments: Annotated[str, Form()],
        comments_image: Annotated[UploadFile | None, File()] = None,
        user: dict = Depends(get_current_user)
):
    # 게시글 존재 여부 확인
    posts = load_posts()
    if not any(p["post_id"] == post_id for p in posts):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    # XSS 방지
    safe_comments = sanitize_text(comments)
    # 이미지 처리
    comments_image_url = None
    if comments_image:
        comments_image_url = await validate_and_process_image(comments_image)
    comment_id = generate_comment_id()
    created_time = datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S')
    new_comment = {
        "comment_id": comment_id,
        "post_id": post_id,
        "comments": safe_comments,
        "comments_image_url": comments_image_url,
        "author_id": user["user_id"],
        "comments_created_time": created_time,
        "comments_modified_time": None
    }
    all_comments = load_comments()
    all_comments.append(new_comment)
    save_comments(all_comments)
    return {
        "status": "success",
        "message": "댓글 등록이 정상적으로 완료되었습니다.",
        "data": {
            "comment_id": comment_id,
            "comments": safe_comments,
            "comments_image_url": comments_image_url,
            "post_id": post_id,
            "comment_author": {
                "user_id": user["user_id"],
                "email_address": user["email_address"],
                "nickname": user["nickname"]
            },
            "comments_created_time": created_time
        }
    }

# 2. 댓글 목록 조회 메서드 구현
@router.get("/posts/{post_id}/comments")
async def get_comments(
        post_id: str,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        user: dict | None = Depends(get_current_user)  # 본인 댓글 여부 확인용
):
    # 게시글 존재 확인
    posts = load_posts()
    if not any(p["post_id"] == post_id for p in posts):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    all_comments = load_comments()
    users = load_users()
    # 해당 게시글의 댓글만 필터링
    post_comments = [c for c in all_comments if c["post_id"] == post_id]
    # 최신순 정렬 (기본)
    post_comments.sort(key=lambda x: x["comments_created_time"], reverse=True)
    # 페이지네이션

    total_comments = len(post_comments)
    total_pages = (total_comments + page_size - 1) // page_size
    start = (page - 1) * page_size
    paginated = post_comments[start:start + page_size]

    result_list = []
    for c in paginated:
        author = next((u for u in users if u["user_id"] == c["author_id"]),
                      {"nickname": "Unknown", "email_address": ""})
        is_mine = False
        if user and user["user_id"] == c["author_id"]:
            is_mine = True

        result_list.append({
            "sequence": total_comments - (post_comments.index(c)),  # 전체 중 순서
            "comment_id": c["comment_id"],
            "comments": c["comments"],
            "comments_image_url": c["comments_image_url"],
            "post_id": c["post_id"],
            "comment_author": {
                "user_id": c["author_id"],
                "email_address": author["email_address"],
                "nickname": author["nickname"]
            },
            "comments_created_time": c["comments_created_time"],
            "comments_modified_time": c["comments_modified_time"],
            "is_mine": is_mine
        })
    return {
        "status": "success",
        "message": "댓글 목록을 성공적으로 불러왔습니다.",
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_comments": total_comments,
        "has_next": page < total_pages,
        "data": {
            "comments_list": result_list
        }
    }

# 3. 댓글 수정
@router.patch("/posts/{post_id}/comments/{comment_id}")
async def update_comment(
        post_id: str,
        comment_id: str,
        comments: Annotated[str | None, Form()] = None,
        comments_image: Annotated[UploadFile | None, File()] = None,
        user: dict = Depends(get_current_user)
):
    all_comments = load_comments()
    target_comment = None
    target_idx = -1

    for idx, c in enumerate(all_comments):
        if c["comment_id"] == comment_id:
            target_comment = c
            target_idx = idx
            break

    if not target_comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    if target_comment["post_id"] != post_id:
        raise HTTPException(status_code=404, detail="해당 게시글의 댓글이 아닙니다.")

    if target_comment["author_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="댓글 수정 권한이 없습니다.")

    if comments:
        target_comment["comments"] = sanitize_text(comments)

    if comments_image:
        target_comment["comments_image_url"] = await validate_and_process_image(comments_image)

    target_comment["comments_modified_time"] = datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S')
    all_comments[target_idx] = target_comment
    save_comments(all_comments)

    return {
        "status": "success",
        "message": "댓글 수정이 완료되었습니다.",
        "data": {
            "comment_id": target_comment["comment_id"],
            "comments": target_comment["comments"],
            "comments_image_url": target_comment["comments_image_url"],
            "comments_modified_time": target_comment["comments_modified_time"]
        }
    }

# 4. 댓글 삭제
@router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(
        post_id: str,
        comment_id: str,
        user: dict = Depends(get_current_user)
):
    all_comments = load_comments()
    target_idx = -1

    for idx, c in enumerate(all_comments):
        if c["comment_id"] == comment_id:
            if c["author_id"] != user["user_id"]:
                raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
            target_idx = idx
            break

    if target_idx == -1:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    all_comments.pop(target_idx)
    save_comments(all_comments)

    return HTTPException(status_code=204)