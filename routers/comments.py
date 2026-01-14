from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, status

from schemas.comment import CommentResponse, CommentCreate, CommentUpdate
from utils import data, auth

router = APIRouter(
    prefix="/posts/{post_id}/comments",
    tags=["comments"]
)

my_comments_router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        post_id: int,
        comment: CommentCreate,
        current_user: dict = Depends(auth.get_current_user)
):
    comment_post = data.find_by_id("posts.json", post_id)
    if not comment_post:
        raise HTTPException(status_code=404, detail="해당 게시물 존재하지 않음")

    comment_id = data.get_next_id("comments.json")
    now = datetime.now(timezone.utc).isoformat()
    new_comment = {
        "id": comment_id,
        "post_id": post_id,
        "user_id": current_user["id"],
        "author_nickname": current_user["nickname"],
        "content": comment.content,
        "created_at": now,
        "updated_at": now
    }

    comments = data.load_data("comments.json")
    comments.append(new_comment)
    success = data.save_data(comments, "comments.json")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 데이터 저장 실패"
        )
    return CommentResponse(
        id=comment_id,
        post_id=post_id,
        user_id=current_user["id"],
        author_nickname=current_user["nickname"],
        content=comment.content,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@router.get("/", response_model=list[CommentResponse], status_code=status.HTTP_200_OK)
async def get_comments_by_post(post_id: int):
    post = data.find_by_id("posts.json", post_id)
    if not post:
        raise HTTPException(status_code=404, detail="해당 게시물 존재하지 않음")

    comments = data.load_data("comments.json")
    post_comments = [c for c in comments if c.get("post_id") == post_id]

    return [
        CommentResponse(
            id=c["id"],
            post_id=c["post_id"],
            user_id=c["user_id"],
            author_nickname=c["author_nickname"],
            content=c["content"],
            created_at=c["created_at"],
            updated_at=c["updated_at"]
        )
        for c in post_comments
    ]

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        post_id: int,
        comment_id: int,
        current_user: dict = Depends(auth.get_current_user)
):
    comment = data.find_by_id("comments.json", comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글 없음"
        )
    if comment["post_id"] != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 게시글의 댓글이 아님"
        )
    if comment["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글 작성자만 삭제 가능"
        )

    data.delete_by_id("comments.json", comment_id)


@router.patch("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def update_comment(
        post_id: int,
        comment_id: int,
        comment_data: CommentUpdate,
        current_user: dict = Depends(auth.get_current_user)
):
    comment = data.find_by_id("comments.json", comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글 없음"
        )
    if comment["post_id"] != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 게시글의 댓글이 아님"
        )
    if comment["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글 작성자만 수정 가능"
        )

    update_fields = {
        "content": comment_data.content,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    data.update_by_id("comments.json", comment_id, update_fields)

    updated_comment = data.find_by_id("comments.json", comment_id)
    return CommentResponse(
        id=updated_comment["id"],
        post_id=updated_comment["post_id"],
        user_id=updated_comment["user_id"],
        author_nickname=updated_comment["author_nickname"],
        content=updated_comment["content"],
        created_at=updated_comment["created_at"],
        updated_at=updated_comment["updated_at"]
    )
@my_comments_router.get("/me", response_model=list[CommentResponse], status_code=status.HTTP_200_OK)
async def get_my_comments(current_user: dict = Depends(auth.get_current_user)):
    comments = data.load_data("comments.json")
    my_comments = [c for c in comments if c.get("user_id") == current_user["id"]]

    my_comments.sort(key=lambda x: x.get("id", 0), reverse=True)

    return [
        CommentResponse(
            id=c["id"],
            post_id=c["post_id"],
            user_id=c["user_id"],
            author_nickname=c["author_nickname"],
            content=c["content"],
            created_at=c["created_at"],
            updated_at=c["updated_at"]
        )
        for c in my_comments
    ]
