from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends

from schemas.user import UserCreate, UserResponse, UserUpdate, UserPublicResponse, Token, UserLogin
from utils import auth, data

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):

    existing_user = data.find_by_field("users.json", "email", user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일"
        )

    hashed_password = auth.hash_password(user_data.password)

    user_id = data.get_next_id("users.json")

    now = datetime.now(timezone.utc).isoformat()
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "nickname": user_data.nickname,
        "profile_image": user_data.profile_image,
        "hashed_password": hashed_password,
        "created_at": now,
        "updated_at": now
    }

    users = data.load_data("users.json")
    users.append(new_user)
    success = data.save_data(users, "users.json")

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 생성에 실패"
        )

    # UserResponse 반환 (hashed_password 제외)
    return UserResponse(
        id=new_user["id"],
        email=new_user["email"],
        nickname=new_user["nickname"],
        profile_image=new_user["profile_image"],
        created_at=new_user["created_at"],
        updated_at=new_user["updated_at"]
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):

    user = data.find_by_field("users.json", "email", credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not auth.verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token_data = {
        "sub": user["email"],
        "user_id": user["id"]
    }
    access_token = auth.create_access_token(token_data)

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(auth.get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        nickname=current_user["nickname"],
        profile_image=current_user.get("profile_image"),
        created_at=current_user["created_at"],
        updated_at=current_user["updated_at"]
    )


@router.patch("/me", response_model=UserResponse)
async def update_profile(
        user_data: UserUpdate,
        current_user: dict = Depends(auth.get_current_user)
):
    update_fields = {}

    if user_data.nickname is not None:
        update_fields["nickname"] = user_data.nickname
    if user_data.profile_image is not None:
        update_fields["profile_image"] = user_data.profile_image
    if user_data.password is not None:
        update_fields["hashed_password"] = auth.hash_password(user_data.password)

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 내용이 없음"
        )

    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    data.update_by_id("users.json", current_user["id"], update_fields)

    updated_user = data.find_by_id("users.json", current_user["id"])
    return UserResponse(
        id=updated_user["id"],
        email=updated_user["email"],
        nickname=updated_user["nickname"],
        profile_image=updated_user.get("profile_image"),
        created_at=updated_user["created_at"],
        updated_at=updated_user["updated_at"]
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: dict = Depends(auth.get_current_user)):
    user_id = current_user["id"]

    posts = data.load_data("posts.json")
    user_post_ids = [p["id"] for p in posts if p.get("user_id") == user_id]

    comments = data.load_data("comments.json")

    user_comment_counts = {}
    for c in comments:
        if c.get("user_id") == user_id and c.get("post_id") not in user_post_ids:
            post_id = c["post_id"]
            user_comment_counts[post_id] = user_comment_counts.get(post_id, 0) + 1

    for post in posts:
        if post["id"] in user_comment_counts:
            post["comment_count"] = max(post.get("comment_count", 0) - user_comment_counts[post["id"]], 0)

    comments = [c for c in comments
                if c.get("user_id") != user_id and c.get("post_id") not in user_post_ids]
    data.save_data(comments, "comments.json")

    likes = data.load_data("likes.json")

    user_liked_post_ids = [l["post_id"] for l in likes
                          if l.get("user_id") == user_id and l.get("post_id") not in user_post_ids]
    for post in posts:
        if post["id"] in user_liked_post_ids:
            post["like_count"] = max(post.get("like_count", 0) - 1, 0)

    likes = [l for l in likes
             if l.get("user_id") != user_id and l.get("post_id") not in user_post_ids]
    data.save_data(likes, "likes.json")

    posts = [p for p in posts if p.get("user_id") != user_id]
    data.save_data(posts, "posts.json")

    users = data.load_data("users.json")
    users = [u for u in users if u.get("id") != user_id]
    data.save_data(users, "users.json")


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_profile(user_id: int):
    user = data.find_by_id("users.json", user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    return UserPublicResponse(
        id=user["id"],
        nickname=user["nickname"],
        profile_image=user.get("profile_image")
    )
