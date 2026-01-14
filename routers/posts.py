from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.post import PostResponse, PostCreate, PostUpdate, PostAllPostResponse
from utils import auth, data

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_new_post(
        post_data: PostCreate,
        current_user: dict = Depends(auth.get_current_user)
):
    post_id = data.get_next_id("posts.json")
    now = datetime.now(timezone.utc).isoformat()
    new_post = {
        "id": post_id,
        "user_id": current_user["id"],
        "author_nickname": current_user["nickname"],
        "title": post_data.title,
        "content": post_data.content,
        "view_count": 0,
        "like_count": 0,
        "comment_count": 0,
        "created_at": now,
        "updated_at": now
    }

    posts = data.load_data("posts.json")
    posts.append(new_post)
    success = data.save_data(posts, "posts.json")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 데이터 저장 실패"
        )

    return PostResponse(
        id=new_post["id"],
        user_id=new_post["user_id"],
        author_nickname=new_post["author_nickname"],
        title=new_post["title"],
        content=new_post["content"],
        view_count=new_post["view_count"],
        like_count=new_post["like_count"],
        comment_count=new_post["comment_count"],
        created_at=new_post["created_at"],
        updated_at=new_post["updated_at"]
    )

@router.get("/", response_model=list[PostAllPostResponse], status_code=status.HTTP_200_OK)
async def get_all_posts(sort: Optional[str] = "latest"):
    posts = data.load_data("posts.json")

    if sort == "views":
        posts.sort(key=lambda x: x.get("view_count", 0), reverse=True)
    elif sort == "likes":
        posts.sort(key=lambda x: x.get("like_count", 0), reverse=True)
    elif sort == "comments":
        posts.sort(key=lambda x: x.get("comment_count", 0), reverse=True)
    else:
        posts.sort(key=lambda x: x.get("id", 0), reverse=True)

    return [
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
        for post in posts
    ]


@router.get("/search", response_model=list[PostAllPostResponse], status_code=status.HTTP_200_OK)
async def search_posts(q: Optional[str] = None, sort: Optional[str] = "latest"):
    if not q or len(q.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="검색어를 입력해주세요"
        )

    keyword = q.strip().lower()
    posts = data.load_data("posts.json")

    matched_posts = [
        post for post in posts
        if keyword in post.get("title", "").lower()
        or keyword in post.get("content", "").lower()
    ]

    if sort == "views":
        matched_posts.sort(key=lambda x: x.get("view_count", 0), reverse=True)
    elif sort == "likes":
        matched_posts.sort(key=lambda x: x.get("like_count", 0), reverse=True)
    elif sort == "comments":
        matched_posts.sort(key=lambda x: x.get("comment_count", 0), reverse=True)
    else:
        matched_posts.sort(key=lambda x: x.get("id", 0), reverse=True)

    return [
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
        for post in matched_posts
    ]


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_detail_post(post_id: int):

    detailed_post = data.find_by_id("posts.json", post_id)

    if not detailed_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없음"
        )

    new_view_count = detailed_post.get("view_count", 0) + 1
    data.update_by_id("posts.json", post_id, {"view_count": new_view_count})
    detailed_post["view_count"] = new_view_count

    return PostResponse(
        id=detailed_post["id"],
        user_id=detailed_post["user_id"],
        author_nickname=detailed_post.get("author_nickname", "탈퇴한 사용자"),
        title=detailed_post["title"],
        content=detailed_post["content"],
        view_count=detailed_post["view_count"],
        like_count=detailed_post.get("like_count", 0),
        comment_count=detailed_post.get("comment_count", 0),
        created_at=detailed_post["created_at"],
        updated_at=detailed_post["updated_at"]
    )

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int,
        current_user: dict = Depends(auth.get_current_user)
):
    post = data.find_by_id("posts.json", post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없음"
        )

    if post["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 삭제할 수 있습니다"
        )

    comments = data.load_data("comments.json")
    comments = [c for c in comments if c.get("post_id") != post_id]
    data.save_data(comments, "comments.json")

    likes = data.load_data("likes.json")
    likes = [l for l in likes if l.get("post_id") != post_id]
    data.save_data(likes, "likes.json")

    data.delete_by_id("posts.json", post_id)


@router.patch("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def update_post(
        post_id: int,
        post_data: PostUpdate,
        current_user: dict = Depends(auth.get_current_user)
):
    post = data.find_by_id("posts.json", post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없음"
        )

    if post["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="작성자만 수정할 수 있습니다"
        )

    update_fields = {}
    if post_data.title is not None:
        update_fields["title"] = post_data.title
    if post_data.content is not None:
        update_fields["content"] = post_data.content

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 내용이 없습니다"
        )

    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    data.update_by_id("posts.json", post_id, update_fields)

    updated_post = data.find_by_id("posts.json", post_id)
    return PostResponse(
        id=updated_post["id"],
        user_id=updated_post["user_id"],
        author_nickname=updated_post.get("author_nickname", "탈퇴한 사용자"),
        title=updated_post["title"],
        content=updated_post["content"],
        view_count=updated_post.get("view_count", 0),
        like_count=updated_post.get("like_count", 0),
        comment_count=updated_post.get("comment_count", 0),
        created_at=updated_post["created_at"],
        updated_at=updated_post["updated_at"]
    )