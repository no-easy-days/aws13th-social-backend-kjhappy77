from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Query

from database import load_likes, save_likes, load_posts, load_users
from utils.auth import get_current_user

router = APIRouter()


# 1. 좋아요 상태 확인
@router.get("/posts/{post_id}/likes")
async def get_likes_status(
        post_id: str,
        user: dict | None = Depends(get_current_user)
):
    posts = load_posts()
    if not any(p["post_id"] == post_id for p in posts):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    likes = load_likes()
    post_likes = [l for l in likes if l["post_id"] == post_id]
    likes_count = len(post_likes)

    liked_by_me = False
    if user:
        liked_by_me = any(l["user_id"] == user["user_id"] for l in post_likes)

    return {
        "status": "success",
        "message": "좋아요 정보를 불러왔습니다.",
        "data": {
            "post_id": post_id,
            "likes_count": likes_count,
            "liked_by_me": liked_by_me
        }
    }


# 2. 좋아요 등록
@router.post("/posts/{post_id}/likes")
async def add_like(
        post_id: str,
        user: dict = Depends(get_current_user)
):
    posts = load_posts()
    if not any(p["post_id"] == post_id for p in posts):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    likes = load_likes()
    # 이미 좋아요 눌렀는지 확인
    if any(l["post_id"] == post_id and l["user_id"] == user["user_id"] for l in likes):
        raise HTTPException(status_code=409, detail="이미 좋아요를 눌렀습니다.")

    new_like = {
        "post_id": post_id,
        "user_id": user["user_id"],
        "likes_created_time": datetime.now(timezone.utc).strftime('%Y.%m.%d - %H:%M:%S')
    }

    likes.append(new_like)
    save_likes(likes)

    # 갱신된 카운트
    current_count = len([l for l in likes if l["post_id"] == post_id])

    return {
        "status": "success",
        "message": "좋아요 등록 완료",
        "data": {
            "post_id": post_id,
            "liked_by_me": True,
            "likes_count": current_count,
            "likes_created_time": new_like["likes_created_time"]
        }
    }


# 3. 좋아요 취소
@router.delete("/posts/{post_id}/likes")
async def delete_like(
        post_id: str,
        user: dict = Depends(get_current_user)
):
    posts = load_posts()
    if not any(p["post_id"] == post_id for p in posts):
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    likes = load_likes()
    target_idx = -1

    for idx, l in enumerate(likes):
        if l["post_id"] == post_id and l["user_id"] == user["user_id"]:
            target_idx = idx
            break

    if target_idx == -1:
        raise HTTPException(status_code=404, detail="좋아요 이력이 없습니다.")

    likes.pop(target_idx)
    save_likes(likes)

    # 갱신된 카운트
    current_count = len([l for l in likes if l["post_id"] == post_id])

    return {
        "status": "success",
        "message": "좋아요 취소 완료",
        "data": {
            "post_id": post_id,
            "liked_by_me": False,
            "likes_count": current_count
        }
    }


# 4. 내가 좋아요한 게시글 목록
@router.get("/users/my-page/likes")
async def get_my_liked_posts(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        user: dict = Depends(get_current_user)
):
    likes = load_likes()
    posts = load_posts()

    # 내가 좋아요 한 post_id 추출
    my_liked_post_ids = [l["post_id"] for l in likes if l["user_id"] == user["user_id"]]

    # 해당 post 데이터 찾기 (삭제된 게시글은 제외)
    liked_posts = []
    for p in posts:
        if p["post_id"] in my_liked_post_ids:
            # 좋아요한 시간 정보도 필요하면 likes 리스트에서 매핑해야 함
            like_info = next((l for l in likes if l["post_id"] == p["post_id"] and l["user_id"] == user["user_id"]),
                             None)

            # 전체 좋아요 수 계산
            l_count = len([l for l in likes if l["post_id"] == p["post_id"]])

            liked_posts.append({
                "post_id": p["post_id"],
                "liked_by_me": True,
                "likes_count": l_count,
                "likes_created_time": like_info["likes_created_time"] if like_info else None
            })

    # 최신순 정렬 (좋아요 누른 시간 기준)
    liked_posts.sort(key=lambda x: x["likes_created_time"] or "", reverse=True)

    # 페이징
    total_likes = len(liked_posts)
    total_pages = (total_likes + page_size - 1) // page_size
    start = (page - 1) * page_size
    paginated = liked_posts[start:start + page_size]

    return {
        "status": "success",
        "message": "내가 좋아요한 게시글 목록을 불러왔습니다.",
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_likes": total_likes,
        "has_next": page < total_pages,
        "data": {
            "list": paginated
        }
    }