from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends, Query

from database import generate_post_id, load_posts, save_posts, load_users, load_likes, load_comments
from utils.auth import get_current_user
from utils.data_validator import validate_and_process_image, sanitize_text

router = APIRouter()

# 1. 게시글 작성 메서드 구현
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

# 2. 게시글 수정 메서드 구현
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
    if target_post is None:
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

# 3. 게시글 삭제 메서드 구현
@router.delete("/posts/{post_id}")
async def delete_posts(
        post_id: str,
        target_user: dict = Depends(get_current_user)
):
    # post_id에 매핑되는 게시글 찾아오기
    posts_json_path = load_posts()
    target_post = None
    for post in posts_json_path:
        if post["post_id"] == post_id:
            target_post = post
            break
    # 게시글 유무 확인
    if target_post is None:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다.")
    # 게시글 ~ 작성자 매핑 여부
    if posts_json_path(target_post)["author"]["user_id"] != target_user["user_id"]:
        raise HTTPException(status_code=403, detail="게시글 작성자가 아닙니다. 삭제할 권한이 없습니다.")
    # 모든 검증 로직 통화, 삭제 수행
    posts_json_path.pop(posts_json_path(target_post))
    save_posts(posts_json_path)
    return {
        "status" : "success",
        "message" : "게시물이 삭제되었습니다. ",
        "data" : {
            "post_id" : target_post["post_id"]
        }
    }

# 4. 게시글 상세 조회 메서드 구현
@router.get("/posts/{post_id}")
async def get_post_post_id(
        post_id: str,
        user: dict | None = Depends(get_current_user)  # 로그인 안 해도 조회 가능, 하면 좋아요 여부 확인
):
    posts_json = load_posts()
    comments_json = load_comments()
    likes_json = load_likes()
    target_post = None
    target_idx = -1
    # 게시글 찾기
    for idx, post in enumerate(posts_json):
        if post["post_id"] == post_id:
            target_post = post
            target_idx = idx
            break
    if target_post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    # 조회수 증가 (본인 글이든 아니든 조회 시 증가 로직)
    # views_count가 없는 데이터 처리를 위해 .get(key, 0) 사용
    current_views = target_post.get("views_count", 0)
    target_post["views_count"] = current_views + 1
    # 변경된 조회수 저장
    posts_json[target_idx] = target_post
    save_posts(posts_json)
    # 부가 정보 계산 (좋아요 수, 댓글 수)
    likes_count = len([l for l in likes_json if l["post_id"] == post_id])
    comments_count = len([c for c in comments_json if c["post_id"] == post_id])
    # 내가 좋아요 눌렀는지 확인
    liked_by_me = False
    if user:
        liked_by_me = any(l["post_id"] == post_id and l["user_id"] == user["user_id"] for l in likes_json)

    # 작성자 정보 매핑 (users.json 참조하지 않고 post에 저장된 author_id로 처리하거나, 필요시 load_users로 조회)
    users = load_users()
    author_info = next((u for u in users if u["user_id"] == target_post["author_id"]),
                       {"nickname": "알수없음", "email_address": ""})
    return {
        "status": "success",
        "message": "요청한 게시글을 성공적으로 불러왔습니다.",
        "data": {
            "post_id": target_post["post_id"],
            "title": target_post["title"],
            "contents": target_post["contents"],
            "contents_image_url": target_post["contents_image_url"],
            "author": {
                "user_id": target_post["author_id"],
                "email_address": author_info.get("email_address", ""),  # 민감정보일 수 있으나 명세서 예시에 있어서 포함
                "nickname": author_info.get("nickname", "")
            },
            "posts_created_time": target_post["posts_created_time"],
            "posts_modified_time": target_post["posts_modified_time"],
            "likes_count": likes_count,
            "comments_count": comments_count,
            "liked_by_me": liked_by_me,
            "views_count": target_post["views_count"]
        }
    }

#5.게시글 목록 조회(검색, 정렬, 페이징) 메서드 구현

