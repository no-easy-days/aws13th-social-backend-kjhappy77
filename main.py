from fastapi import FastAPI

app = FastAPI()
############### 먼저 Users 엔드포인트 작성 ############
# 내 프로필 조회
@app.get("/users/me")
async def read_users_me():
    pass
# 특정 회원 조회
@app.get("/users/{user_id}")
async def get_user():
    pass
# 내가 쓴 게시글 목록
@app.get("/users/me/posts")
async def get_user_posts():
    pass

# 내가 작성한 댓글
@app.get("/users/me/comments")
async def get_user_comments():
    pass

# 내가 좋아요한 게시글 목록
@app.get("/users/me/likes")
async def get_user_likes():
    pass

# 회원 가입
@app.post("/users")
async def post_users():
    pass

# 프로필 수정
@app.put("/users/me")
async def put_user():
    pass

#회원 탈퇴
@app.delete("/users/me")
async def delete_user():
    pass

######Posts############
#GET 먼저 생성
# 게시글 검색 및 게시글 목록 조회 (query parameters의 keword가 있으면 게시글 검색), 게시글 정렬도 sort
@app.get("/posts")
async def get_posts():
    pass

# 게시글 상세조회
@app.get("/posts/{post_id}")
async def get_post():
    pass

# 댓글 목록 조회
@app.get("/posts/{post_id}/comments")
async def get_post_comments():
    pass

# 좋아요 상태 확인
@app.get("/posts/{post_id}/likes")
async def get_post_likes():
    pass

# 게시글 작성
@app.post("/posts")
async def post_post():
    pass

# 게시글 수정
@app.put("/posts/{post_id}")
async def put_post():
    pass

# 게시글 삭제
@app.delete("/posts/{post_id}")
async def delete_post():
    pass

# 댓글 작성 (특정 게시글에 댓글을 작성합니다.)
@app.post("/posts/{post_id}/comments")
async def post_comment():
    pass

# 댓글 수정
@app.put("/posts/{post_id}/comments/{comment_id}")
async def change_comment():
    pass

# 좋아요 등록
@app.post("/posts/{post_id}/likes")
async def post_like():
    pass

# 좋아요 취소
@app.delete("/posts/{post_id}/likes")
async def delete_like():
    pass

############Comments##################
# 댓글 삭제
@app.delete("/comments/{comment_id}")
async def delete_comment():
    pass

######### auth ############
# 회원 로그인
@app.post("/auth/token")
async def auth_token():
    pass





