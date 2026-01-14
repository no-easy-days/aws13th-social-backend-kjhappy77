from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.like import LikeCreate, LikeResponse, LikeStatus
from schemas.post import PostAllPostResponse
from utils import auth, data

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("/", response_model=LikeStatus, status_code=status.HTTP_201_CREATED)
async def create_like(
        like_data: LikeCreate,
        current_user: dict = Depends(auth.get_current_user)
):

    post = data.find_by_id("posts.json", like_data.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없음"
        )

    likes = data.load_data("likes.json")
    existing_like = next(
        (like for like in likes
         if like["post_id"] == like_data.post_id and like["user_id"] == current_user["id"]),
        None
    )

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 좋아요를 누른 게시글입니다"
        )

    like_id = data.get_next_id("likes.json")
    now = datetime.now(timezone.utc).isoformat()
    new_like = {
        "id": like_id,
        "post_id": like_data.post_id,
        "user_id": current_user["id"],
        "created_at": now
    }

    likes.append(new_like)
    success = data.save_data(likes, "likes.json")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="좋아요 데이터 저장 실패"
        )

    new_like_count = post.get("like_count", 0) + 1
    count_updated = data.update_by_id("posts.json", like_data.post_id, {"like_count": new_like_count})

    if not count_updated:
        data.delete_by_id("likes.json", like_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="좋아요 카운트 업데이트 실패"
        )

    return LikeStatus(
        is_liked=True,
        total_likes=new_like_count
    )


@router.delete("/{post_id}", response_model=LikeStatus, status_code=status.HTTP_200_OK)
async def delete_like(
        post_id: int,
        current_user: dict = Depends(auth.get_current_user)
):
    post = data.find_by_id("posts.json", post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없음"
        )

    likes = data.load_data("likes.json")
    existing_like = next(
        (like for like in likes
         if like["post_id"] == post_id and like["user_id"] == current_user["id"]),
        None
    )

    if not existing_like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="좋아요를 누르지 않은 게시글입니다"
        )

    deleted = data.delete_by_id("likes.json", existing_like["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="좋아요 삭제 실패"
        )

    new_like_count = max(post.get("like_count", 0) - 1, 0)
    count_updated = data.update_by_id("posts.json", post_id, {"like_count": new_like_count})

    if not count_updated:
        likes = data.load_data("likes.json")
        likes.append(existing_like)
        data.save_data(likes, "likes.json")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="좋아요 카운트 업데이트 실패"
        )

    return LikeStatus(
        is_liked=False,
        total_likes=new_like_count
    )


@router.get("/status/{post_id}", response_model=LikeStatus, status_code=status.HTTP_200_OK)
async def get_like_status(
        post_id: int,
        current_user: dict = Depends(auth.get_current_user)
):
    post = data.find_by_id("posts.json", post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없음"
        )

    likes = data.load_data("likes.json")
    existing_like = next(
        (like for like in likes
         if like["post_id"] == post_id and like["user_id"] == current_user["id"]),
        None
    )

    return LikeStatus(
        is_liked=existing_like is not None,
        total_likes=post.get("like_count", 0)
    )


@router.get("/me", response_model=list[PostAllPostResponse], status_code=status.HTTP_200_OK)
async def get_my_liked_posts(
        current_user: dict = Depends(auth.get_current_user)
):
    likes = data.load_data("likes.json")
    my_likes = [like for like in likes if like["user_id"] == current_user["id"]]

    my_likes.sort(key=lambda x: x.get("id", 0), reverse=True)

    posts = data.load_data("posts.json")
    liked_post_ids = [like["post_id"] for like in my_likes]

    liked_posts = []
    for post_id in liked_post_ids:
        post = next((p for p in posts if p["id"] == post_id), None)
        if post:
            liked_posts.append(
                PostAllPostResponse(
                    id=post["id"],
                    user_id=post["user_id"],
                    author_nickname=post.get("author_nickname", "탈퇴한 사용자"),
                    title=post["title"],
                    view_count=post.get("view_count", 0),
                    like_count=post.get("like_count", 0),
                    comment_count=post.get("comment_count", 0),
                    created_at=post["created_at"],
                    updated_at=post["updated_at"]
                )
            )

    return liked_posts