@router.get("/posts/")
async def get_posts_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=30),
        keyword: str = Query("", description="검색 키워드"),
        sort_type: str = Query("latest", regex="^(latest|likes|top_viewed)$")
):
    posts = load_posts()
    likes = load_likes()
    comments = load_comments()
    users = load_users()
    # 검색 (Keyword)
    if keyword:
        posts = [p for p in posts if keyword in p["title"] or keyword in p["contents"]]
    # 좋아요, 댓글수 매핑을 위한 리스트 재구성. 정렬을 위해 미리 계산 필요
    enriched_posts = []
    for p in posts:
        l_count = len([l for l in likes if l["post_id"] == p["post_id"]])
        c_count = len([c for c in comments if c["post_id"] == p["post_id"]])
        # 작성자 정보 찾기
        author = next((u for u in users if u["user_id"] == p["author_id"]),
                      {"nickname": "알수없음", "email_address": ""})
        enriched_posts.append({
            **p,
            "likes_count": l_count,
            "comments_count": c_count,
            "author_nickname": author["nickname"],
            "author_email": author["email_address"]
        })
    # 정렬 타입
    if sort_type == "latest":
        enriched_posts.sort(key=lambda x: x["posts_created_time"], reverse=True)
    elif sort_type == "likes":
        enriched_posts.sort(key=lambda x: x["likes_count"], reverse=True)
    elif sort_type == "top_viewed":
        enriched_posts.sort(key=lambda x: x.get("views_count", 0), reverse=True)
    # 페이지네이션
    total_posts = len(enriched_posts)
    total_pages = (total_posts + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_posts = enriched_posts[start_idx:end_idx]
    # 응답 데이터 포맷팅
    result_list = []
    for idx, p in enumerate(paginated_posts):
        result_list.append({
            "sequence": total_posts - (start_idx + idx),  # 역순 번호
            "post_id": p["post_id"],
            "title": p["title"],
            "author": {
                "user_id": p["author_id"],
                "email_address": p["author_email"],
                "nickname": p["author_nickname"]
            },
            "posts_created_time": p["posts_created_time"],
            "posts_modified_time": p["posts_modified_time"],
            "likes_count": p["likes_count"],
            "comments_count": p["comments_count"],
            "views_count": p.get("views_count", 0)
        })
    return {
        "status": "success",
        "message": "게시글 목록을 성공적으로 불러왔습니다." if total_posts > 0 else "게시글 목록을 불러왔으나, 결과가 없습니다.",
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_posts": total_posts,
        "has_next": page < total_pages,
        "keyword": keyword,
        "sort_type": sort_type,
        "data": {
            "list": result_list
        }
    }

# 6. 내가 쓴 게시글 목록 조회 메서드 구현
@router.get("/users/my-page/posts")
async def get_my_posts(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=30),
        keyword: str = Query(""),
        sort_type: str = Query("latest", regex="^(latest|likes|top_viewed)$"),
        user: dict = Depends(get_current_user)
):
    posts = load_posts()
    # 내 글만 필터링
    my_posts = [p for p in posts if p["author_id"] == user["user_id"]]
    # 이하 로직은 게시글 목록 조회와 동일하게 구현
    if keyword:
        my_posts = [p for p in my_posts if keyword in p["title"] or keyword in p["contents"]]
    likes = load_likes()
    comments = load_comments()
    enriched_posts = []
    for p in my_posts:
        l_count = len([l for l in likes if l["post_id"] == p["post_id"]])
        c_count = len([c for c in comments if c["post_id"] == p["post_id"]])
        enriched_posts.append({
            **p,
            "likes_count": l_count,
            "comments_count": c_count,
        })

    if sort_type == "latest":
        enriched_posts.sort(key=lambda x: x["posts_created_time"], reverse=True)
    elif sort_type == "likes":
        enriched_posts.sort(key=lambda x: x["likes_count"], reverse=True)
    elif sort_type == "top_viewed":
        enriched_posts.sort(key=lambda x: x.get("views_count", 0), reverse=True)

    total_posts = len(enriched_posts)
    total_pages = (total_posts + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    paginated_posts = enriched_posts[start_idx:start_idx + page_size]

    result_list = []
    for idx, p in enumerate(paginated_posts):
        result_list.append({
            "sequence": total_posts - (start_idx + idx),
            "post_id": p["post_id"],
            "title": p["title"],
            "author": {
                "user_id": user["user_id"],
                "email_address": user["email_address"],
                "nickname": user["nickname"]
            },
            "posts_created_time": p["posts_created_time"],
            "posts_modified_time": p["posts_modified_time"],
            "likes_count": p["likes_count"],
            "comments_count": p["comments_count"]
        })
    return {
        "status": "success",
        "message": "내가 쓴 게시글 목록을 성공적으로 불러왔습니다.",
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_posts": total_posts,
        "has_next": page < total_pages,
        "keyword": keyword,
        "sort_type": sort_type,
        "data": {
            "list": result_list
        }
    }

